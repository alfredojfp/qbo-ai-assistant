"""dexter.skills — Sistema de skills auto-descubribles.

Cada skill es un directorio con:
  - __init__.py  → exporta SCHEMA, FUNCTIONS, KEYWORDS
  - SKILL.md     → documentación de la skill (opcional)

El registry auto-descubre skills del directorio y agrega sus
schemas/funciones al sistema de tools global.

Para backward compat, dexter.tools sigue funcionando como fachada.
"""
from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ── Auto-discovery ─────────────────────────────────────────────────────
_SKILLS_DIR = Path(__file__).resolve().parent

ALL_SKILLS: Dict[str, Any] = {}
ALL_SCHEMAS: List[Dict[str, Any]] = []
ALL_FUNCTIONS: Dict[str, Callable[..., Any]] = {}
KEYWORDS_BY_SKILL: Dict[str, List[str]] = {}


def _discover_skills():
    """Escanea el directorio y descubre skills automáticamente."""
    global ALL_SKILLS, ALL_SCHEMAS, ALL_FUNCTIONS, KEYWORDS_BY_SKILL
    
    if ALL_SKILLS:
        return  # ya descubiertas
    
    for entry in sorted(_SKILLS_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith("_") or entry.name.startswith("."):
            continue
        
        init_file = entry / "__init__.py"
        if not init_file.exists():
            continue
        
        skill_name = entry.name
        try:
            module = importlib.import_module(f"dexter.skills.{skill_name}")
            if hasattr(module, "SCHEMA") and hasattr(module, "FUNCTIONS"):
                ALL_SKILLS[skill_name] = module
                
                # Extraer nombre de cada schema para evitar duplicados
                for schema in module.SCHEMA:
                    name = _extract_name(schema)
                    if name and name not in ALL_FUNCTIONS:
                        ALL_SCHEMAS.append(schema)
                        ALL_FUNCTIONS[name] = module.FUNCTIONS[name]
                
                # Keywords
                if hasattr(module, "KEYWORDS"):
                    KEYWORDS_BY_SKILL[skill_name] = list(module.KEYWORDS)
        except Exception as e:
            print(f"⚠️  Skill '{skill_name}' no se pudo cargar: {e}")


def _extract_name(schema: Dict[str, Any]) -> str:
    """Extrae el nombre de un schema en formato OpenAI o simplificado."""
    if "function" in schema and isinstance(schema.get("function"), dict):
        return schema["function"].get("name", "")
    return schema.get("name", "")


def get_skill_info(skill_name: str) -> Optional[Dict]:
    """Retorna metadata de una skill (nombre, descripción, tool count)."""
    _discover_skills()
    if skill_name not in ALL_SKILLS:
        return None
    module = ALL_SKILLS[skill_name]
    return {
        "name": skill_name,
        "tools": len(module.SCHEMA) if hasattr(module, "SCHEMA") else 0,
        "has_skill_md": (Path(_SKILLS_DIR) / skill_name / "SKILL.md").exists(),
    }


def list_skills() -> List[Dict]:
    """Lista todas las skills disponibles con metadata."""
    _discover_skills()
    return [get_skill_info(name) for name in sorted(ALL_SKILLS.keys())]


# Auto-descubrir al importar
_discover_skills()
