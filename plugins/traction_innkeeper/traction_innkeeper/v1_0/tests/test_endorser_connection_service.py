import logging
from unittest.mock import MagicMock, AsyncMock, patch, call

import pytest
from acapy_agent.core.profile import Profile
from acapy_agent.core.event_bus import Event, EventBus
from acapy_agent.config.injector import Injector
from acapy_agent.connections.models.conn_record import ConnRecord
from acapy_agent.wallet.models.wallet_record import WalletRecord


from traction_innkeeper.v1_0.innkeeper.models import TenantRecord


# Import the module containing the service and handler to be tested
from traction_innkeeper.v1_0.endorser import endorser_connection_service as test_module
from traction_innkeeper.v1_0.endorser.endorser_connection_service import (
    EndorserConnectionService,
    connections_event_handler,
    CONNECTIONS_EVENT_PATTERN,
)

# Import mocked dependencies


# Disable logging noise during tests
logging.disable(logging.CRITICAL)

# --- Constants ---
TEST_ENDORSER_ALIAS = "TestEndorser"
TEST_ENDORSER_DID = "did:sov:EndorserDID123"
TEST_TENANT_WALLET_ID = "tenant-wallet-abc"
TEST_TENANT_NAME = "Tenant Name"
TEST_WALLET_NAME = "Wallet Name"
TEST_CONN_ID = "conn-id-xyz-789"


# --- Fixtures ---
@pytest.fixture
def mock_profile():
    """Provides a mocked Profile with settings, session, and inject."""
    profile = MagicMock(spec=Profile)
    mock_session = AsyncMock(name="MockSession")
    profile.session = MagicMock(return_value=mock_session)
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    profile.settings = MagicMock()
    profile.settings.get = MagicMock()  # Mock the .get method directly
    profile.inject = MagicMock()
    return profile, mock_session


@pytest.fixture
def mock_context():
    """Provides a mocked Injector context."""
    context = MagicMock(spec=Injector)
    context.inject = MagicMock()
    return context


@pytest.fixture
def endorser_service():
    """Provides an EndorserConnectionService instance."""
    # Service has no constructor dependencies
    return EndorserConnectionService()


@pytest.fixture
def mock_conn_record():
    """Provides a mocked ConnRecord instance."""
    record = AsyncMock(spec=ConnRecord)
    record.connection_id = TEST_CONN_ID
    record.alias = TEST_ENDORSER_ALIAS
    record.state = ConnRecord.State.COMPLETED
    record.metadata_get_all = AsyncMock()
    record.metadata_get = AsyncMock()
    record.metadata_set = AsyncMock()
    return record


@pytest.fixture
def mock_event(mock_conn_record: AsyncMock):
    """Provides a mocked Event instance with a serialized ConnRecord payload."""
    event = MagicMock(spec=Event)
    # Simulate serialized payload; deserialize will be mocked
    event.payload = {
        "connection_id": mock_conn_record.connection_id,
        "alias": mock_conn_record.alias,
        "state": mock_conn_record.state.rfc160,
    }
    return event


# --- Test Cases for EndorserConnectionService Methods ---


