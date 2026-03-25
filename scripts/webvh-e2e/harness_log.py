"""TTY-aware logging for the WebVH E2E harness (glyphs, colors, phase banners)."""

from __future__ import annotations

import logging
import os
import sys
import textwrap

LOG = logging.getLogger("webvh-e2e")

# Widest labels in run.py: ``verifier_pres_ex`` (16). Keeps columns aligned.
_DETAIL_LABEL_WIDTH = 16


def _detail_label_column(label: str) -> str:
    """Fixed-width label column (5-space gutter + padded label)."""
    w = _DETAIL_LABEL_WIDTH
    return f"     {label:<{w}}"


def headline_request(
    method: str,
    path: str,
    *,
    role: str | None = None,
    subtitle: str | None = None,
) -> str:
    """
    Standard first line for an HTTP action, e.g.::

        POST /anoncreds/schema  ·  (issuer)

    ``role`` is wrapped in parentheses (issuer / holder). ``subtitle`` is dim free text
    (e.g. ``AnonCreds``, ``verifier / issuer tenant``).
    """
    parts: list[str] = [f"{bold(method)} {dim(path)}"]
    if role:
        parts.append(dim(f"({role})"))
    if subtitle:
        parts.append(dim(subtitle))
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]}  ·  " + "  ·  ".join(parts[1:])


def party_headline(party: str, sentence: str, *, bold_message: bool = True) -> str:
    """Tenant tag (dim) + message (bold by default; use ``bold_message=False`` for errors)."""
    body = bold(sentence) if bold_message else sentence
    return f"{dim(f'({party})')} {body}"


def detail_field_line(label: str, value: str, *, emphasis: bool = False) -> str:
    """One detail row: fixed label column, space, then value (matches ``wrap_dim_block``)."""
    col = _detail_label_column(label)
    shown = bold(value) if emphasis else dim(value)
    return f"{col} {shown}"


def ansi_enabled() -> bool:
    return sys.stderr.isatty() and not (os.environ.get("NO_COLOR") or "").strip()


def bold(s: str) -> str:
    return f"\033[1m{s}\033[0m" if ansi_enabled() else s


def dim(s: str) -> str:
    return f"\033[2m{s}\033[0m" if ansi_enabled() else s


def magenta(s: str) -> str:
    return f"\033[38;5;177m{s}\033[0m" if ansi_enabled() else s


def wrap_dim_block(label: str, value: str, *, chunk_width: int = 68) -> str:
    """Label column + dim-wrapped value (multi-line) for long DIDs / IDs."""
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


class HarnessFormatter(logging.Formatter):
    """Compact glyph column + message (NO_COLOR disables styling)."""

    _MULTI_INDENT_PLAIN = " " * 7
    _MULTI_INDENT_TTY = " " * 4

    @classmethod
    def _indent_continuations(cls, msg: str, *, tty: bool) -> str:
        """Indent continuation lines that are not already guttered (detail helpers use 5 spaces)."""
        if "\n" not in msg:
            return msg
        first, *rest = msg.split("\n")
        pad = cls._MULTI_INDENT_TTY if tty else cls._MULTI_INDENT_PLAIN
        out: list[str] = [first]
        for line in rest:
            if not line:
                out.append(line)
            elif line.startswith("     "):
                out.append(line)
            else:
                out.append(pad + line)
        return "\n".join(out)

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        if not ansi_enabled():
            msg = self._indent_continuations(msg, tty=False)
            return f"{record.levelname:5}  {msg}"
        rst, d, cyn, ylw, red = (
            "\033[0m",
            "\033[2m",
            "\033[36m",
            "\033[33m",
            "\033[31m",
        )
        if record.levelno == logging.DEBUG:
            msg = self._indent_continuations(msg, tty=True)
            return f"{d}    · {msg}{rst}"
        if record.levelno == logging.INFO:
            msg = self._indent_continuations(msg, tty=True)
            return f"{cyn} ●{rst}  {msg}{rst}"
        if record.levelno == logging.WARNING:
            msg = self._indent_continuations(msg, tty=True)
            return f"{ylw} ▲{rst}  {msg}{rst}"
        if record.levelno >= logging.ERROR:
            msg = self._indent_continuations(msg, tty=True)
            return f"{red} ✖{rst}  {red}{msg}{rst}"
        return msg


def phase_banner(name: str) -> None:
    w = 44
    inner = name[: w - 2].center(w)
    bar = "─" * w
    if ansi_enabled():
        m = magenta
        sys.stderr.write(f"\n{m('╭' + bar + '╮')}\n")
        sys.stderr.write(f"{m('│')}{bold(inner)}{m('│')}\n")
        sys.stderr.write(f"{m('╰' + bar + '╯')}\n\n")
    else:
        sys.stderr.write(f"\n┌{bar}┐\n│{inner}│\n└{bar}┘\n\n")


def setup_logging(*, verbose: bool, force: bool = True) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s", force=force)
    for h in logging.root.handlers:
        h.setFormatter(HarnessFormatter())
    # Named harness logger (used by run.py, records.py) — explicit level, propagate to root.
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
    """
    Print the final run report on **stderr** with heavy borders so it reads as a
    footer, separate from normal ``LOG.info`` lines (cyan ● prefix).
    """
    width = 62
    sep_plain = "=" * width
    sep_tty = f"\033[38;5;177m{'━' * width}\033[0m" if ansi_enabled() else sep_plain

    status = bold("PASSED") if ok else bold("FAILED")
    body_lines = [
        f"Result · {status} · {n_done}/{n_plan} phase(s) · {elapsed_s:.1f}s",
        f"Target · {dim(base_url)}",
        f"Witness · {bold('on') if witness else dim('off')}",
    ]
    if not ok:
        if failed_phase:
            body_lines.append(f"Stopped · {bold(failed_phase)}")
        if completed_phases:
            body_lines.append(f"Completed · {dim(', '.join(completed_phases))}")

    sys.stderr.write("\n")
    sys.stderr.write(sep_tty + "\n")
    if ansi_enabled():
        sys.stderr.write(f"{magenta(' ▌ ')}{bold('Run summary')}\n")
    else:
        sys.stderr.write(" Run summary\n")
    sys.stderr.write(sep_tty + "\n")
    for ln in body_lines:
        sys.stderr.write(f"  {ln}\n")
    sys.stderr.write(sep_tty + "\n\n")
