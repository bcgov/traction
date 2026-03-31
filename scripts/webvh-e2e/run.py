#!/usr/bin/env python3
"""Traction WebVH E2E harness — see README.md for env, phases, and profiles."""

from __future__ import annotations

import logging
import sys
import time

import click
import requests
from dotenv import load_dotenv

from context import build_context
from phases import PHASES, PROFILES

LOG = logging.getLogger("webvh-e2e")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--profile",
    type=click.Choice(tuple(PROFILES.keys())),
    default="all",
    show_default=True,
    help="Phase bundle to run.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
def main(profile: str, verbose: bool) -> int:
    """Run WebVH E2E phases against the Traction tenant proxy."""
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(message)s")

    try:
        ctx = build_context()
    except RuntimeError as e:
        LOG.error("%s", e)
        return 1

    plan = PROFILES[profile]
    LOG.info("base_url=%s profile=%s", ctx.base_url, profile)
    LOG.info("")

    t0 = time.perf_counter()
    done = 0
    stop: str | None = None

    for i, name in enumerate(plan):
        if i:
            LOG.info("")
        LOG.info("-- %s --", name)
        try:
            if not PHASES[name](ctx):
                stop = name
                break
        except (RuntimeError, requests.RequestException) as err:
            LOG.error("%s: %s", name, err)
            stop = name
            break
        done += 1

    LOG.info("")
    LOG.info(
        "%s  %s/%s phases  %.1fs",
        "ok" if stop is None else "failed",
        done,
        len(plan),
        time.perf_counter() - t0,
    )
    return 0 if stop is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
