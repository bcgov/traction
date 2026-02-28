from traction_innkeeper.v1_0.innkeeper.config import (
    _alias_generator,
    EndorserLedgerConfig,
    get_config,
)


def test_endorser_config():
    assert _alias_generator("a_b") == "a-b"
    assert EndorserLedgerConfig(endorser_alias="a", ledger_id="b").serialize()


def test_get_config():
    c = get_config({"plugin_config": {"traction_innkeeper": {"innkeeper_wallet": {"tenant_id": "x"}}}})
    assert c.innkeeper_wallet.tenant_id == "x"
    assert get_config({}).reservation.expiry_minutes == 60
