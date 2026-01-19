import logging
from unittest.mock import MagicMock, AsyncMock, patch, ANY

import pytest
from acapy_agent.core.profile import Profile
from acapy_agent.core.event_bus import Event, EventBus
from acapy_agent.storage.error import StorageError, StorageNotFoundError
from acapy_agent.messaging.models.base import BaseModelError

# Assuming models and service are importable like this
from acapy_agent.protocols.issue_credential.v2_0.models.cred_ex_record import (
    V20CredExRecord,
)
from acapy_agent.protocols.issue_credential.v2_0.models.detail.indy import (
    V20CredExRecordIndy,
)

# Import the module containing the service and handler to be tested
from traction_innkeeper.v1_0.tenant.holder_revocation_service import (
    HolderRevocationService,
    subscribe,
    revocation_notification_handler,
    REVOCATION_NOTIFICATION_EVENT_PATTERN,
)

# Disable logging noise during tests
logging.disable(logging.CRITICAL)

# --- Constants ---
TEST_REV_REG_ID = "RvgFV1_CL_1_tag:4:RvgFV1_CL_1_tag:3:CL:1:tag:CL_ACCUM:default"
TEST_REVOCATION_ID = "12345"
TEST_THREAD_ID = f"indy::{TEST_REV_REG_ID}::{TEST_REVOCATION_ID}"
TEST_CRED_EX_ID = "cred-ex-id-abc-987"
TEST_COMMENT = "Credential revoked by issuer"


# --- Fixtures ---
@pytest.fixture
def mock_profile():
    """Provides a mocked Profile with session, transaction, and inject."""
    profile = MagicMock(spec=Profile)
    # Mock session context manager
    mock_session = AsyncMock(name="MockSession")
    profile.session = MagicMock(return_value=mock_session)
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    # Mock transaction context manager
    mock_txn = AsyncMock(name="MockTransaction")
    profile.transaction = MagicMock(return_value=mock_txn)
    mock_txn.__aenter__.return_value = mock_txn
    mock_txn.__aexit__.return_value = None
    mock_txn.commit = AsyncMock()
    mock_txn.rollback = AsyncMock()
    # Mock injection directly on profile (for event handler)
    profile.inject = MagicMock()
    return profile, mock_session, mock_txn


@pytest.fixture
def holder_revocation_service():
    """Provides a HolderRevocationService instance."""
    return HolderRevocationService()


@pytest.fixture
def mock_v20_cred_ex_record():
    """Provides a mocked V20CredExRecord instance."""
    record = AsyncMock(spec=V20CredExRecord)
    record.cred_ex_id = TEST_CRED_EX_ID
    record.state = V20CredExRecord.STATE_DONE  # Initial state
    record.error_msg = None
    record.save = AsyncMock()
    return record


@pytest.fixture
def mock_v20_cred_ex_indy_detail():
    """Provides a mocked V20CredExRecordIndy detail record."""
    detail = AsyncMock(spec=V20CredExRecordIndy)
    detail.cred_ex_id = TEST_CRED_EX_ID
    detail.rev_reg_id = TEST_REV_REG_ID
    detail.cred_rev_id = TEST_REVOCATION_ID
    return detail


@pytest.fixture
def mock_event():
    """Provides a mocked Event for revocation notification."""
    event = MagicMock(spec=Event)
    event.payload = {"thread_id": TEST_THREAD_ID, "comment": TEST_COMMENT}
    return event


@pytest.fixture
def mock_event_bus():
    """Provides a mocked EventBus."""
    bus = MagicMock(spec=EventBus)
    bus.subscribe = MagicMock()
    return bus


# --- Test Cases for HolderRevocationService Methods ---


# Test parse_thread_id
def test_parse_thread_id(holder_revocation_service: HolderRevocationService):
    """Test parsing a valid thread_id."""
    revoc_reg_id, revocation_id = holder_revocation_service.parse_thread_id(
        TEST_THREAD_ID
    )
    assert revoc_reg_id == TEST_REV_REG_ID
    assert revocation_id == TEST_REVOCATION_ID


def test_parse_thread_id_invalid_format(
    holder_revocation_service: HolderRevocationService,
):
    """Test parsing an invalid thread_id format."""
    with pytest.raises(IndexError):
        holder_revocation_service.parse_thread_id("invalid-thread-id")


