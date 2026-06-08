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
from rich.json import JSON
from rich.status import Status
from contextlib import contextmanager
import time as _time

_console = _RichConsole()
_theme = "dark"


def banner(text: str, version: str = "4.1.0-dev", company: str = ""):
    """Muestra el banner principal de Dexter con ASCII art."""
    subtitle = f"v{version}"
    if company:
        subtitle += f" · {company}"

    ascii_art = """
[bold cyan]   ██████╗ ███████╗██╗  ██╗████████╗███████╗██████╗[/bold cyan]
[bold cyan]   ██╔══██╗██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝██╔══██╗[/bold cyan]
[bold cyan]   ██║  ██║█████╗   ╚███╔╝    ██║   █████╗  ██████╔╝[/bold cyan]
[bold cyan]   ██║  ██║██╔══╝   ██╔██╗    ██║   ██╔══╝  ██╔══██╗[/bold cyan]
[bold cyan]   ██████╔╝███████╗██╔╝ ██╗   ██║   ███████╗██║  ██║[/bold cyan]
[bold cyan]   ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝[/bold cyan]"""

    _console.print(ascii_art)
    _console.print()
    panel = Panel(
        f"[bold white]{text}[/bold white]",
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


def thinking_spinner(msg: str = "Pensando"):
    """Context manager con spinner mientras el LLM procesa."""
    return _console.status(f"[bold cyan]{msg}...[/bold cyan]", spinner="dots")


def tool_result_pretty(result_str: str, success: bool = True):
    """Muestra el resultado de un tool en JSON coloreado (primeros 200 chars)."""
    icon = "[green]  ✓[/green]" if success else "[red]  ✗[/red]"
    _console.print(f"{icon} ", end="")
    try:
        import json
        data = json.loads(result_str)
        # Mostrar keys principales en vez del JSON completo
        preview = {k: v for k, v in data.items()
                   if k not in ("dry_run_note",) and not isinstance(v, (list, dict))}
        if not preview:
            preview = {"resultado": str(data)[:80]}
        _console.print(JSON.from_data(preview))
    except Exception:
        _console.print(f"[dim]{result_str[:100]}[/dim]")


def elapsed_since(start: float) -> str:
    """Formato legible de tiempo transcurrido."""
    elapsed = _time.time() - start
    if elapsed < 1:
        return f"{elapsed*1000:.0f}ms"
    return f"{elapsed:.1f}s"


# Export para uso directo
console = _console
