import logging
from unittest.mock import MagicMock, AsyncMock, patch, ANY

import pytest
from acapy_agent.core.profile import Profile
from acapy_agent.core.event_bus import Event, EventBus
from acapy_agent.storage.error import StorageNotFoundError, StorageError
from acapy_agent.protocols.issue_credential.v2_0.models.cred_ex_record import (
    V20CredExRecord,
)
from acapy_agent.revocation.models.issuer_cred_rev_record import IssuerCredRevRecord

# Import the module containing the service and handler to be tested
from traction_innkeeper.v1_0.tenant.issuer_revocation_service import (
    IssuerRevocationService,
    subscribe,
    issuer_cred_rev_revoked_handler,
    ISSUER_CRED_REV_REVOKED_EVENT_PATTERN,
)

# Disable logging noise during tests
logging.disable(logging.CRITICAL)

# --- Constants ---
TEST_CRED_EX_ID = "cred-ex-id-abc-987"
TEST_REV_REG_ID = "RvgFV1_CL_1_tag:4:RvgFV1_CL_1_tag:3:CL:1:tag:CL_ACCUM:default"
TEST_CRED_REV_ID = "12345"


# --- Fixtures ---
@pytest.fixture
def mock_profile():
    """Provides a mocked Profile with transaction and inject."""
    profile = MagicMock(spec=Profile)
    # Mock transaction context manager
    mock_txn = AsyncMock(name="MockTransaction")
    profile.transaction = MagicMock(return_value=mock_txn)
    mock_txn.__aenter__.return_value = mock_txn
    mock_txn.__aexit__.return_value = None
    mock_txn.commit = AsyncMock()
    # Mock injection directly on profile (for event handler)
    profile.inject = MagicMock()
    return profile, mock_txn


@pytest.fixture
def issuer_revocation_service():
    """Provides an IssuerRevocationService instance."""
    return IssuerRevocationService()


@pytest.fixture
def mock_v20_cred_ex_record():
    """Provides a mocked V20CredExRecord instance."""
    record = AsyncMock(spec=V20CredExRecord)
    record.cred_ex_id = TEST_CRED_EX_ID
    record.state = V20CredExRecord.STATE_DONE  # Initial state
    record.save = AsyncMock()
    return record


@pytest.fixture
def mock_issuer_cred_rev_record():
    """Provides a mocked IssuerCredRevRecord instance."""
    rev_rec = MagicMock(spec=IssuerCredRevRecord)
    rev_rec.cred_ex_id = TEST_CRED_EX_ID
    rev_rec.rev_reg_id = TEST_REV_REG_ID
    rev_rec.cred_rev_id = TEST_CRED_REV_ID
    rev_rec.state = "revoked"
    return rev_rec


@pytest.fixture
def mock_event():
    """Provides a mocked Event for issuer credential revocation."""
    event = MagicMock(spec=Event)
    event.topic = "acapy::record::issuer_cred_rev::revoked"
    # Event payload is a serialized dict representation
    event.payload = {
        "cred_ex_id": TEST_CRED_EX_ID,
        "rev_reg_id": TEST_REV_REG_ID,
        "cred_rev_id": TEST_CRED_REV_ID,
        "state": "revoked",
    }
    return event


@pytest.fixture
def mock_event_bus():
    """Provides a mocked EventBus."""
    bus = MagicMock(spec=EventBus)
    bus.subscribe = MagicMock()
    return bus


# --- Test Cases for IssuerRevocationService Methods ---


# Test update_credential_exchange_state
@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.issuer_revocation_service.V20CredExRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_update_credential_exchange_state_success(
    mock_retrieve: AsyncMock,
    issuer_revocation_service: IssuerRevocationService,
    mock_profile: tuple,
    mock_v20_cred_ex_record: AsyncMock,
    mock_issuer_cred_rev_record: MagicMock,
):
    """Test successfully updating a credential exchange to revoked state."""
    profile, txn = mock_profile
    mock_retrieve.return_value = mock_v20_cred_ex_record

    result = await issuer_revocation_service.update_credential_exchange_state(
        profile, mock_issuer_cred_rev_record
    )

    assert result is True
    assert mock_v20_cred_ex_record.state == V20CredExRecord.STATE_CREDENTIAL_REVOKED
    profile.transaction.assert_called_once()
    mock_retrieve.assert_awaited_once_with(txn, TEST_CRED_EX_ID, for_update=True)
    mock_v20_cred_ex_record.save.assert_awaited_once_with(
        txn, reason="revoke credential"
    )
    txn.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_credential_exchange_state_no_cred_ex_id(
    issuer_revocation_service: IssuerRevocationService,
    mock_profile: tuple,
    mock_issuer_cred_rev_record: MagicMock,
):
    """Test updating when IssuerCredRevRecord has no cred_ex_id."""
    profile, _ = mock_profile
    mock_issuer_cred_rev_record.cred_ex_id = None

    result = await issuer_revocation_service.update_credential_exchange_state(
        profile, mock_issuer_cred_rev_record
    )

    assert result is False
    profile.transaction.assert_not_called()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.issuer_revocation_service.V20CredExRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_update_credential_exchange_state_not_found(
    mock_retrieve: AsyncMock,
    issuer_revocation_service: IssuerRevocationService,
    mock_profile: tuple,
    mock_issuer_cred_rev_record: MagicMock,
):
    """Test updating when the credential exchange record is not found."""
    profile, txn = mock_profile
    mock_retrieve.side_effect = StorageNotFoundError("Record not found")

    result = await issuer_revocation_service.update_credential_exchange_state(
        profile, mock_issuer_cred_rev_record
    )

    # Service catches StorageNotFoundError and returns False
    assert result is False
    profile.transaction.assert_called_once()
    mock_retrieve.assert_awaited_once_with(txn, TEST_CRED_EX_ID, for_update=True)
    txn.commit.assert_not_called()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.issuer_revocation_service.V20CredExRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_update_credential_exchange_state_save_error(
    mock_retrieve: AsyncMock,
    issuer_revocation_service: IssuerRevocationService,
    mock_profile: tuple,
    mock_v20_cred_ex_record: AsyncMock,
    mock_issuer_cred_rev_record: MagicMock,
):
    """Test updating when save fails."""
    profile, txn = mock_profile
    mock_retrieve.return_value = mock_v20_cred_ex_record
    mock_v20_cred_ex_record.save.side_effect = StorageError("Save failed")

    # The service catches Exception and returns False
    result = await issuer_revocation_service.update_credential_exchange_state(
        profile, mock_issuer_cred_rev_record
    )

    assert result is False
    profile.transaction.assert_called_once()
    mock_retrieve.assert_awaited_once_with(txn, TEST_CRED_EX_ID, for_update=True)
    mock_v20_cred_ex_record.save.assert_awaited_once_with(
        txn, reason="revoke credential"
    )
    txn.commit.assert_not_called()