# Test find_credential_exchange_v20
@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.holder_revocation_service.V20CredExRecordIndy.query",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.tenant.holder_revocation_service.V20CredExRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_find_credential_exchange_v20_success(
    mock_retrieve: AsyncMock,
    mock_indy_query: AsyncMock,
    holder_revocation_service: HolderRevocationService,
    mock_profile: tuple,
    mock_v20_cred_ex_record: AsyncMock,
    mock_v20_cred_ex_indy_detail: AsyncMock,
):
    """Test finding a V20 credential exchange successfully."""
    profile, session, _ = mock_profile
    mock_indy_query.return_value = [mock_v20_cred_ex_indy_detail]
    mock_retrieve.return_value = mock_v20_cred_ex_record

    result = await holder_revocation_service.find_credential_exchange_v20(
        profile, TEST_REV_REG_ID, TEST_REVOCATION_ID
    )

    assert result == mock_v20_cred_ex_record
    profile.session.assert_called_once()
    expected_tag_filter = {}
    expected_post_filter = {
        "rev_reg_id": TEST_REV_REG_ID,
        "cred_rev_id": TEST_REVOCATION_ID,
    }
    mock_indy_query.assert_awaited_once_with(
        session=session,
        tag_filter=expected_tag_filter,
        post_filter_positive=expected_post_filter,
    )
    mock_retrieve.assert_awaited_once_with(session, TEST_CRED_EX_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.holder_revocation_service.V20CredExRecordIndy.query",
    new_callable=AsyncMock,
)
async def test_find_credential_exchange_v20_not_found(
    mock_indy_query: AsyncMock,
    holder_revocation_service: HolderRevocationService,
    mock_profile: tuple,
):
    """Test finding V20 credential exchange when none exists."""
    profile, session, _ = mock_profile
    mock_indy_query.return_value = []  # No records found

    # Service should handle empty results
    result = await holder_revocation_service.find_credential_exchange_v20(
        profile, TEST_REV_REG_ID, TEST_REVOCATION_ID
    )

    assert result is None
    profile.session.assert_called_once()
    mock_indy_query.assert_awaited_once_with(
        session=session, tag_filter=ANY, post_filter_positive=ANY
    )


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.holder_revocation_service.V20CredExRecordIndy.query",
    new_callable=AsyncMock,
)
@pytest.mark.parametrize("error_cls", [StorageError, BaseModelError])
async def test_find_credential_exchange_v20_query_error(
    mock_indy_query: AsyncMock,
    error_cls: type,
    holder_revocation_service: HolderRevocationService,
    mock_profile: tuple,
):
    """Test finding V20 credential exchange with storage/model errors."""
    profile, session, _ = mock_profile
    mock_indy_query.side_effect = error_cls("Query failed")

    result = await holder_revocation_service.find_credential_exchange_v20(
        profile, TEST_REV_REG_ID, TEST_REVOCATION_ID
    )

    # Service catches the error and returns None
    assert result is None
    profile.session.assert_called_once()
    mock_indy_query.assert_awaited_once_with(
        session=session, tag_filter=ANY, post_filter_positive=ANY
    )


# Test set_credential_exchange_revoked_v20
@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.holder_revocation_service.V20CredExRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_set_credential_exchange_revoked_v20_success(
    mock_retrieve: AsyncMock,
    holder_revocation_service: HolderRevocationService,
    mock_profile: tuple,
    mock_v20_cred_ex_record: AsyncMock,
):
    """Test successfully setting a credential exchange to revoked state."""
    profile, _, txn = mock_profile
    mock_retrieve.return_value = mock_v20_cred_ex_record

    result = await holder_revocation_service.set_credential_exchange_revoked_v20(
        profile, TEST_CRED_EX_ID, TEST_COMMENT
    )

    assert result == mock_v20_cred_ex_record
    assert result.state == V20CredExRecord.STATE_CREDENTIAL_REVOKED
    assert result.error_msg == TEST_COMMENT
    profile.transaction.assert_called_once()
    mock_retrieve.assert_awaited_once_with(txn, TEST_CRED_EX_ID, for_update=True)
    mock_v20_cred_ex_record.save.assert_awaited_once_with(
        txn, reason="revoke credential"
    )
    txn.commit.assert_awaited_once()
    txn.rollback.assert_not_called()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.holder_revocation_service.V20CredExRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_set_credential_exchange_revoked_v20_not_found(
    mock_retrieve: AsyncMock,
    holder_revocation_service: HolderRevocationService,
    mock_profile: tuple,
):
    """Test setting revoked state when the record is not found."""
    profile, _, txn = mock_profile
    mock_retrieve.side_effect = StorageNotFoundError("Record not found")

    result = await holder_revocation_service.set_credential_exchange_revoked_v20(
        profile, TEST_CRED_EX_ID, TEST_COMMENT
    )

    # Service catches and returns None
    assert result is None
    profile.transaction.assert_called_once()
    mock_retrieve.assert_awaited_once_with(txn, TEST_CRED_EX_ID, for_update=True)
    txn.commit.assert_not_called()  # Commit shouldn't happen
    # Rollback might be called implicitly by context manager exit on error


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.tenant.holder_revocation_service.V20CredExRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_set_credential_exchange_revoked_v20_save_error(
    mock_retrieve: AsyncMock,
    holder_revocation_service: HolderRevocationService,
    mock_profile: tuple,
    mock_v20_cred_ex_record: AsyncMock,
):
    """Test setting revoked state when save fails."""
    profile, _, txn = mock_profile
    mock_retrieve.return_value = mock_v20_cred_ex_record
    mock_v20_cred_ex_record.save.side_effect = StorageError("Save failed")

    # The service doesn't explicitly catch this, expect StorageError propagation
    with pytest.raises(StorageError, match="Save failed"):
        await holder_revocation_service.set_credential_exchange_revoked_v20(
            profile, TEST_CRED_EX_ID, TEST_COMMENT
        )

    profile.transaction.assert_called_once()
    mock_retrieve.assert_awaited_once_with(txn, TEST_CRED_EX_ID, for_update=True)
    mock_v20_cred_ex_record.save.assert_awaited_once_with(
        txn, reason="revoke credential"
    )
    txn.commit.assert_not_called()  # Commit shouldn't happen


