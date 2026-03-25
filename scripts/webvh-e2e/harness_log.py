"""Small TTY-aware helpers for the WebVH E2E harness (stdlib logging only)."""

from __future__ import annotations

import logging
import os
import sys
import textwrap

LOG = logging.getLogger("webvh-e2e")

_DETAIL_LABEL_WIDTH = 16
_RST = "\033[0m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_RED = "\033[31m"
_CYAN = "\033[36m"


def _tty() -> bool:
    return sys.stderr.isatty() and not (os.environ.get("NO_COLOR") or "").strip()


def bold(s: str) -> str:
    return f"{_BOLD}{s}{_RST}" if _tty() else s


def dim(s: str) -> str:
    return f"{_DIM}{s}{_RST}" if _tty() else s


def _detail_label_column(label: str) -> str:
    return f"  {label:<{_DETAIL_LABEL_WIDTH}}"


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
    return f"{parts[0]}  {dim('·')}  " + f"  {dim('·')}  ".join(parts[1:])


def party_headline(party: str, sentence: str, *, bold_message: bool = True) -> str:
    body = bold(sentence) if bold_message else sentence
    return f"{dim(f'({party})')} {body}"


def detail_field_line(label: str, value: str, *, emphasis: bool = False) -> str:
    col = _detail_label_column(label)
    shown = bold(value) if emphasis else dim(value)
    return f"{col} {shown}"


def wrap_dim_block(label: str, value: str, *, chunk_width: int = 72) -> str:
    col = _detail_label_column(label)
    sep = " "
    chunks = textwrap.wrap(
        value,
        width=chunk_width,
        break_long_words=True,
        break_on_hyphens=False,
    ) or [value]
    pad = " " * (len(col) + len(sep))
    lines = [f"{col}{sep}{dim(chunks[0])}"]
    lines.extend(f"{pad}{dim(c)}" for c in chunks[1:])
    return "\n".join(lines)


class _Fmt(logging.Formatter):
    """One-character level gutter; continuation lines stay aligned."""

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        if "\n" in msg:
            first, *rest = msg.split("\n")
            pad = "     "
            rest = [ln if (not ln or ln.startswith("  ")) else pad + ln for ln in rest]
            msg = "\n".join([first, *rest])
        if not _tty():
            return msg
        if record.levelno >= logging.ERROR:
            return f"{_RED}×{_RST} {msg}"
        if record.levelno >= logging.WARNING:
            return f"{_RED}!{_RST} {msg}"
        if record.levelno == logging.DEBUG:
            return f"{_DIM}·{_RST} {msg}"
        return f"{_CYAN}·{_RST} {msg}"


def phase_banner(name: str) -> None:
    line = f"── {name} ──"
    sys.stderr.write("\n" + (dim(line) if _tty() else line) + "\n")


def setup_logging(*, verbose: bool, force: bool = True) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(_Fmt())
    logging.basicConfig(level=level, handlers=[h], force=force)
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
    w = "on" if witness else "off"
    status = bold("ok") if ok else bold("failed")
    parts = [f"{status}  {n_done}/{n_plan} phases  {elapsed_s:.1f}s  {base_url}  witness={w}"]
    if not ok:
        if failed_phase:
            parts.append(f"stopped: {failed_phase}")
        if completed_phases:
            parts.append("done: " + ", ".join(completed_phases))
    block = "\n".join(parts)
    bar = "── summary ──"
    sys.stderr.write("\n" + (dim(bar) if _tty() else bar) + "\n")
    sys.stderr.write(block + "\n\n")