# --- Test Cases for Global Functions ---


# Test subscribe
def test_subscribe(mock_event_bus: MagicMock):
    """Test the subscribe function registers the handler."""
    subscribe(mock_event_bus)
    mock_event_bus.subscribe.assert_called_once_with(
        ISSUER_CRED_REV_REVOKED_EVENT_PATTERN, issuer_cred_rev_revoked_handler
    )


# Test issuer_cred_rev_revoked_handler
@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.issuer_revocation_service.IssuerCredRevRecord.deserialize"
)
async def test_issuer_cred_rev_revoked_handler_success(
    mock_deserialize: MagicMock,
    mock_profile: tuple,
    issuer_revocation_service: IssuerRevocationService,
    mock_event: MagicMock,
    mock_issuer_cred_rev_record: MagicMock,
):
    """Test the issuer_cred_rev_revoked_handler successfully processes event."""
    profile, _ = mock_profile

    # Mock profile.inject to return our service instance
    profile.inject.return_value = issuer_revocation_service

    # Mock deserialize to return our mock record
    mock_deserialize.return_value = mock_issuer_cred_rev_record

    # Mock the service method
    issuer_revocation_service.update_credential_exchange_state = AsyncMock(
        return_value=True
    )

    await issuer_cred_rev_revoked_handler(profile, mock_event)

    profile.inject.assert_called_once_with(IssuerRevocationService)
    mock_deserialize.assert_called_once_with(mock_event.payload)
    issuer_revocation_service.update_credential_exchange_state.assert_awaited_once_with(
        profile, mock_issuer_cred_rev_record
    )


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.issuer_revocation_service.IssuerCredRevRecord.deserialize"
)
async def test_issuer_cred_rev_revoked_handler_no_cred_ex_id(
    mock_deserialize: MagicMock,
    mock_profile: tuple,
    issuer_revocation_service: IssuerRevocationService,
    mock_event: MagicMock,
    mock_issuer_cred_rev_record: MagicMock,
):
    """Test the handler when IssuerCredRevRecord has no cred_ex_id."""
    profile, _ = mock_profile
    profile.inject.return_value = issuer_revocation_service

    # Mock record with no cred_ex_id
    mock_issuer_cred_rev_record.cred_ex_id = None
    mock_deserialize.return_value = mock_issuer_cred_rev_record

    issuer_revocation_service.update_credential_exchange_state = AsyncMock()

    await issuer_cred_rev_revoked_handler(profile, mock_event)

    profile.inject.assert_called_once_with(IssuerRevocationService)
    mock_deserialize.assert_called_once_with(mock_event.payload)
    # Should not call update_credential_exchange_state when cred_ex_id is missing
    issuer_revocation_service.update_credential_exchange_state.assert_not_awaited()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.issuer_revocation_service.IssuerCredRevRecord.deserialize"
)
async def test_issuer_cred_rev_revoked_handler_deserialize_error(
    mock_deserialize: MagicMock,
    mock_profile: tuple,
    issuer_revocation_service: IssuerRevocationService,
    mock_event: MagicMock,
):
    """Test the handler when deserialization fails."""
    profile, _ = mock_profile
    profile.inject.return_value = issuer_revocation_service

    # Mock deserialize to raise an error
    mock_deserialize.side_effect = ValueError("Deserialization failed")

    issuer_revocation_service.update_credential_exchange_state = AsyncMock()

    # Handler should catch the exception and not raise
    await issuer_cred_rev_revoked_handler(profile, mock_event)

    profile.inject.assert_called_once_with(IssuerRevocationService)
    mock_deserialize.assert_called_once_with(mock_event.payload)
    # Should not call update_credential_exchange_state when deserialization fails
    issuer_revocation_service.update_credential_exchange_state.assert_not_awaited()
