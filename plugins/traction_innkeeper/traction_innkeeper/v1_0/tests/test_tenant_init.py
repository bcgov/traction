import logging
from unittest.mock import MagicMock, patch

import pytest

from acapy_agent.core.event_bus import EventBus
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.protocol_registry import ProtocolRegistry
from traction_innkeeper.v1_0.tenant import (
    ContextFilter,
    setup_multitenant_logging,
    log_records_inject,
    setup,
)


def test_context_filter():
    f = ContextFilter()
    r = logging.LogRecord("n", 0, "", 0, "", (), None)
    assert f.filter(r)
    r.tenant_id = "x"
    assert f.filter(r)


def test_setup_multitenant_logging():
    h = MagicMock()
    with patch("traction_innkeeper.v1_0.tenant.logging") as m:
        m.getLogger.return_value.handlers = [h]
        setup_multitenant_logging()
    h.setFormatter.assert_called_once()


def test_log_records_inject():
    orig = logging.getLogRecordFactory()
    log_records_inject("t")
    assert logging.getLogRecordFactory()("n", 0, "", 0, "", (), None).tenant_id == "t"
    logging.setLogRecordFactory(orig)


def test_log_records_inject_error():
    with patch("traction_innkeeper.v1_0.tenant.base_log_record_factory", side_effect=Exception):
        log_records_inject("t")


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


@pytest.mark.parametrize("inject_map,match", [
    ({}, "ProtocolRegistry"),
    ({ProtocolRegistry: MagicMock()}, "PluginRegistry"),
    ({ProtocolRegistry: MagicMock(), PluginRegistry: MagicMock()}, "EventBus"),
])
async def test_setup_missing_dep(inject_map, match):
    ctx = MagicMock()
    ctx.inject.side_effect = inject_map.get
    with pytest.raises(ValueError, match=match):
        await setup(ctx)