def test_endorser_alias(
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test getting the endorser alias from settings."""
    profile, _ = mock_profile
    profile.settings.get.return_value = TEST_ENDORSER_ALIAS
    assert endorser_service.endorser_alias(profile) == TEST_ENDORSER_ALIAS
    profile.settings.get.assert_called_once_with("endorser.endorser_alias")


def test_endorser_alias_missing(
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test getting endorser alias when setting is missing."""
    profile, _ = mock_profile
    profile.settings.get.return_value = None
    assert endorser_service.endorser_alias(profile) is None
    profile.settings.get.assert_called_once_with("endorser.endorser_alias")


def test_endorser_public_did(
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test getting the endorser public DID from settings."""
    profile, _ = mock_profile
    profile.settings.get.return_value = TEST_ENDORSER_DID
    assert endorser_service.endorser_public_did(profile) == TEST_ENDORSER_DID
    profile.settings.get.assert_called_once_with("endorser.endorser_public_did")


def test_endorser_public_did_missing(
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test getting endorser public DID when setting is missing."""
    profile, _ = mock_profile
    profile.settings.get.return_value = None
    assert endorser_service.endorser_public_did(profile) is None
    profile.settings.get.assert_called_once_with("endorser.endorser_public_did")


def test_endorser_info_success(
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test getting endorser info when both settings are present."""
    profile, _ = mock_profile

    # Configure profile.settings.get side effect
    def get_setting(key):
        if key == "endorser.endorser_alias":
            return TEST_ENDORSER_ALIAS
        if key == "endorser.endorser_public_did":
            return TEST_ENDORSER_DID
        return None

    profile.settings.get.side_effect = get_setting

    expected_info = {
        "endorser_did": TEST_ENDORSER_DID,
        "endorser_name": TEST_ENDORSER_ALIAS,
    }
    assert endorser_service.endorser_info(profile) == expected_info
    assert profile.settings.get.call_count == 2
    profile.settings.get.assert_has_calls(
        [
            call("endorser.endorser_alias"),
            call("endorser.endorser_public_did"),
        ],
        any_order=True,
    )


@pytest.mark.parametrize(
    "alias, did",
    [
        (None, TEST_ENDORSER_DID),
        (TEST_ENDORSER_ALIAS, None),
        (None, None),
    ],
)
def test_endorser_info_missing_data(
    alias,
    did,
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test getting endorser info when one or both settings are missing."""
    profile, _ = mock_profile

    def get_setting(key):
        if key == "endorser.endorser_alias":
            return alias
        if key == "endorser.endorser_public_did":
            return did
        return None

    profile.settings.get.side_effect = get_setting

    assert endorser_service.endorser_info(profile) is None
    # Check that both were attempted
    assert profile.settings.get.call_count >= 1


@pytest.mark.asyncio
@patch.object(test_module.ConnRecord, "retrieve_by_alias", new_callable=AsyncMock)
async def test_endorser_connection_found(
    mock_retrieve_by_alias: AsyncMock,
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_conn_record: AsyncMock,
):
    """Test finding an existing endorser connection."""
    profile, session = mock_profile
    # Mock endorser_info to return valid data
    endorser_service.endorser_info = MagicMock(
        return_value={
            "endorser_did": TEST_ENDORSER_DID,
            "endorser_name": TEST_ENDORSER_ALIAS,
        }
    )
    mock_retrieve_by_alias.return_value = [mock_conn_record]  # Found one record

    result = await endorser_service.endorser_connection(profile)

    assert result == mock_conn_record
    endorser_service.endorser_info.assert_called_once_with(profile)
    profile.session.assert_called_once()
    mock_retrieve_by_alias.assert_awaited_once_with(session, alias=TEST_ENDORSER_ALIAS)


@pytest.mark.asyncio
@patch.object(test_module.ConnRecord, "retrieve_by_alias", new_callable=AsyncMock)
async def test_endorser_connection_not_found(
    mock_retrieve_by_alias: AsyncMock,
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test when endorser connection doesn't exist."""
    profile, session = mock_profile
    endorser_service.endorser_info = MagicMock(
        return_value={
            "endorser_did": TEST_ENDORSER_DID,
            "endorser_name": TEST_ENDORSER_ALIAS,
        }
    )
    mock_retrieve_by_alias.return_value = []  # Found no records

    result = await endorser_service.endorser_connection(profile)

    assert result is None
    endorser_service.endorser_info.assert_called_once_with(profile)
    profile.session.assert_called_once()
    mock_retrieve_by_alias.assert_awaited_once_with(session, alias=TEST_ENDORSER_ALIAS)


@pytest.mark.asyncio
async def test_endorser_connection_no_info(
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test endorser_connection when endorser_info returns None."""
    profile, _ = mock_profile
    endorser_service.endorser_info = MagicMock(return_value=None)

    result = await endorser_service.endorser_connection(profile)

    assert result is None
    endorser_service.endorser_info.assert_called_once_with(profile)
    profile.session.assert_not_called()  # Should not try to get session


@pytest.mark.asyncio
async def test_connect_with_endorser_no_info(
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_context: MagicMock,
):
    """Test connect_with_endorser when endorser_info returns None."""
    profile, _ = mock_profile
    endorser_service.endorser_info = MagicMock(return_value=None)

    result = await endorser_service.connect_with_endorser(profile, mock_context)

    assert result is None
    endorser_service.endorser_info.assert_called_once_with(profile)
    # Ensure no further calls were made
    mock_context.inject.assert_not_called()


@pytest.mark.asyncio
async def test_connect_with_endorser_already_connected(
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_context: MagicMock,
    mock_conn_record: AsyncMock,
):
    """Test connect_with_endorser when connection already exists."""
    profile, _ = mock_profile
    endorser_service.endorser_info = MagicMock(
        return_value={
            "endorser_did": TEST_ENDORSER_DID,
            "endorser_name": TEST_ENDORSER_ALIAS,
        }
    )
    # Mock endorser_connection to return an existing connection
    endorser_service.endorser_connection = AsyncMock(return_value=mock_conn_record)

    result = await endorser_service.connect_with_endorser(profile, mock_context)

    assert result == mock_conn_record
    endorser_service.endorser_info.assert_called_once_with(profile)
    endorser_service.endorser_connection.assert_awaited_once_with(profile)
    # Ensure creation logic was not called
    mock_context.inject.assert_not_called()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.endorser.endorser_connection_service.TenantManager",
    autospec=True,
)
@patch(
    "traction_innkeeper.v1_0.endorser.endorser_connection_service.DIDXManager",
    autospec=True,
)
async def test_connect_with_endorser_create_connection(
    MockDIDXManager: MagicMock,
    MockTenantManager: MagicMock,
    endorser_service: EndorserConnectionService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_context: MagicMock,
):
    """Test connect_with_endorser initiating a new connection."""
    profile, _ = mock_profile
    endorser_info_dict = {
        "endorser_did": TEST_ENDORSER_DID,
        "endorser_name": TEST_ENDORSER_ALIAS,
    }
    endorser_service.endorser_info = MagicMock(return_value=endorser_info_dict)
    # Mock endorser_connection to return None (not connected)
    endorser_service.endorser_connection = AsyncMock(return_value=None)

    # Mock profile settings for wallet ID
    profile.settings.get.return_value = TEST_TENANT_WALLET_ID

    # Mock TenantManager
    mock_tenant_mgr_instance = MockTenantManager.return_value
    mock_wallet_rec = MagicMock(spec=WalletRecord, wallet_name=TEST_WALLET_NAME)
    mock_tenant_rec = MagicMock(spec=TenantRecord, tenant_name=TEST_TENANT_NAME)
    mock_tenant_mgr_instance.get_wallet_and_tenant = AsyncMock(
        return_value=(mock_wallet_rec, mock_tenant_rec)
    )
    mock_context.inject.return_value = mock_tenant_mgr_instance  # Configure injector

    # Mock DIDXManager
    mock_didx_mgr_instance = MockDIDXManager.return_value
    mock_didx_result = {"connection_id": "new-conn-id"}
    mock_didx_mgr_instance.create_request_implicit = AsyncMock(
        return_value=mock_didx_result
    )

    result = await endorser_service.connect_with_endorser(profile, mock_context)

    assert result == mock_didx_result
    endorser_service.endorser_info.assert_called_once_with(profile)
    endorser_service.endorser_connection.assert_awaited_once_with(profile)
    profile.settings.get.assert_called_once_with("wallet.id")
    mock_context.inject.assert_called_once_with(MockTenantManager)
    mock_tenant_mgr_instance.get_wallet_and_tenant.assert_awaited_once_with(
        TEST_TENANT_WALLET_ID
    )
    MockDIDXManager.assert_called_once_with(profile)
    mock_didx_mgr_instance.create_request_implicit.assert_awaited_once_with(
        their_public_did=TEST_ENDORSER_DID,
        alias=TEST_ENDORSER_ALIAS,
        my_label=TEST_TENANT_NAME,  # Tenant name should be preferred
    )


# --- Test Cases for Global Functions ---


def test_subscribe(endorser_service: EndorserConnectionService):
    """Test the subscribe function."""
    mock_bus = MagicMock(spec=EventBus)
    test_module.subscribe(mock_bus)
    mock_bus.subscribe.assert_called_once_with(
        CONNECTIONS_EVENT_PATTERN, connections_event_handler
    )


@pytest.mark.asyncio
@patch.object(test_module.ConnRecord, "deserialize")
@patch.object(test_module.ConnRecord, "retrieve_by_id", new_callable=AsyncMock)
@patch(
    "traction_innkeeper.v1_0.endorser.endorser_connection_service.TransactionManager",
    autospec=True,
)
async def test_connections_event_handler_metadata_needs_setting(
    MockTransactionManager: MagicMock,
    mock_retrieve_by_id: AsyncMock,
    mock_deserialize: MagicMock,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_event: MagicMock,
    mock_conn_record: AsyncMock,  # The record deserialized from event
):
    """Test event handler when connection is completed and needs metadata."""
    profile, session = mock_profile

    # Configure settings for alias and DID
    def get_setting(key):
        if key == "endorser.endorser_alias":
            return TEST_ENDORSER_ALIAS
        if key == "endorser.endorser_public_did":
            return TEST_ENDORSER_DID
        return None

    profile.settings.get.side_effect = get_setting

    # Configure deserialized record
    mock_deserialize.return_value = mock_conn_record
    mock_conn_record.alias = TEST_ENDORSER_ALIAS  # Ensure alias matches
    mock_conn_record.state = ConnRecord.State.COMPLETED  # Ensure state is completed

    # Simulate metadata missing transaction_my_job
    mock_conn_record.metadata_get_all.return_value = {"some": "other_data"}

    # Mock TransactionManager
    mock_tx_mgr_instance = MockTransactionManager.return_value
    mock_tx_mgr_instance.set_transaction_my_job = AsyncMock(return_value="tx_job_info")

    # Mock ConnRecord.retrieve_by_id to return a record for metadata setting
    # Important: This should be a *different* mock instance if we want to check
    # methods called on *it* vs the one from deserialize.
    mock_retrieved_conn_rec = AsyncMock(spec=ConnRecord)
    mock_retrieve_by_id.return_value = mock_retrieved_conn_rec

    await connections_event_handler(profile, mock_event)

    # Assertions
    profile.settings.get.assert_any_call("endorser.endorser_alias")
    mock_deserialize.assert_called_once_with(mock_event.payload)
    profile.session.assert_has_calls(
        [call(), call()]
    )  # Called twice: once for get_all, once for set
    mock_conn_record.metadata_get_all.assert_awaited_once_with(session)

    # Check transaction manager calls
    MockTransactionManager.assert_called_once_with(profile)
    mock_tx_mgr_instance.set_transaction_my_job.assert_awaited_once_with(
        record=mock_conn_record, transaction_my_job="TRANSACTION_AUTHOR"
    )

    # Check metadata setting calls on the *retrieved* record
    mock_retrieve_by_id.assert_awaited_once_with(
        session, mock_conn_record.connection_id
    )
    mock_retrieved_conn_rec.metadata_get.assert_awaited_with(session, "endorser_info")
    mock_retrieved_conn_rec.metadata_set.assert_awaited_once_with(
        session,
        key="endorser_info",
        value={"endorser_did": TEST_ENDORSER_DID, "endorser_name": TEST_ENDORSER_ALIAS},
    )


@pytest.mark.asyncio
@patch.object(test_module.ConnRecord, "deserialize")
async def test_connections_event_handler_alias_mismatch(
    mock_deserialize: MagicMock,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_event: MagicMock,
    mock_conn_record: AsyncMock,
):
    """Test event handler when the connection alias doesn't match."""
    profile, _ = mock_profile
    profile.settings.get.return_value = "DifferentAlias"  # Endorser alias setting
    mock_deserialize.return_value = mock_conn_record
    mock_conn_record.alias = TEST_ENDORSER_ALIAS  # Record has different alias

    await connections_event_handler(profile, mock_event)

    profile.settings.get.assert_called_once_with("endorser.endorser_alias")
    mock_deserialize.assert_called_once_with(mock_event.payload)
    profile.session.assert_not_called()  # Should exit early


@pytest.mark.asyncio
@patch.object(test_module.ConnRecord, "deserialize")
async def test_connections_event_handler_state_not_completed(
    mock_deserialize: MagicMock,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_event: MagicMock,
    mock_conn_record: AsyncMock,
):
    """Test event handler when connection state is not completed."""
    profile, _ = mock_profile
    profile.settings.get.return_value = TEST_ENDORSER_ALIAS  # Alias matches
    mock_deserialize.return_value = mock_conn_record
    mock_conn_record.alias = TEST_ENDORSER_ALIAS
    mock_conn_record.state = ConnRecord.State.REQUEST  # State is not completed

    await connections_event_handler(profile, mock_event)

    profile.settings.get.assert_called_once_with("endorser.endorser_alias")
    mock_deserialize.assert_called_once_with(mock_event.payload)
    profile.session.assert_not_called()  # Should exit before checking metadata


@pytest.mark.asyncio
@patch.object(test_module.ConnRecord, "deserialize")
async def test_connections_event_handler_metadata_exists(
    mock_deserialize: MagicMock,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_event: MagicMock,
    mock_conn_record: AsyncMock,
):
    """Test event handler when metadata indicating author role already exists."""
    profile, session = mock_profile
    profile.settings.get.return_value = TEST_ENDORSER_ALIAS  # Alias matches
    mock_deserialize.return_value = mock_conn_record
    mock_conn_record.alias = TEST_ENDORSER_ALIAS
    mock_conn_record.state = ConnRecord.State.COMPLETED  # State is completed

    # Simulate metadata *already* having the job set
    mock_conn_record.metadata_get_all.return_value = {
        "transaction-jobs": {"transaction_my_job": "TRANSACTION_AUTHOR"}
    }

    await connections_event_handler(profile, mock_event)

    profile.settings.get.assert_called_once_with("endorser.endorser_alias")
    mock_deserialize.assert_called_once_with(mock_event.payload)
    profile.session.assert_called_once()  # Only called once for metadata_get_all
    mock_conn_record.metadata_get_all.assert_awaited_once_with(session)
    # Ensure setting logic was not called
    mock_conn_record.metadata_set.assert_not_called()
