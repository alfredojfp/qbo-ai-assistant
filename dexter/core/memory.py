"""dexter.core.memory — Memoria persistente entre sesiones.

Inspirado en Hermes Agent: MEMORY.md (notas del agente) y USER.md
(perfil del usuario). Las entradas se persisten a disco como texto
separado por § y se inyectan en el system prompt al inicio de cada
sesión. El agente puede gestionar su memoria via tools.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict


class PersistentMemory:
    """Memoria persistente del agente (Hermes-style).

    Dos archivos:
      - MEMORY.md: datos del entorno, clientes frecuentes, lecciones
      - USER.md:  perfil del usuario, preferencias, estilo

    Las entradas se almacenan como texto plano separado por §.
    """

    MEMORY_CHAR_LIMIT = 2200    # ~800 tokens
    USER_CHAR_LIMIT = 1375      # ~500 tokens

    def __init__(self, memory_path: str = None, user_path: str = None):
        base = Path(os.path.expanduser("~/.config/dexter"))
        base.mkdir(parents=True, exist_ok=True)
        self._memory_path = Path(memory_path) if memory_path else base / "MEMORY.md"
        self._user_path = Path(user_path) if user_path else base / "USER.md"

    # --- Lectura ---

    def _read(self, path: Path) -> List[str]:
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return []
        return [e.strip() for e in text.split("§") if e.strip()]

    def get_memory_entries(self) -> List[str]:
        return self._read(self._memory_path)

    def get_user_entries(self) -> List[str]:
        return self._read(self._user_path)

    def _write(self, path: Path, entries: List[str]):
        path.parent.mkdir(parents=True, exist_ok=True)
        clean = [e.strip() for e in entries if e.strip()]
        text = " § ".join(clean)
        path.write_text(text, encoding="utf-8")

    # --- Escritura ---

    def _get_path(self, target: str) -> Path:
        if target == "memory":
            return self._memory_path
        elif target == "user":
            return self._user_path
        raise ValueError(f"Target inválido: {target} (debe ser 'memory' o 'user')")

    def _get_limit(self, target: str) -> int:
        return self.MEMORY_CHAR_LIMIT if target == "memory" else self.USER_CHAR_LIMIT

    def add(self, target: str, content: str) -> Dict:
        """Agrega entrada. Si duplicado o excede límite, retorna error."""
        path = self._get_path(target)
        limit = self._get_limit(target)
        entries = self._read(path)
        content = content.strip()

        # Duplicados
        if content in entries:
            return {"success": True, "note": "Entrada ya existente, no duplicada"}

        # Límite
        current_chars = sum(len(e) for e in entries)
        separator_overhead = 3 * (len(entries))  # " § "
        new_chars = current_chars + separator_overhead + len(content)
        if new_chars > limit and entries:
            return {
                "success": False,
                "error": f"Memoria {target} llena ({current_chars}/{limit} chars). "
                         f"Consolida o elimina entradas antes de agregar.",
                "current_entries": entries,
                "usage": f"{current_chars}/{limit}",
            }

        entries.append(content)
        self._write(path, entries)
        return {"success": True}

    def remove(self, target: str, substring: str) -> Dict:
        """Elimina entrada que contenga el substring (único match)."""
        path = self._get_path(target)
        entries = self._read(path)
        matches = [e for e in entries if substring in e]
        if not matches:
            return {"success": False, "error": f"No se encontró '{substring}'"}
        if len(matches) > 1:
            return {"success": False, "error": f"'{substring}' coincide con {len(matches)} entradas"}
        entries.remove(matches[0])
        self._write(path, entries)
        return {"success": True}

    # --- Formato para system prompt ---

    @staticmethod
    def _normalize_key(text: str) -> str:
        """Normaliza una clave para fuzzy matching.

        Convierte a snake_case: quita espacios, tildes, guiones
        y caracteres no alfanuméricos. "banco default" → "banco_default".
        """
        import re
        text = text.lower().strip()
        text = re.sub(r'[áàäâ]', 'a', text)
        text = re.sub(r'[éèëê]', 'e', text)
        text = re.sub(r'[íìïî]', 'i', text)
        text = re.sub(r'[óòöô]', 'o', text)
        text = re.sub(r'[úùüû]', 'u', text)
        text = re.sub(r'[^a-z0-9]', '_', text)
        text = re.sub(r'_+', '_', text)
        return text.strip('_')

    def parse_defaults(self, known_keys: List[str] = None) -> Dict[str, str]:
        """Extrae entradas de memoria con formato clave:valor.

        HIGH-2b: fuzzy key matching con aliases. Normaliza la clave y la compara
        contra `known_keys`. También soporta aliases: 'deposito_default' también
        matchea 'cuenta_linea_default', 'linea_default', 'cuenta_deposito_default'.

        Args:
            known_keys: Lista de claves conocidas a buscar (ej: ['banco_default']).
                        Si es None, retorna todas las entradas con ':'.
        """
        # Alias map: canonical_key → additional patterns to match
        _ALIASES = {
            "deposito_default": ["cuenta_linea", "linea_default", "cuenta_deposito"],
            "banco_default": ["cuenta_banco", "banco_cuenta"],
        }

        defaults: Dict[str, str] = {}
        for entry in self.get_memory_entries():
            if ":" not in entry:
                continue
            key, _, value = entry.partition(":")
            value = value.strip()
            norm_key = self._normalize_key(key)
            if not norm_key or not value:
                continue

            if known_keys is None:
                defaults[norm_key] = value
            else:
                for target in known_keys:
                    target_norm = self._normalize_key(target)
                    if target_norm in norm_key:
                        defaults[target] = value
                        break
                    # Check aliases
                    for alias in _ALIASES.get(target, []):
                        if self._normalize_key(alias) in norm_key:
                            defaults[target] = value
                            break
                    else:
                        continue
                    break
        return defaults

    def parse_rules(self) -> Dict[str, str]:
        """Extrae reglas de comportamiento desde la memoria.

        Formato en MEMORY.md:
          regla: nombre_de_regla = valor
          regla: nombre_de_regla: valor

        Prefiere '=' como separador; si no hay, usa ':'.
        """
        rules: Dict[str, str] = {}
        for entry in self.get_memory_entries():
            norm = self._normalize_key(entry)
            if not norm.startswith("regla_"):
                continue
            body = entry.strip()
            # Find separator: prefer '=', fallback to ':'
            sep = "=" if "=" in body else ":"
            # Split on the separator that comes AFTER the "regla:" prefix
            # Find the LAST occurrence of the separator to handle values with colons
            sep_idx = body.rfind(sep)
            if sep_idx < 0:
                continue
            # Extract key: everything between "regla:" and the separator
            key_raw = body[:sep_idx].strip()
            if ":" in key_raw:
                key_raw = key_raw.split(":", 1)[-1].strip()
            elif key_raw.lower().startswith("regla"):
                key_raw = key_raw[5:].strip().lstrip(":").strip()
            value = body[sep_idx + 1:].strip()
            key = self._normalize_key(key_raw)
            if key and value:
                rules[key] = value
        return rules

    def usage_percent(self, target: str) -> float:
        path = self._get_path(target)
        limit = self._get_limit(target)
        entries = self._read(path)
        chars = sum(len(e) for e in entries)
        overhead = 3 * max(0, len(entries) - 1)
        return round((chars + overhead) / limit * 100, 1)

    def format_for_prompt(self) -> str:
        """Retorna bloque markdown para inyectar en system prompt."""
        parts = []

        mem_entries = self.get_memory_entries()
        if mem_entries:
            mem_chars = sum(len(e) for e in mem_entries)
            mem_overhead = 3 * max(0, len(mem_entries) - 1)
            mem_usage = mem_chars + mem_overhead
            mem_pct = self.usage_percent("memory")
            header = (
                f"═══ MEMORY (tus notas personales) "
                f"[{mem_pct:.0f}% — {mem_usage}/{self.MEMORY_CHAR_LIMIT} chars] ═══"
            )
            body = " § ".join(mem_entries)
            parts.append(f"{header}\n{body}")

        user_entries = self.get_user_entries()
        if user_entries:
            user_chars = sum(len(e) for e in user_entries)
            user_overhead = 3 * max(0, len(user_entries) - 1)
            user_usage = user_chars + user_overhead
            user_pct = self.usage_percent("user")
            header = (
                f"═══ USER PROFILE (perfil de Alfredo) "
                f"[{user_pct:.0f}% — {user_usage}/{self.USER_CHAR_LIMIT} chars] ═══"
            )
            body = " § ".join(user_entries)
            parts.append(f"{header}\n{body}")

        return "\n".join(parts) if parts else ""

    def get_status(self) -> Dict:
        return {
            "memory_entries": len(self.get_memory_entries()),
            "memory_usage_pct": self.usage_percent("memory"),
            "user_entries": len(self.get_user_entries()),
            "user_usage_pct": self.usage_percent("user"),
        }
