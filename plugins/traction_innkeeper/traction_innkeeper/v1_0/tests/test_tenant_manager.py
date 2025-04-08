import logging
from unittest.mock import MagicMock, AsyncMock, patch
import pytest

# Assuming tenant_manager.py is in ../innkeeper relative to this test file
from traction_innkeeper.v1_0.innkeeper.tenant_manager import TenantManager

# Import classes that need mocking or inspection
from traction_innkeeper.v1_0.innkeeper.models import (
    TenantRecord,
)  # noqa F401 mocked
from traction_innkeeper.v1_0.innkeeper.config import (
    TractionInnkeeperConfig,
    InnkeeperWalletConfig,
    ReservationConfig,
)
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import (
    StorageNotFoundError,
)  # noqa F401 used in tests
from acapy_agent.wallet.models.wallet_record import WalletRecord
from acapy_agent.multitenant.base import BaseMultitenantManager


# Disable logging noise during tests
logging.disable(logging.CRITICAL)


# --- Mock Configuration ---
@pytest.fixture
def mock_innkeeper_wallet_config():
    """Mock InnkeeperWalletConfig."""
    config = MagicMock(spec=InnkeeperWalletConfig)
    config.tenant_id = "innkeeper_tenant_id"
    config.wallet_name = "InnkeeperWallet"
    config.wallet_key = "innkeeper_key"
    config.connect_to_endorser = []  # Example: Mock endorsement config if needed
    config.create_public_did = []  # Example: Mock public DID config if needed
    config.print_key = False
    config.print_token = False
    config.enable_ledger_switch = False
    return config


@pytest.fixture
def mock_reservation_config():
    """Mock ReservationConfig."""
    config = MagicMock(spec=ReservationConfig)
    config.auto_issuer = False
    return config


@pytest.fixture
def mock_traction_config(mock_innkeeper_wallet_config, mock_reservation_config):
    """Mock TractionInnkeeperConfig."""
    config = MagicMock(spec=TractionInnkeeperConfig)
    config.innkeeper_wallet = mock_innkeeper_wallet_config
    config.reservation = mock_reservation_config
    return config


# --- Base Fixtures ---
@pytest.fixture
def mock_profile():
    """Provides a mocked Profile with a working async session manager and context."""
    profile = MagicMock(spec=Profile)
    mock_session = AsyncMock()
    profile.session = MagicMock()
    profile.session.return_value.__aenter__.return_value = mock_session
    profile.session.return_value.__aexit__.return_value = None
    # Mock context and settings needed by create_wallet
    profile.context = MagicMock()
    profile.context.settings = {"wallet.type": "askar"}
    # Mock inject for BaseMultitenantManager
    profile.inject = MagicMock()
    return profile, mock_session


@pytest.fixture
def mock_multitenant_mgr():
    """Provides a mocked BaseMultitenantManager."""
    mgr = AsyncMock(spec=BaseMultitenantManager)
    return mgr


@pytest.fixture
def tenant_manager(mock_profile, mock_traction_config, mock_multitenant_mgr):
    """Provides a TenantManager instance with mocked profile and config."""
    root_profile, _ = mock_profile
    # Configure profile.inject to return the mock manager
    root_profile.inject.return_value = mock_multitenant_mgr
    return TenantManager(root_profile, mock_traction_config)


