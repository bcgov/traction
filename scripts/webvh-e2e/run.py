#!/usr/bin/env python3
"""Traction WebVH E2E harness — see README.md for env, phases, and profiles."""

from __future__ import annotations

import time

import click
import requests
from dotenv import load_dotenv

from context import build_context
from helpers import HarnessLogger
from phases import PHASES, PROFILES


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--profile",
    type=click.Choice(tuple(PROFILES.keys())),
    default="all",
    show_default=True,
    help="Phase bundle to run.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
@click.option(
    "--witness",
    is_flag=True,
    help="Include endorsement in POST /did/webvh/configuration (endorser-style flow).",
)
def main(profile: str, verbose: bool, witness: bool) -> int:
    """Run WebVH E2E phases against the Traction tenant proxy."""
    load_dotenv()
    HarnessLogger.configure_cli_logging(verbose=verbose)

    try:
        context = build_context(use_witness=witness)
    except RuntimeError as err:
        HarnessLogger.log_context_init_failed(str(err))
        return 1

    plan = PROFILES[profile]
    HarnessLogger.log_run_start(context.base_url, profile)

    run_started_at_monotonic = time.perf_counter()
    phases_completed = 0
    stop: str | None = None

    for phase_index, name in enumerate(plan):
        HarnessLogger.log_phase_begin(name, is_first_phase=(phase_index == 0))
        try:
            if not PHASES[name](context):
                stop = name
                break
        except (RuntimeError, requests.RequestException) as phase_error:
            HarnessLogger.log_phase_uncaught_exception(name, phase_error)
            stop = name
            break
        phases_completed += 1

    HarnessLogger.log_run_footer(
        success=(stop is None),
        phases_completed=phases_completed,
        phase_count=len(plan),
        elapsed_seconds=time.perf_counter() - run_started_at_monotonic,
    )
    HarnessLogger.log_run_summary(context, stop, plan)
    return 0 if stop is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
