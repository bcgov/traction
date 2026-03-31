#!/usr/bin/env python3
"""
Traction WebVH E2E harness — HTTP checks against the tenant proxy.

See README.md for environment variables, phases, and profiles.

Default run: ``--profile all`` (all registered phases).
Use ``--profile new-issuer-webvh`` for the WebVH-named phase path.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from context import build_context
from phases import PHASES, PROFILES

LOG = logging.getLogger("webvh-e2e")


def setup_logging(*, verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s")


def phase_banner(name: str) -> None:
    LOG.info("\n== %s ==", name)


def run_summary(
    *,
    ok: bool,
    n_done: int,
    n_plan: int,
    elapsed_s: float,
    failed_phase: str | None,
) -> None:
    status = "ok" if ok else "failed"
    LOG.info(
        "\n== summary ==\n%s  %s/%s phases  %.1fs",
        status,
        n_done,
        n_plan,
        elapsed_s,
    )
    if failed_phase:
        LOG.info("stopped: %s", failed_phase)


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
    args = parser.parse_args()
    setup_logging(verbose=args.verbose)

    try:
        ctx = build_context()
    except RuntimeError as e:
        LOG.error("%s", e)
        return 1
    to_run = PROFILES[args.profile]
    run_desc = f"profile {args.profile}"

    LOG.info(
        "Run target\nbase_url=%s\nrun=%s",
        ctx.base_url,
        run_desc,
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

    run_summary(
        ok=ok,
        n_done=len(completed),
        n_plan=len(to_run),
        elapsed_s=time.perf_counter() - t0,
        failed_phase=failed_phase,
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
