#!/usr/bin/env python3
"""
Traction WebVH E2E harness — HTTP checks against the tenant proxy.

See README.md for environment variables, phases, and profiles.

Default run: ``--profile all`` (all registered phases).
Use ``--profile new-issuer-webvh`` for the WebVH-named phase path.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from context import build_context
from harness_log import (
    LOG,
    bold,
    detail_field_line,
    phase_banner,
    run_summary_standout,
    setup_logging,
    wrap_dim_block,
)
from phases import PHASES, PROFILES


def _load_local_env() -> None:
    """Load ``scripts/webvh-e2e/.env`` if present (does not override existing OS env)."""
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.is_file():
        load_dotenv(env_file, override=False)


def main() -> int:
    _load_local_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=tuple(PROFILES.keys()),
        default="all",
        help=(
            "Phase bundle: ``all`` = every registered phase (default). "
            "``new-issuer-webvh`` = smoke through ``verify-webvh-post-revoke``."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Debug logging",
    )
    parser.add_argument(
        "--witness",
        action="store_true",
        help=(
            "Include witnesses and witness threshold in POST /did/webvh/create "
            "(default: omit them for a no-witness create payload)"
        ),
    )
    args = parser.parse_args()
    setup_logging(verbose=args.verbose)

    try:
        ctx = build_context()
    except RuntimeError as e:
        LOG.error("%s", e)
        return 1
    ctx.use_witness = bool(args.witness)
    to_run = PROFILES[args.profile]
    run_desc = f"profile {args.profile}"

    LOG.info(
        "%s\n%s\n%s\n%s",
        bold("Run target"),
        wrap_dim_block("base_url", ctx.base_url),
        detail_field_line(
            "witness",
            "on" if ctx.use_witness else "off",
            emphasis=ctx.use_witness,
        ),
        detail_field_line("run", run_desc),
    )

    ok = True
    completed: list[str] = []
    failed_phase: str | None = None
    t0 = time.perf_counter()
    for name in to_run:
        phase_banner(name)
        fn = PHASES[name]
        try:
            if not fn(ctx):
                ok = False
                failed_phase = name
                break
        except RuntimeError as e:
            LOG.error("%s", e)
            ok = False
            failed_phase = name
            break
        except requests.RequestException as e:
            LOG.error("HTTP error in phase %r  %s", name, e)
            ok = False
            failed_phase = name
            break
        completed.append(name)

    run_summary_standout(
        ok=ok,
        base_url=ctx.base_url,
        witness=ctx.use_witness,
        n_done=len(completed),
        n_plan=len(to_run),
        elapsed_s=time.perf_counter() - t0,
        failed_phase=failed_phase,
        completed_phases=tuple(completed),
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
