import asyncio
import logging
from unittest.mock import MagicMock, patch

import pytest

from acapy_agent.core.event_bus import EventBus
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.protocol_registry import ProtocolRegistry
from traction_innkeeper.v1_0.tenant import (
    ContextFilter,
    context_tenant_id,
    setup_multitenant_logging,
    log_records_inject,
    setup,
)


def test_context_filter():
    f = ContextFilter()
    r = logging.LogRecord("n", 0, "", 0, "", (), None)
    assert f.filter(r)
    assert r.tenant_id is None
    token = context_tenant_id.set("x")
    try:
        assert f.filter(r)
        assert r.tenant_id == "x"
    finally:
        context_tenant_id.reset(token)


def test_setup_multitenant_logging_keeps_formatter():
    h = logging.StreamHandler()
    fmt = logging.Formatter("%(message)s")
    h.setFormatter(fmt)
    root = logging.getLogger()
    root.addHandler(h)
    try:
        setup_multitenant_logging()
        assert h.formatter is fmt
        assert any(isinstance(f, ContextFilter) for f in h.filters)
    finally:
        root.removeHandler(h)


async def test_log_records_inject_is_request_scoped():
    async def request(tid):
        log_records_inject(tid)
        await asyncio.sleep(0)
        return context_tenant_id.get()

    results = await asyncio.gather(asyncio.create_task(request("a")), asyncio.create_task(request("b")))
    assert results == ["a", "b"]
    assert context_tenant_id.get() is None


async def test_setup_success():
    ctx = MagicMock()
    ctx.inject.side_effect = {
        ProtocolRegistry: MagicMock(),
        PluginRegistry: MagicMock(),
        EventBus: MagicMock(),
    }.get
    with (
        patch("traction_innkeeper.v1_0.tenant.subscribe"),
        patch("traction_innkeeper.v1_0.tenant.HolderRevocationService"),
        patch("traction_innkeeper.v1_0.tenant.setup_multitenant_logging"),
    ):
        await setup(ctx)


@pytest.mark.parametrize(
    "inject_map,match",
    [
        ({}, "ProtocolRegistry"),
        ({ProtocolRegistry: MagicMock()}, "PluginRegistry"),
        ({ProtocolRegistry: MagicMock(), PluginRegistry: MagicMock()}, "EventBus"),
    ],
)
async def test_setup_missing_dep(inject_map, match):
    ctx = MagicMock()
    ctx.inject.side_effect = inject_map.get
    with pytest.raises(ValueError, match=match):
        await setup(ctx)
