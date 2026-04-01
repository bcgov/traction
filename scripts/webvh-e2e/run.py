#!/usr/bin/env python3
"""Traction WebVH E2E harness — see README.md for env, phases, and profiles."""

from __future__ import annotations

import logging
import sys
import time

import click
import requests
from dotenv import load_dotenv

from context import Context, build_context
from helpers import (
    webvh_explorer_dids_url,
    webvh_scid_from_did,
    webvh_server_base_for_explorer,
)
from phases import PHASES, PROFILES

LOG = logging.getLogger("webvh-e2e")

_SUMMARY_LABEL_WIDTH = 22


def _log_summary_kv(indent: str, label: str, value: object) -> None:
    LOG.info("%s%-*s  %s", indent, _SUMMARY_LABEL_WIDTH, label, value)


def _log_run_summary(ctx: Context, stop: str | None, plan: tuple[str, ...] | list[str]) -> None:
    LOG.info("")
    LOG.info("=== summary ===")
    LOG.info("")
    LOG.info("  run")
    _log_summary_kv("    ", "traction_url", ctx.base_url)

    if ctx.webvh_last_create_namespace is not None:
        LOG.info("")
        LOG.info("  webvh (create)")
        if ctx.webvh_last_created_did:
            last_created_did = ctx.webvh_last_created_did
            _log_summary_kv("    ", "did", last_created_did)
            scid = webvh_scid_from_did(last_created_did)
            explorer_base = webvh_server_base_for_explorer(
                ctx.webvh_last_create_server_url, last_created_did
            )
            if scid and explorer_base:
                _log_summary_kv(
                    "    ",
                    "explorer",
                    webvh_explorer_dids_url(explorer_base, scid),
                )
        elif stop is None:
            _log_summary_kv("    ", "did", "(not in create response yet)")

    elif ctx.webvh_server_url and "configure-webvh-plugin" in plan:
        LOG.info("")
        LOG.info("  webvh (controller)")
        _log_summary_kv("    ", "server_url", ctx.webvh_server_url)


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
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(message)s")

    try:
        ctx = build_context()
        ctx.use_witness = witness
    except RuntimeError as err:
        LOG.error("%s", err)
        return 1

    plan = PROFILES[profile]
    LOG.info("traction_url=%s profile=%s", ctx.base_url, profile)
    LOG.info("")

    run_started_at_monotonic = time.perf_counter()
    phases_completed = 0
    stop: str | None = None

    for phase_index, name in enumerate(plan):
        if phase_index:
            LOG.info("")
        LOG.info("-- %s --", name)
        try:
            if not PHASES[name](ctx):
                stop = name
                break
        except (RuntimeError, requests.RequestException) as phase_error:
            LOG.error("%s: %s", name, phase_error)
            stop = name
            break
        phases_completed += 1

    LOG.info("")
    LOG.info(
        "%s  %s/%s phases  %.1fs",
        "ok" if stop is None else "failed",
        phases_completed,
        len(plan),
        time.perf_counter() - run_started_at_monotonic,
    )
    _log_run_summary(ctx, stop, plan)
    return 0 if stop is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
