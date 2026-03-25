"""Console output for the WebVH E2E harness (Rich: panels + markup in log lines)."""

from __future__ import annotations

import logging
import textwrap

from rich.align import Align
from rich.console import Console
from rich.logging import RichHandler
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

LOG = logging.getLogger("webvh-e2e")

_DETAIL_LABEL_WIDTH = 16
_console_err = Console(stderr=True, highlight=False, soft_wrap=True)


def _detail_label_column(label: str) -> str:
    w = _DETAIL_LABEL_WIDTH
    return f"     {label:<{w}}"


def bold(s: str) -> str:
    return f"[bold]{escape(s)}[/bold]"


def dim(s: str) -> str:
    return f"[dim]{escape(s)}[/dim]"


def headline_request(
    method: str,
    path: str,
    *,
    role: str | None = None,
    subtitle: str | None = None,
) -> str:
    parts: list[str] = [f"{bold(method)} {dim(path)}"]
    if role:
        parts.append(dim(f"({role})"))
    if subtitle:
        parts.append(dim(subtitle))
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]}  ·  " + "  ·  ".join(parts[1:])


def party_headline(party: str, sentence: str, *, bold_message: bool = True) -> str:
    body = bold(sentence) if bold_message else escape(sentence)
    return f"{dim(f'({party})')} {body}"


def detail_field_line(label: str, value: str, *, emphasis: bool = False) -> str:
    col = _detail_label_column(label)
    shown = bold(value) if emphasis else dim(value)
    return f"{col} {shown}"


def wrap_dim_block(label: str, value: str, *, chunk_width: int = 68) -> str:
    label_col = _detail_label_column(label)
    sep = " "
    chunks = textwrap.wrap(
        value,
        width=chunk_width,
        break_long_words=True,
        break_on_hyphens=False,
    ) or [value]
    pad = " " * (len(label_col) + len(sep))
    lines = [f"{label_col}{sep}{dim(chunks[0])}"]
    lines.extend(f"{pad}{dim(c)}" for c in chunks[1:])
    return "\n".join(lines)


def phase_banner(name: str) -> None:
    display = name[:42] + ("…" if len(name) > 42 else "")
    _console_err.print()
    _console_err.print(
        Panel(
            Align.center(Text(display, style="bold")),
            width=46,
            border_style="bright_magenta",
            padding=(0, 1),
        )
    )
    _console_err.print()


def setup_logging(*, verbose: bool, force: bool = True) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handler = RichHandler(
        console=_console_err,
        show_time=False,
        show_level=False,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
        highlighter=None,
    )
    logging.basicConfig(level=level, format="%(message)s", handlers=[handler], force=force)
    LOG.setLevel(level)
    LOG.propagate = True
    for name in ("urllib3", "urllib3.connectionpool", "charset_normalizer", "requests"):
        logging.getLogger(name).setLevel(logging.WARNING)


def run_summary_standout(
    *,
    ok: bool,
    base_url: str,
    witness: bool,
    n_done: int,
    n_plan: int,
    elapsed_s: float,
    failed_phase: str | None = None,
    completed_phases: tuple[str, ...] = (),
) -> None:
    status = bold("PASSED") if ok else bold("FAILED")
    lines = [
        f"  Result · {status} · {n_done}/{n_plan} phase(s) · {elapsed_s:.1f}s",
        f"  Target · {dim(base_url)}",
        f"  Witness · {bold('on') if witness else dim('off')}",
    ]
    if not ok:
        if failed_phase:
            lines.append(f"  Stopped · {bold(failed_phase)}")
        if completed_phases:
            lines.append(f"  Completed · {dim(', '.join(completed_phases))}")
    content = "\n".join(lines)
    _console_err.print()
    _console_err.print(
        Panel.fit(
            content,
            title="[bold]Run summary[/bold]",
            border_style="bright_magenta",
            padding=(0, 1),
        )
    )
    _console_err.print()