# --- Test Cases for Global Functions ---


# Test subscribe
def test_subscribe(mock_event_bus: MagicMock):
    """Test the subscribe function registers the handler."""
    subscribe(mock_event_bus)
    mock_event_bus.subscribe.assert_called_once_with(
        REVOCATION_NOTIFICATION_EVENT_PATTERN, revocation_notification_handler
    )


# Test revocation_notification_handler
@pytest.mark.asyncio
async def test_revocation_notification_handler_success(
    mock_profile: tuple,
    holder_revocation_service: HolderRevocationService,  # Use fixture
    mock_event: MagicMock,
    mock_v20_cred_ex_record: AsyncMock,
):
    """Test the revocation_notification_handler successfully finds and updates."""
    profile, _, _ = mock_profile

    # Mock profile.inject to return our service instance
    profile.inject.return_value = holder_revocation_service

    # Mock the service methods specifically for this test
    holder_revocation_service.parse_thread_id = MagicMock(
        return_value=(TEST_REV_REG_ID, TEST_REVOCATION_ID)
    )
    holder_revocation_service.find_credential_exchange_v20 = AsyncMock(
        return_value=mock_v20_cred_ex_record
    )
    holder_revocation_service.set_credential_exchange_revoked_v20 = AsyncMock(
        return_value=mock_v20_cred_ex_record  # Simulate successful update
    )

    await revocation_notification_handler(profile, mock_event)

    profile.inject.assert_called_once_with(HolderRevocationService)
    holder_revocation_service.parse_thread_id.assert_called_once_with(TEST_THREAD_ID)
    holder_revocation_service.find_credential_exchange_v20.assert_awaited_once_with(
        profile, TEST_REV_REG_ID, TEST_REVOCATION_ID
    )
    holder_revocation_service.set_credential_exchange_revoked_v20.assert_awaited_once_with(
        profile, TEST_CRED_EX_ID, TEST_COMMENT
    )


@pytest.mark.asyncio
async def test_revocation_notification_handler_record_not_found(
    mock_profile: tuple,
    holder_revocation_service: HolderRevocationService,
    mock_event: MagicMock,
):
    """Test the handler when the credential exchange record is not found."""
    profile, _, _ = mock_profile
    profile.inject.return_value = holder_revocation_service
    holder_revocation_service.parse_thread_id = MagicMock(
        return_value=(TEST_REV_REG_ID, TEST_REVOCATION_ID)
    )
    # Simulate find returning None
    holder_revocation_service.find_credential_exchange_v20 = AsyncMock(
        return_value=None
    )
    holder_revocation_service.set_credential_exchange_revoked_v20 = AsyncMock()

    await revocation_notification_handler(profile, mock_event)

    profile.inject.assert_called_once_with(HolderRevocationService)
    holder_revocation_service.parse_thread_id.assert_called_once_with(TEST_THREAD_ID)
    holder_revocation_service.find_credential_exchange_v20.assert_awaited_once_with(
        profile, TEST_REV_REG_ID, TEST_REVOCATION_ID
    )
    # Ensure set_credential_exchange_revoked_v20 was NOT called
    holder_revocation_service.set_credential_exchange_revoked_v20.assert_not_awaited()