# --- Test Cases ---


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord", autospec=True)
@patch("traction_innkeeper.v1_0.innkeeper.tenant_manager.TenantRecord", autospec=True)
async def test_create_tenant_success(
    MockTenantRecord: MagicMock,
    MockWalletRecord: MagicMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test creating a tenant record successfully when wallet exists."""
    profile, session = mock_profile
    wallet_id = "test-wallet-id"
    tenant_email = "test@example.com"
    tenant_id = "test-tenant-id"
    wallet_name = "MyWalletName"

    # Setup mock WalletRecord retrieve
    mock_wallet_rec_instance = MagicMock(spec=WalletRecord)
    mock_wallet_rec_instance.wallet_id = wallet_id
    mock_wallet_rec_instance.wallet_name = "actual_wallet_name"  # Underlying name
    mock_wallet_rec_instance.settings = {
        "default_label": wallet_name
    }  # Label used for tenant_name
    MockWalletRecord.retrieve_by_id = AsyncMock(return_value=mock_wallet_rec_instance)

    # Setup mock TenantRecord instance methods (save, query)
    mock_tenant_rec_instance = AsyncMock(spec=TenantRecord)
    # Make the MockTenantRecord class return our instance when called
    MockTenantRecord.return_value = mock_tenant_rec_instance

    result_tenant = await tenant_manager.create_tenant(
        wallet_id=wallet_id,
        email=tenant_email,
        tenant_id=tenant_id,
        # Provide other optional args if needed for the test case
    )

    # Assertions
    MockWalletRecord.retrieve_by_id.assert_awaited_once_with(session, wallet_id)
    MockTenantRecord.assert_called_once_with(
        tenant_id=tenant_id,
        tenant_name=wallet_name,  # Should use default_label from settings
        contact_email=tenant_email,
        wallet_id=wallet_id,
        new_with_id=True,
        connected_to_endorsers=[],  # Default if not passed
        created_public_did=[],  # Default if not passed
        enable_ledger_switch=False,  # Default if not passed
        auto_issuer=False,  # Default if not passed
    )
    mock_tenant_rec_instance.save.assert_awaited_once_with(session, reason="New tenant")
    mock_tenant_rec_instance.query.assert_awaited_once_with(
        session
    )  # Query is called after save
    assert result_tenant == mock_tenant_rec_instance


@pytest.mark.asyncio
async def test_create_tenant_wallet_not_found(
    tenant_manager: TenantManager, mock_profile
):
    """Test create_tenant failure when wallet is not found."""
    profile, session = mock_profile
    wallet_id = "non-existent-wallet-id"

    # Setup mock WalletRecord retrieve to raise error
    with patch(
        "traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord.retrieve_by_id",
        AsyncMock(side_effect=StorageNotFoundError("Not Found")),
    ):
        with pytest.raises(StorageNotFoundError):
            await tenant_manager.create_tenant(
                wallet_id=wallet_id, email="test@fail.com"
            )


@pytest.mark.asyncio
@patch.object(TenantManager, "get_unique_wallet_name", new_callable=AsyncMock)
@patch.object(TenantManager, "get_token", new_callable=AsyncMock)
@patch.object(TenantManager, "create_tenant", new_callable=AsyncMock)
async def test_create_wallet_success(
    mock_create_tenant: AsyncMock,
    mock_get_token: AsyncMock,
    mock_get_unique_wallet_name: AsyncMock,
    tenant_manager: TenantManager,
    mock_multitenant_mgr: MagicMock,  # Get the injected mock directly
    mock_profile,
    mock_traction_config,  # Ensure config is available
):
    """Test the full create_wallet flow successfully."""
    profile, _ = mock_profile  # We don't need the session directly here
    wallet_name = "Test Wallet"
    wallet_key = "test_key"
    tenant_email = "tenant@test.com"
    unique_wallet_name = "Test-Wallet-Unique"
    tenant_id = "new-tenant-id"
    mock_token = "mock_auth_token"

    # Setup mock return values
    mock_get_unique_wallet_name.return_value = unique_wallet_name
    mock_wallet_record = MagicMock(
        spec=WalletRecord, wallet_id="new-wallet-id", wallet_name=unique_wallet_name
    )
    mock_multitenant_mgr.create_wallet = AsyncMock(return_value=mock_wallet_record)
    mock_get_token.return_value = mock_token
    mock_tenant_record = MagicMock(spec=TenantRecord, tenant_id=tenant_id)
    mock_create_tenant.return_value = mock_tenant_record

    # Call the method
    result_tenant, result_wallet, result_token = await tenant_manager.create_wallet(
        wallet_name=wallet_name,
        wallet_key=wallet_key,
        tenant_email=tenant_email,
        tenant_id=tenant_id,
        extra_settings={},  # Add settings if needed for test case
    )

    # Assertions
    mock_get_unique_wallet_name.assert_awaited_once_with(wallet_name)
    profile.inject.assert_called_once_with(BaseMultitenantManager)
    # Check call to multitenant_mgr.create_wallet (complex dict check)
    mock_multitenant_mgr.create_wallet.assert_awaited_once()
    call_args, call_kwargs = mock_multitenant_mgr.create_wallet.call_args
    assert call_args[0] == {  # settings dict
        "wallet.type": "askar",  # From mock_profile context
        "wallet.name": unique_wallet_name,  # The unique name
        "wallet.key": wallet_key,
        "wallet.webhook_urls": [],  # Default
        "wallet.dispatch_type": "base",  # Default
        "default_label": wallet_name,  # Original name used as label
    }
    assert call_args[1] == WalletRecord.MODE_MANAGED  # key_management_mode

    mock_get_token.assert_awaited_once_with(mock_wallet_record, wallet_key)

    # Check call to create_tenant (verify defaults from config are handled)
    expected_connect_endorser = (
        mock_traction_config.innkeeper_wallet.connect_to_endorser
    )
    expected_public_did = mock_traction_config.innkeeper_wallet.create_public_did
    expected_auto_issuer = mock_traction_config.reservation.auto_issuer
    expected_ledger_switch = mock_traction_config.innkeeper_wallet.enable_ledger_switch

    mock_create_tenant.assert_awaited_once_with(
        wallet_id=mock_wallet_record.wallet_id,
        email=tenant_email,
        tenant_id=tenant_id,
        connected_to_endorsers=expected_connect_endorser,
        created_public_did=expected_public_did,
        auto_issuer=expected_auto_issuer,
        enable_ledger_switch=expected_ledger_switch,
    )

    assert result_tenant == mock_tenant_record
    assert result_wallet == mock_wallet_record
    assert result_token == mock_token


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.TenantRecord.query_by_wallet_id",
    new_callable=AsyncMock,
)
async def test_get_wallet_and_tenant_success(
    mock_query_by_wallet_id: AsyncMock,
    mock_retrieve_by_id: AsyncMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test successfully retrieving wallet and tenant records."""
    profile, session = mock_profile
    wallet_id = "existing-wallet-id"

    # Setup mock return values
    mock_wallet_rec = MagicMock(spec=WalletRecord, wallet_id=wallet_id)
    mock_tenant_rec = MagicMock(spec=TenantRecord, wallet_id=wallet_id)
    mock_retrieve_by_id.return_value = mock_wallet_rec
    mock_query_by_wallet_id.return_value = mock_tenant_rec

    # Call the method
    result_wallet, result_tenant = await tenant_manager.get_wallet_and_tenant(wallet_id)

    # Assertions
    mock_retrieve_by_id.assert_awaited_once_with(session, wallet_id)
    mock_query_by_wallet_id.assert_awaited_once_with(session, wallet_id)
    assert result_wallet == mock_wallet_rec
    assert result_tenant == mock_tenant_rec


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.TenantRecord.query_by_wallet_id",
    new_callable=AsyncMock,
)
async def test_get_wallet_and_tenant_wallet_not_found(
    mock_query_by_wallet_id: AsyncMock,
    mock_retrieve_by_id: AsyncMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test get_wallet_and_tenant when WalletRecord is not found."""
    profile, session = mock_profile
    wallet_id = "non-existent-wallet-id"

    # Setup mock retrieve_by_id to raise StorageNotFoundError
    mock_retrieve_by_id.side_effect = StorageNotFoundError("Wallet not found")

    # Call and assert exception
    with pytest.raises(StorageNotFoundError, match="Tenant not found with wallet_id"):
        await tenant_manager.get_wallet_and_tenant(wallet_id)

    # Assertions
    mock_retrieve_by_id.assert_awaited_once_with(session, wallet_id)
    # query_by_wallet_id should not be called if retrieve_by_id fails first
    mock_query_by_wallet_id.assert_not_awaited()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.TenantRecord.query_by_wallet_id",
    new_callable=AsyncMock,
)
async def test_get_wallet_and_tenant_tenant_not_found(
    mock_query_by_wallet_id: AsyncMock,
    mock_retrieve_by_id: AsyncMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test get_wallet_and_tenant when TenantRecord is not found (wallet exists)."""
    profile, session = mock_profile
    wallet_id = "wallet-exists-tenant-doesnt"

    # Setup mocks: WalletRecord found, TenantRecord not found (returns None or empty list typically)
    mock_wallet_rec = MagicMock(spec=WalletRecord, wallet_id=wallet_id)
    mock_retrieve_by_id.return_value = mock_wallet_rec
    mock_query_by_wallet_id.return_value = None  # Simulate tenant not found

    # Call the method - should still return wallet, but tenant is None
    result_wallet, result_tenant = await tenant_manager.get_wallet_and_tenant(wallet_id)

    # Assertions
    mock_retrieve_by_id.assert_awaited_once_with(session, wallet_id)
    mock_query_by_wallet_id.assert_awaited_once_with(session, wallet_id)
    assert result_wallet == mock_wallet_rec
    assert result_tenant is None  # Expect None when tenant query returns nothing
