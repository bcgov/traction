import logging
from unittest.mock import MagicMock, AsyncMock, patch, call
import pytest

# Assuming tenant_manager.py is in ../innkeeper relative to this test file
from traction_innkeeper.v1_0.innkeeper.tenant_manager import TenantManager

# Import classes that need mocking or inspection
from traction_innkeeper.v1_0.innkeeper.models import (
    TenantRecord,
    ReservationRecord,
    TenantAuthenticationApiRecord,
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


@pytest.fixture
def mock_bcrypt(mocker):
    """Mocks bcrypt functions."""
    # Use mocker fixture provided by pytest-mock
    mocked_bcrypt = mocker.patch(
        "traction_innkeeper.v1_0.innkeeper.tenant_manager.bcrypt", autospec=True
    )
    return mocked_bcrypt


@pytest.fixture
def mock_tenant_rec():
    """Mocks bcrypt functions."""
    # Use mocker fixture provided by pytest-mock
    mock_tenant_rec = MagicMock(spec=TenantRecord)
    mock_tenant_rec.wallet_id = "existing_wallet_id"
    mock_tenant_rec.tenant_name = "test_tenant"
    mock_tenant_rec.connected_to_endorsers = True
    mock_tenant_rec.tenant_id = None
    mock_tenant_rec.wallet_name = None
    mock_tenant_rec.connected_to_endorsers = None
    mock_tenant_rec.created_public_did = None
    mock_tenant_rec.auto_issuer = None
    mock_tenant_rec.enable_ledger_switch = None
    return mock_tenant_rec


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


@pytest.mark.asyncio
async def test_get_token_success(
    tenant_manager: TenantManager,
    mock_multitenant_mgr: AsyncMock,
):
    """Test get_token successfully retrieves a token."""
    mock_wallet_record = MagicMock(spec=WalletRecord, wallet_name="test-wallet")
    wallet_key = "test_key"
    expected_token = "mock_auth_token_123"
    mock_multitenant_mgr.create_auth_token = AsyncMock(return_value=expected_token)

    token = await tenant_manager.get_token(mock_wallet_record, wallet_key)

    assert token == expected_token
    mock_multitenant_mgr.create_auth_token.assert_awaited_once_with(
        mock_wallet_record, wallet_key
    )


@pytest.mark.asyncio
async def test_get_token_failure(
    tenant_manager: TenantManager,
    mock_multitenant_mgr: AsyncMock,
):
    """Test get_token handles BaseError during token creation."""
    from acapy_agent.core.error import BaseError  # Import locally if needed

    mock_wallet_record = MagicMock(spec=WalletRecord, wallet_name="test-wallet")
    wallet_key = "test_key"
    mock_multitenant_mgr.create_auth_token = AsyncMock(
        side_effect=BaseError("Token generation failed")
    )

    with pytest.raises(BaseError, match="Token generation failed"):
        await tenant_manager.get_token(mock_wallet_record, wallet_key)

    mock_multitenant_mgr.create_auth_token.assert_awaited_once_with(
        mock_wallet_record, wallet_key
    )


# --- Tests for check_tables_for_wallet_name ---


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord.query",
    new_callable=AsyncMock,
)
async def test_check_tables_for_wallet_name_exists(
    mock_wallet_query: AsyncMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test check_tables_for_wallet_name when wallet exists."""
    profile, session = mock_profile
    wallet_name = "existing-wallet"
    mock_wallet_query.return_value = [MagicMock()]  # Return a list with one item

    exists = await tenant_manager.check_tables_for_wallet_name(session, wallet_name)

    assert exists is True
    mock_wallet_query.assert_awaited_once_with(session, {"wallet_name": wallet_name})


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord.query",
    new_callable=AsyncMock,
)
async def test_check_tables_for_wallet_name_not_exists(
    mock_wallet_query: AsyncMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test check_tables_for_wallet_name when wallet does not exist."""
    profile, session = mock_profile
    wallet_name = "new-wallet"
    mock_wallet_query.return_value = []  # Return an empty list

    exists = await tenant_manager.check_tables_for_wallet_name(session, wallet_name)

    assert exists is False
    mock_wallet_query.assert_awaited_once_with(session, {"wallet_name": wallet_name})


# --- Tests for get_unique_wallet_name ---


@pytest.mark.asyncio
@patch.object(TenantManager, "check_tables_for_wallet_name", new_callable=AsyncMock)
async def test_get_unique_wallet_name_already_unique(
    mock_check_tables: AsyncMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test get_unique_wallet_name when the name is already unique."""
    profile, session = mock_profile
    wallet_name = "unique-wallet"
    mock_check_tables.return_value = False  # Name is unique

    unique_name = await tenant_manager.get_unique_wallet_name(wallet_name)

    assert unique_name == wallet_name
    mock_check_tables.assert_awaited_once_with(session, wallet_name)


@pytest.mark.asyncio
@patch.object(TenantManager, "check_tables_for_wallet_name", new_callable=AsyncMock)
async def test_get_unique_wallet_name_needs_one_suffix(
    mock_check_tables: AsyncMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test get_unique_wallet_name when one suffix is needed."""
    profile, session = mock_profile
    wallet_name = "taken-wallet"
    # Simulate: 'taken-wallet' exists, 'taken-wallet-1' does not
    mock_check_tables.side_effect = [True, False]

    unique_name = await tenant_manager.get_unique_wallet_name(wallet_name)

    assert unique_name == f"{wallet_name}-1"
    assert mock_check_tables.await_count == 2
    mock_check_tables.assert_has_awaits(
        [
            call(session, wallet_name),
            call(session, f"{wallet_name}-1"),
        ]
    )


@pytest.mark.asyncio
@patch.object(TenantManager, "check_tables_for_wallet_name", new_callable=AsyncMock)
async def test_get_unique_wallet_name_needs_multiple_suffixes(
    mock_check_tables: AsyncMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test get_unique_wallet_name when multiple suffixes are needed."""
    profile, session = mock_profile
    wallet_name = "very-taken-wallet"
    # Simulate: 'very-taken-wallet' exists, 'very-taken-wallet-1' exists, 'very-taken-wallet-1-2' does not
    mock_check_tables.side_effect = [True, True, False]

    unique_name = await tenant_manager.get_unique_wallet_name(wallet_name)

    # Note: The loop logic adds '-1', then '-1-2', etc.
    assert unique_name == f"{wallet_name}-1-2"
    assert mock_check_tables.await_count == 3
    mock_check_tables.assert_has_awaits(
        [
            call(session, wallet_name),
            call(session, f"{wallet_name}-1"),
            call(session, f"{wallet_name}-1-2"),
        ]
    )


# --- Tests for check_reservation_password ---


def test_check_reservation_password_null_input(
    tenant_manager: TenantManager, mock_bcrypt
):
    """Test check_reservation_password with null inputs."""
    mock_reservation = MagicMock(spec=ReservationRecord)
    assert tenant_manager.check_reservation_password(None, mock_reservation) is None
    assert tenant_manager.check_reservation_password("pwd", None) is None
    mock_bcrypt.hashpw.assert_not_called()
    mock_bcrypt.checkpw.assert_not_called()


def test_check_reservation_password_correct(tenant_manager: TenantManager, mock_bcrypt):
    """Test check_reservation_password with correct password."""
    pwd = "correct_password"
    salt = b"salt_value"
    hash_val = b"hashed_password_value"
    mock_reservation = MagicMock(
        spec=ReservationRecord,
        reservation_token_salt=salt.decode(),
        reservation_token_hash=hash_val.decode(),
    )
    # Make hashpw return something deterministic based on input pwd and salt
    mock_bcrypt.hashpw.return_value = hash_val
    # Make checkpw return True (indicating match)
    mock_bcrypt.checkpw.return_value = True

    # Expected token is the *re-hashed* password using the salt
    expected_token = hash_val.decode()
    result_token = tenant_manager.check_reservation_password(pwd, mock_reservation)

    assert result_token == expected_token
    mock_bcrypt.hashpw.assert_called_once_with(pwd.encode("utf-8"), salt)
    # checkpw is called twice in the function
    assert mock_bcrypt.checkpw.call_count == 2
    mock_bcrypt.checkpw.assert_has_calls(
        [
            call(pwd.encode("utf-8"), hash_val),  # Check against re-hashed
            call(pwd.encode("utf-8"), hash_val),  # Check against stored hash
        ]
    )


def test_check_reservation_password_incorrect(
    tenant_manager: TenantManager, mock_bcrypt
):
    """Test check_reservation_password with incorrect password."""
    pwd = "wrong_password"
    salt = b"salt_value"
    correct_hash = b"correct_hashed_password"
    wrong_hash = b"wrong_hashed_password"  # What hashpw returns for wrong pwd
    mock_reservation = MagicMock(
        spec=ReservationRecord,
        reservation_token_salt=salt.decode(),
        reservation_token_hash=correct_hash.decode(),
    )
    mock_bcrypt.hashpw.return_value = wrong_hash
    # Simulate checkpw failing on one or both checks
    mock_bcrypt.checkpw.side_effect = [False, False]  # Fails both checks

    result_token = tenant_manager.check_reservation_password(pwd, mock_reservation)

    assert result_token is None
    mock_bcrypt.hashpw.assert_called_once_with(pwd.encode("utf-8"), salt)
    assert mock_bcrypt.checkpw.call_count == 2
    mock_bcrypt.checkpw.assert_has_calls(
        [
            call(pwd.encode("utf-8"), wrong_hash),  # Check against re-hashed (fails)
            call(
                pwd.encode("utf-8"), correct_hash
            ),  # Check against stored hash (fails)
        ]
    )


# --- Tests for check_api_key --- (Similar structure to password check)


def test_check_api_key_null_input(tenant_manager: TenantManager, mock_bcrypt):
    """Test check_api_key with null inputs."""
    mock_api_rec = MagicMock(spec=TenantAuthenticationApiRecord)
    assert tenant_manager.check_api_key(None, mock_api_rec) is None
    assert tenant_manager.check_api_key("key", None) is None
    mock_bcrypt.hashpw.assert_not_called()
    mock_bcrypt.checkpw.assert_not_called()


def test_check_api_key_correct(tenant_manager: TenantManager, mock_bcrypt):
    """Test check_api_key with correct API key."""
    api_key = "correct_api_key"
    salt = b"api_salt_value"
    hash_val = b"hashed_api_key_value"
    mock_api_rec = MagicMock(
        spec=TenantAuthenticationApiRecord,
        api_key_token_salt=salt.decode(),
        api_key_token_hash=hash_val.decode(),
    )
    mock_bcrypt.hashpw.return_value = hash_val
    mock_bcrypt.checkpw.return_value = True

    expected_token = hash_val.decode()
    result_token = tenant_manager.check_api_key(api_key, mock_api_rec)

    assert result_token == expected_token
    mock_bcrypt.hashpw.assert_called_once_with(api_key.encode("utf-8"), salt)
    assert mock_bcrypt.checkpw.call_count == 2


def test_check_api_key_incorrect(tenant_manager: TenantManager, mock_bcrypt):
    """Test check_api_key with incorrect API key."""
    api_key = "wrong_api_key"
    salt = b"api_salt_value"
    correct_hash = b"correct_hashed_api_key"
    wrong_hash = b"wrong_hashed_api_key"
    mock_api_rec = MagicMock(
        spec=TenantAuthenticationApiRecord,
        api_key_token_salt=salt.decode(),
        api_key_token_hash=correct_hash.decode(),
    )
    mock_bcrypt.hashpw.return_value = wrong_hash
    mock_bcrypt.checkpw.side_effect = [False, False]

    result_token = tenant_manager.check_api_key(api_key, mock_api_rec)

    assert result_token is None
    mock_bcrypt.hashpw.assert_called_once_with(api_key.encode("utf-8"), salt)
    assert mock_bcrypt.checkpw.call_count == 2


# --- Tests for create_wallet Error Paths and Options ---


@pytest.mark.asyncio
@patch.object(TenantManager, "get_unique_wallet_name", new_callable=AsyncMock)
async def test_create_wallet_multitenant_error(
    mock_get_unique_wallet_name: AsyncMock,
    tenant_manager: TenantManager,
    mock_multitenant_mgr: AsyncMock,
    mock_profile,
):
    """Test create_wallet failure during multitenant.create_wallet."""
    from acapy_agent.core.error import BaseError  # Import locally if needed

    profile, _ = mock_profile
    unique_wallet_name = "UniqueName"
    mock_get_unique_wallet_name.return_value = unique_wallet_name
    mock_multitenant_mgr.create_wallet = AsyncMock(
        side_effect=BaseError("Wallet creation failed")
    )

    with pytest.raises(BaseError, match="Wallet creation failed"):
        await tenant_manager.create_wallet(
            wallet_name="Test Wallet",
            wallet_key="key",
            tenant_email="email@test.com",
        )

    mock_get_unique_wallet_name.assert_awaited_once_with("Test Wallet")
    mock_multitenant_mgr.create_wallet.assert_awaited_once()


@pytest.mark.asyncio
@patch.object(TenantManager, "get_unique_wallet_name", new_callable=AsyncMock)
@patch.object(TenantManager, "get_token", new_callable=AsyncMock)
@patch.object(TenantManager, "create_tenant", new_callable=AsyncMock)
async def test_create_wallet_get_token_error(
    mock_create_tenant: AsyncMock,
    mock_get_token: AsyncMock,
    mock_get_unique_wallet_name: AsyncMock,
    tenant_manager: TenantManager,
    mock_multitenant_mgr: AsyncMock,
    mock_profile,
):
    """Test create_wallet failure during get_token."""
    from acapy_agent.core.error import BaseError  # Import locally if needed

    profile, _ = mock_profile
    unique_wallet_name = "UniqueName"
    mock_get_unique_wallet_name.return_value = unique_wallet_name
    mock_wallet_record = MagicMock(spec=WalletRecord)
    mock_multitenant_mgr.create_wallet = AsyncMock(return_value=mock_wallet_record)
    mock_get_token.side_effect = BaseError("Get token failed")

    with pytest.raises(BaseError, match="Get token failed"):
        await tenant_manager.create_wallet(
            wallet_name="Test Wallet",
            wallet_key="key",
            tenant_email="email@test.com",
        )

    mock_get_unique_wallet_name.assert_awaited_once()
    mock_multitenant_mgr.create_wallet.assert_awaited_once()
    mock_get_token.assert_awaited_once()
    mock_create_tenant.assert_not_awaited()  # Should fail before creating tenant


@pytest.mark.asyncio
@patch.object(TenantManager, "get_unique_wallet_name", new_callable=AsyncMock)
@patch.object(TenantManager, "get_token", new_callable=AsyncMock)
@patch.object(TenantManager, "create_tenant", new_callable=AsyncMock)
async def test_create_wallet_with_extra_settings(
    mock_create_tenant: AsyncMock,
    mock_get_token: AsyncMock,
    mock_get_unique_wallet_name: AsyncMock,
    tenant_manager: TenantManager,
    mock_multitenant_mgr: AsyncMock,
    mock_profile,
):
    """Test create_wallet successfully handles extra_settings override."""
    profile, _ = mock_profile
    wallet_name = "Test Wallet"
    wallet_key = "test_key"
    tenant_email = "tenant@test.com"
    unique_wallet_name = "Test-Wallet-Unique"
    mock_token = "mock_auth_token"
    tenant_id = "extra-settings-tenant-id"

    # Custom settings to override config
    extra_connect_endorser = [{"endpoint": "http://extra.endorser"}]
    extra_public_did = [{"did": "did:sov:extra123"}]
    extra_auto_issuer = True  # Override config default (False)
    extra_ledger_switch = True  # Override config default (False)
    extra_wallet_setting = {"custom_key": "custom_value"}

    extra_settings = {
        "tenant.endorser_config": extra_connect_endorser,
        "tenant.public_did_config": extra_public_did,
        "tenant.auto_issuer": extra_auto_issuer,
        "tenant.enable_ledger_switch": extra_ledger_switch,
        **extra_wallet_setting,
    }

    # Setup mocks
    mock_get_unique_wallet_name.return_value = unique_wallet_name
    mock_wallet_record = MagicMock(spec=WalletRecord, wallet_id="new-wallet-id")
    mock_multitenant_mgr.create_wallet = AsyncMock(return_value=mock_wallet_record)
    mock_get_token.return_value = mock_token
    mock_tenant_record = MagicMock(spec=TenantRecord, tenant_id=tenant_id)
    mock_create_tenant.return_value = mock_tenant_record

    await tenant_manager.create_wallet(
        wallet_name=wallet_name,
        wallet_key=wallet_key,
        tenant_email=tenant_email,
        extra_settings=extra_settings,
        tenant_id=tenant_id,
    )

    # Assert multitenant_mgr.create_wallet received extra wallet settings
    mock_multitenant_mgr.create_wallet.assert_awaited_once()
    call_args, _ = mock_multitenant_mgr.create_wallet.call_args
    passed_settings = call_args[0]
    assert passed_settings["custom_key"] == "custom_value"

    # Assert create_tenant received overridden values
    mock_create_tenant.assert_awaited_once_with(
        wallet_id=mock_wallet_record.wallet_id,
        email=tenant_email,
        tenant_id=tenant_id,
        connected_to_endorsers=extra_connect_endorser,  # Overridden
        created_public_did=extra_public_did,  # Overridden
        auto_issuer=extra_auto_issuer,  # Overridden
        enable_ledger_switch=extra_ledger_switch,  # Overridden
    )


# --- Tests for create_tenant Edge Cases ---


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord", autospec=True)
@patch("traction_innkeeper.v1_0.innkeeper.tenant_manager.TenantRecord", autospec=True)
async def test_create_tenant_label_fallback(
    MockTenantRecord: MagicMock,
    MockWalletRecord: MagicMock,
    tenant_manager: TenantManager,
    mock_profile,
):
    """Test create_tenant uses wallet_name if default_label is missing."""
    profile, session = mock_profile
    wallet_id = "test-wallet-id"
    tenant_email = "test@example.com"
    wallet_name = "ActualWalletName"  # The underlying name

    # Setup mock WalletRecord without default_label in settings
    mock_wallet_rec_instance = MagicMock(spec=WalletRecord)
    mock_wallet_rec_instance.wallet_id = wallet_id
    mock_wallet_rec_instance.wallet_name = wallet_name
    mock_wallet_rec_instance.settings = {}  # Empty settings, no default_label
    MockWalletRecord.retrieve_by_id = AsyncMock(return_value=mock_wallet_rec_instance)

    mock_tenant_rec_instance = AsyncMock(spec=TenantRecord)
    MockTenantRecord.return_value = mock_tenant_rec_instance

    await tenant_manager.create_tenant(
        wallet_id=wallet_id,
        email=tenant_email,
    )

    # Assert TenantRecord called with wallet_name as tenant_name
    MockTenantRecord.assert_called_once_with(
        tenant_id=None,  # Default
        tenant_name=wallet_name,  # <<< Should fallback to wallet_name
        contact_email=tenant_email,
        wallet_id=wallet_id,
        new_with_id=False,
        connected_to_endorsers=[],
        created_public_did=[],
        enable_ledger_switch=False,
        auto_issuer=False,
    )
    mock_tenant_rec_instance.save.assert_awaited_once()


# --- Tests for create_innkeeper ---


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.TenantRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
@patch.object(TenantManager, "get_token", new_callable=AsyncMock)
@patch.object(TenantManager, "create_wallet", new_callable=AsyncMock)
@patch("builtins.print")  # Mock print to avoid polluting test output
async def test_create_innkeeper_exists(
    mock_print: MagicMock,
    mock_create_wallet: AsyncMock,
    mock_get_token: AsyncMock,
    mock_wallet_retrieve: AsyncMock,
    mock_tenant_retrieve: AsyncMock,
    mock_tenant_rec: MagicMock,
    tenant_manager: TenantManager,  # Uses the fixture with mocked config
    mock_traction_config: MagicMock,
    mock_profile,
):
    """Test create_innkeeper when the innkeeper tenant/wallet already exist."""
    profile, session = mock_profile
    config = mock_traction_config.innkeeper_wallet
    tenant_id = config.tenant_id
    wallet_key = config.wallet_key
    expected_token = "existing_token"

    mock_wallet_rec = MagicMock(
        spec=WalletRecord,
        wallet_id="existing_wallet_id",
        wallet_name=config.wallet_name,
    )
    mock_tenant_retrieve.return_value = mock_tenant_rec
    mock_wallet_retrieve.return_value = mock_wallet_rec
    mock_get_token.return_value = expected_token

    await tenant_manager.create_innkeeper()

    mock_tenant_retrieve.assert_awaited_once_with(session, tenant_id)
    mock_wallet_retrieve.assert_awaited_once_with(session, "existing_wallet_id")
    mock_get_token.assert_awaited_once_with(mock_wallet_rec, wallet_key)
    mock_create_wallet.assert_not_awaited()  # Should not create wallet
    assert mock_print.call_count > 5  # Check that info was printed


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.TenantRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.innkeeper.tenant_manager.WalletRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
@patch.object(TenantManager, "get_token", new_callable=AsyncMock)
@patch.object(TenantManager, "create_wallet", new_callable=AsyncMock)
@patch("builtins.print")  # Mock print
async def test_create_innkeeper_does_not_exist(
    mock_print: MagicMock,
    mock_create_wallet: AsyncMock,
    mock_get_token: AsyncMock,  # This mock won't be called directly
    mock_wallet_retrieve: AsyncMock,
    mock_tenant_retrieve: AsyncMock,
    mock_tenant_rec: MagicMock,
    tenant_manager: TenantManager,
    mock_traction_config: MagicMock,
    mock_profile,
):
    """Test create_innkeeper when the innkeeper needs to be created."""
    from acapy_agent.storage.error import StorageNotFoundError  # Import locally

    profile, session = mock_profile
    config = mock_traction_config.innkeeper_wallet
    res_config = mock_traction_config.reservation
    tenant_id = config.tenant_id
    wallet_name = config.wallet_name
    wallet_key = config.wallet_key
    expected_token = "newly_created_token"

    # Simulate retrieval failure
    mock_tenant_retrieve.side_effect = StorageNotFoundError("Tenant not found")
    # Wallet retrieve won't be called if tenant retrieve fails

    # Mock create_wallet return values
    mock_tenant_rec.tenant_id = tenant_id
    mock_tenant_rec.wallet_id = "new_wallet_id"
    mock_wallet_rec = MagicMock(
        spec=WalletRecord, wallet_id="new_wallet_id", wallet_name=wallet_name
    )
    mock_create_wallet.return_value = (mock_tenant_rec, mock_wallet_rec, expected_token)

    await tenant_manager.create_innkeeper()

    mock_tenant_retrieve.assert_awaited_once_with(session, tenant_id)
    mock_wallet_retrieve.assert_not_awaited()  # Not called because tenant failed
    mock_get_token.assert_not_awaited()  # Not called directly, part of create_wallet mock
    # Check create_wallet was called with correct args from config
    mock_create_wallet.assert_awaited_once_with(
        wallet_name,
        wallet_key,
        None,  # Innkeeper has no email in this flow
        {  # Extra settings expected for innkeeper
            "wallet.innkeeper": True,
            "tenant.endorser_config": config.connect_to_endorser,
            "tenant.public_did_config": config.create_public_did,
            "tenant.auto_issuer": res_config.auto_issuer,
        },
        tenant_id,
    )
    assert mock_print.call_count > 5  # Check that info was printed
