# -*- coding: utf-8 -*-
"""
Disambiguator: preguntas interactivas al usuario.

Componente clave para que el sistema funcione con datos incompletos o
ambiguos. Cuando el motor no puede decidir (cliente no existe, cuenta no
encontrada, fecha ambigua), el disambiguator pregunta al usuario.

API testeable: input_func y output_func son inyectables.
"""
from typing import Any, Callable, Dict, List, Optional, Tuple


class Disambiguator:
    """Realiza preguntas al usuario cuando hay ambigüedad."""

    def __init__(
        self,
        input_func: Optional[Callable[[str], str]] = None,
        output_func: Optional[Callable[[str], None]] = None
    ):
        self.input = input_func or input
        self.output = output_func or print

    def _header(self, title: str) -> None:
        self.output("")
        self.output("=" * 70)
        self.output(f"  {title}")
        self.output("=" * 70)

    def ask_choice(
        self,
        question: str,
        options: List[str],
        allow_new: bool = True
    ) -> Optional[str]:
        """
        Presenta opciones y pide selección.

        Returns:
            La opción seleccionada, o None si el usuario cancela.
        """
        self._header(question)
        for i, opt in enumerate(options, 1):
            self.output(f"  [{i}] {opt}")
        if allow_new:
            self.output(f"  [N] Crear nuevo")
        self.output(f"  [S] Saltar este item")
        self.output("")

        while True:
            choice = self.input("Tu elección: ").strip().lower()
            if choice in ("s", "skip", "salir"):
                return None
            if allow_new and choice in ("n", "new", "nuevo"):
                return "__NEW__"
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
            except ValueError:
                pass
            self.output(f"  ⚠️  Opción inválida. Intenta de nuevo.")

    def ask_new_customer(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Pide datos para crear un cliente nuevo.

        Returns:
            Dict con email, terms, etc. o None si el usuario cancela.
        """
        self._header(f"Cliente no encontrado: '{name}'")
        self.output("  Necesito los siguientes datos para crearlo en QBO:")
        self.output("")

        confirm = self.input("  ¿Crear nuevo cliente? (S/n): ").strip().lower()
        if confirm in ("n", "no"):
            return None

        email = self.input("  Email: ").strip()
        if not email:
            self.output("  ⚠️  Email es obligatorio")
            return None

        terms = self.input("  Términos de pago [Net 30/Net 15/Due on receipt]: ").strip()
        if not terms:
            terms = "Net 30"

        phone = self.input("  Teléfono (opcional): ").strip()
        company = self.input("  Nombre de la compañía (opcional): ").strip()

        result: Dict[str, Any] = {
            "name": name,
            "email": email,
            "terms": terms,
        }
        if phone:
            result["phone"] = phone
        if company:
            result["company"] = company
        return result

    def ask_account(
        self,
        description: str,
        candidates: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Pide seleccionar una cuenta contable.

        Args:
            description: descripción de la transacción
            candidates: lista de dicts con 'id' y 'name'

        Returns:
            ID de la cuenta seleccionada, o None
        """
        self._header(f"Selecciona cuenta para: '{description}'")
        for i, c in enumerate(candidates, 1):
            self.output(f"  [{i}] {c.get('name', 'Sin nombre')} (ID: {c.get('id', '?')})")
        self.output(f"  [N] No clasificar (dejar pendiente)")
        self.output("")

        while True:
            choice = self.input("Tu elección: ").strip().lower()
            if choice in ("n", "no", "skip"):
                return None
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(candidates):
                    return candidates[idx].get("id")
            except ValueError:
                pass
            self.output("  ⚠️  Opción inválida")

    def confirm_batch(self, summary: Dict[str, Any]) -> bool:
        """
        Muestra resumen del batch y pide confirmación final.

        Returns:
            True si el usuario confirma, False si cancela.
        """
        self._header("DRY RUN — Resumen del batch")
        self.output(f"  Total items:           {summary.get('total', 0)}")
        self.output(f"  Listos para ejecutar:  {summary.get('ready_to_execute', 0)}")
        self.output(f"  Omitidos / con error:  {summary.get('skipped', 0)}")
        self.output("")
        self.output("  Detalle:")
        for item in summary.get("items", []):
            idx = item.get("index", "?")
            state = item.get("state", "?")
            inp = item.get("input", {})
            self.output(f"    [{idx}] ({state}) {inp}")
        self.output("")

        while True:
            choice = self.input("¿Ejecutar? (S/n): ").strip().lower()
            if choice in ("s", "si", "yes", "y", ""):
                return True
            if choice in ("n", "no"):
                return False
            self.output("  ⚠️  Responde S o n")

    def show_error(self, title: str, error: str) -> None:
        """Muestra un error al usuario de forma legible."""
        self._header(f"❌ {title}")
        self.output(f"  {error}")
        self.output("")
