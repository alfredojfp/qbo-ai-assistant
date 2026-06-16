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
    """Retorna el prompt estilizado para input con autocomplete de tools (/)."""
    try:
        from prompt_toolkit import prompt as pt_prompt
        from prompt_toolkit.styles import Style
        from prompt_toolkit.completion import Completer, Completion

        class _DexterCompleter(Completer):
            def get_completions(self, document, event):
                text = document.text_before_cursor
                topic = _build_topic(text)
                if topic is None:
                    return
                # prefix_len: cuántos caracteres borrar (desde el / inclusive)
                prefix_len = len(text) - text.rfind("/")
                partial = topic.lower()
                tools = _get_slash_tools()

                if topic:
                    # substring match primero
                    for cmd, desc in tools.items():
                        if partial in cmd or partial in cmd.replace("_", " "):
                            yield Completion(
                                cmd, start_position=-prefix_len,
                                display=f"/{cmd}", display_meta=desc[:60],
                            )
                    # fuzzy fallback si hay al menos 2 chars
                    if len(topic) >= 2:
                        from difflib import SequenceMatcher
                        candidates = []
                        for cmd, desc in tools.items():
                            score = SequenceMatcher(None, partial, cmd).ratio()
                            if score >= 0.35:
                                candidates.append((score, cmd, desc))
                        candidates.sort(key=lambda x: x[0], reverse=True)
                        for score, cmd, desc in candidates[:6]:
                            yield Completion(
                                cmd, start_position=-prefix_len,
                                display=f"/{cmd}",
                                display_meta=f"{desc[:55]} ({int(score*100)}%)",
                            )
                else:
                    # solo "/" → mostrar todos los tools, orden alfabético
                    for cmd, desc in sorted(tools.items()):
                        yield Completion(
                            cmd, start_position=-prefix_len,
                            display=f"/{cmd}", display_meta=desc[:60],
                        )

        style = Style.from_dict({
            "prompt": "bold cyan",
            "": "bold white",
            "completion-menu": "bg:#1e1e2e #cdd6f4",
            "completion-menu.completion": "bg:#313244 #cdd6f4",
            "completion-menu.completion.current": "bg:#45475a #ffffff",
            "completion-menu.meta": "bg:#1e1e2e #a6adc8",
            "completion-menu.meta.current": "bg:#45475a #ffffff",
            "scrollbar.background": "bg:#1e1e2e",
            "scrollbar.button": "bg:#585b70",
        })

        return pt_prompt(
            [("class:prompt", "\u276f T\u00fa: ")],
            completer=_DexterCompleter(),
            style=style,
            complete_while_typing=True,
        )
    except ImportError:
        return _console.input("[bold cyan]\u276f[/bold cyan] [bold]T\u00fa:[/bold] ")


# ── lazy tool list (evita circular import) ──

_slash_tools_cache = None


def _get_slash_tools():
    global _slash_tools_cache
    if _slash_tools_cache is not None:
        return _slash_tools_cache
    tools = {}
    try:
        from dexter.skills import ALL_SCHEMAS, ALL_FUNCTIONS
        for schema in ALL_SCHEMAS:
            fn = schema.get("function", schema)
            name = fn.get("name", "")
            if name:
                desc = fn.get("description", "")
                tools[name] = desc
    except (ImportError, AttributeError):
        pass
    _slash_tools_cache = tools or {"buscar_cliente": "Busca clientes por nombre (fuzzy)"}
    return _slash_tools_cache


def _build_topic(text):
    last = text.rfind("/")
    if last < 0:
        return None
    return text[last + 1:]


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
