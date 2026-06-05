"""dexter.console — Terminal styling via Rich.

Provee un console global con estilos consistentes para toda la app:
- Paneles con bordes para resultados estructurados
- Colores semánticos (éxito=verde, error=rojo, tool=cyan)
- Markdown rendering para respuestas del LLM
"""
from __future__ import annotations

from rich.console import Console as _RichConsole
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich import box

_console = _RichConsole()
_theme = "dark"


def banner(text: str, version: str = "4.1.0-dev", company: str = ""):
    """Muestra el banner principal de Dexter."""
    subtitle = f"v{version}"
    if company:
        subtitle += f" · {company}"
    panel = Panel(
        f"[bold cyan]{text}[/bold cyan]",
        subtitle=f"[dim]{subtitle}[/dim]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    _console.print(panel)


def header(title: str):
    """Panel con título."""
    _console.print(Panel(title, border_style="blue", box=box.ROUNDED))


def success(msg: str):
    """Mensaje de éxito."""
    _console.print(f"[green]✓[/green] {msg}")


def error(msg: str):
    """Mensaje de error."""
    _console.print(f"[red]✗[/red] {msg}")


def warning(msg: str):
    _console.print(f"[yellow]⚠[/yellow] {msg}")


def info(msg: str):
    _console.print(f"[blue]ℹ[/blue] {msg}")


def tool_start(name: str, args: str = ""):
    """Indica que se está ejecutando un tool."""
    arg_text = f" [dim]· {args}[/dim]" if args else ""
    _console.print(f"  [cyan]⚡ {name}[/cyan]{arg_text}")


def tool_result(summary: str, success: bool = True):
    """Mini-resumen del resultado de un tool."""
    icon = "[green]  ✓[/green]" if success else "[red]  ✗[/red]"
    _console.print(f"{icon} {summary}")


def result_panel(title: str, rows: list[tuple[str, str]], style: str = "green"):
    """Panel con datos clave (ej: resultado de un estimate)."""
    if not rows:
        return
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    table.add_column(style="dim", width=12)
    table.add_column(style="bold")
    for key, value in rows:
        table.add_row(key, str(value))
    _console.print(Panel(table, title=f"[bold {style}]{title}[/bold {style}]",
                        border_style=style, box=box.ROUNDED))


def user_prompt():
    """Retorna el prompt estilizado para input."""
    return _console.input("[bold cyan]❯[/bold cyan] [bold]Tú:[/bold] ")


def assistant_label():
    """Prefijo para respuestas del asistente."""
    _console.print("\n  [bold green]Dexter[/bold green] · ", end="")


def assistant_response(text: str):
    """Renderiza la respuesta del asistente (Markdown)."""
    _console.print(Markdown(text))
    _console.print()


def divider():
    _console.print("[dim]" + "─" * 60 + "[/dim]")


def status_msg(msg: str):
    """Mensaje de estado general."""
    _console.print(f"  [dim]{msg}[/dim]")


# Export para uso directo
console = _console
