import logging
from acapy_agent.wallet.crypto import ED25519
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call, ANY

from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageDuplicateError, StorageNotFoundError
from acapy_agent.wallet.base import SOV, BaseWallet
from acapy_agent.wallet.did_info import DIDInfo
from acapy_agent.wallet.error import WalletError
from marshmallow import ValidationError

# Assuming models and service are importable like this
from traction_innkeeper.v1_0.oca.models import OcaRecord
from traction_innkeeper.v1_0.oca.oca_service import (
    OcaService,
    PublicDIDRequiredError,
    PublicDIDMismatchError,
)

# Disable logging noise during tests
logging.disable(logging.CRITICAL)
ISSUER_DID = "55GkHamhTU1ZbTbV2ab9DE"
SCHEMA_ID = f"{ISSUER_DID}:2:schema:1.0"
CRED_DEF_ID = f"{ISSUER_DID}:3:CL:1:tag"
OCA_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


# --- Fixtures (Optional but can simplify setup) ---
@pytest.fixture
def mock_profile():
    """Provides a mocked Profile with a working async session manager."""
    profile = MagicMock(spec=Profile)
    mock_session = AsyncMock()
    profile.session = MagicMock()
    profile.session.return_value.__aenter__.return_value = mock_session
    profile.session.return_value.__aexit__.return_value = None
    return profile, mock_session


@pytest.fixture
def mock_issuer_profile():
    """Provides a mocked issuer Profile."""
    profile = MagicMock(spec=Profile)
    mock_session = AsyncMock()
    profile.session = MagicMock()
    profile.session.return_value.__aenter__.return_value = mock_session
    profile.session.return_value.__aexit__.return_value = None
    return profile, mock_session


@pytest.fixture
def mock_wallet():
    """Provides a mocked BaseWallet."""
    return AsyncMock(spec=BaseWallet)


@pytest.fixture
def mock_did_info():
    """Provides an example DIDInfo."""
    return DIDInfo(
        did="test-did-123",
        verkey="test-verkey-456",
        metadata={},
        method=SOV,
        key_type=ED25519,
    )


@pytest.fixture
def oca_service(mock_profile):
    """Provides an OcaService instance with a mocked root profile."""
    root_profile, _ = mock_profile
    return OcaService(root_profile)


@pytest.mark.asyncio
async def test_get_public_did_info_success(
    oca_service: OcaService, mock_issuer_profile, mock_wallet, mock_did_info
):
    """Test successfully getting public DID info."""
    issuer_profile, issuer_session = mock_issuer_profile
    issuer_session.inject_or = MagicMock(return_value=mock_wallet)
    mock_wallet.get_public_did.return_value = mock_did_info

    result = await oca_service.get_public_did_info(issuer_profile)

    assert result == mock_did_info
    issuer_profile.session.assert_called_once()
    issuer_session.inject_or.assert_called_once_with(BaseWallet)
    mock_wallet.get_public_did.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_public_did_info_no_wallet(
    oca_service: OcaService, mock_issuer_profile
):
    """Test getting public DID info when wallet is not found."""
    issuer_profile, issuer_session = mock_issuer_profile
    issuer_session.inject_or = MagicMock(return_value=None)

    with pytest.raises(WalletError, match="Wallet not found"):
        await oca_service.get_public_did_info(issuer_profile)

    issuer_profile.session.assert_called_once()
    issuer_session.inject_or.assert_called_once_with(BaseWallet)


@pytest.mark.asyncio
async def test_get_public_did_info_wallet_error(
    oca_service: OcaService, mock_issuer_profile, mock_wallet
):
    """Test getting public DID info when wallet raises an error."""
    issuer_profile, issuer_session = mock_issuer_profile
    issuer_session.inject_or = MagicMock(return_value=mock_wallet)
    mock_wallet.get_public_did.side_effect = WalletError("Wallet access failed")

    with pytest.raises(WalletError, match="Wallet access failed"):
        await oca_service.get_public_did_info(issuer_profile)

    mock_wallet.get_public_did.assert_awaited_once()


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info")
async def test_get_public_did_success(
    mock_get_info, oca_service: OcaService, mock_issuer_profile, mock_did_info
):
    """Test getting public DID successfully."""
    issuer_profile, _ = mock_issuer_profile
    mock_get_info.return_value = mock_did_info

    result = await oca_service.get_public_did(issuer_profile)

    assert result == "test-did-123"
    mock_get_info.assert_awaited_once_with(issuer_profile)


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info")
async def test_get_public_did_no_did_no_raise(
    mock_get_info, oca_service: OcaService, mock_issuer_profile
):
    """Test getting public DID when none exists, without raising error."""
    issuer_profile, _ = mock_issuer_profile
    mock_get_info.return_value = None

    result = await oca_service.get_public_did(issuer_profile, raise_err=False)

    assert result is None
    mock_get_info.assert_awaited_once_with(issuer_profile)


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info")
async def test_get_public_did_no_did_raise(
    mock_get_info, oca_service: OcaService, mock_issuer_profile
):
    """Test getting public DID when none exists, raising error."""
    issuer_profile, _ = mock_issuer_profile
    mock_get_info.return_value = None

    with pytest.raises(PublicDIDRequiredError):
        await oca_service.get_public_did(issuer_profile, raise_err=True)

    mock_get_info.assert_awaited_once_with(issuer_profile)


def test_is_cred_def_owner(oca_service: OcaService):
    """Test cred def owner check."""
    issuer_did = "55GkHamhTU1ZbTbV2ab9DE"
    assert (
        oca_service.is_cred_def_owner(
            issuer_did, "55GkHamhTU1ZbTbV2ab9DE:3:CL:1234:default"
        )
        is True
    )
    assert oca_service.is_cred_def_owner(issuer_did, "123:3:CL:1:tag") is False
    assert oca_service.is_cred_def_owner(issuer_did, None) is False
    assert oca_service.is_cred_def_owner(issuer_did, "invalid-cd-id") is False


def test_validate_oca_data_success(oca_service: OcaService):
    """Test successful OCA data validation."""
    issuer_did = ISSUER_DID
    valid_data = {
        "schema_id": SCHEMA_ID,
        "cred_def_id": CRED_DEF_ID,
        "url": "http://example.com/oca",
    }
    assert oca_service.validate_oca_data(issuer_did, valid_data) is True

    valid_data_bundle = {
        "schema_id": SCHEMA_ID,
        "cred_def_id": CRED_DEF_ID,
        "bundle": {"some": "data"},
    }
    assert oca_service.validate_oca_data(issuer_did, valid_data_bundle) is True


def test_validate_oca_data_failures(oca_service: OcaService):
    """Test OCA data validation failures."""
    with pytest.raises(ValidationError) as exc_info:
        oca_service.validate_oca_data("did:sov:123", {})
    assert "schema_id" in exc_info.value.messages
    assert "cred_def_id" in exc_info.value.messages
    assert "url" in exc_info.value.messages

    with pytest.raises(ValidationError) as exc_info:
        oca_service.validate_oca_data(
            "did:sov:ABC",
            {
                "schema_id": "did:sov:123:2:schema:1.0",
                "cred_def_id": "did:sov:123:3:CL:1:tag",
                "url": "http://example.com/oca",
            },
        )
    assert "cred_def_id" in exc_info.value.messages
    assert "not created by caller" in exc_info.value.messages["cred_def_id"]

    with pytest.raises(ValidationError) as exc_info:
        oca_service.validate_oca_data(
            "did:sov:123",
            {
                "schema_id": "did:sov:123:2:schema:1.0",
                "cred_def_id": "did:sov:123:3:CL:1:tag",
            },
        )
    assert "url" in exc_info.value.messages


def test_build_tag_filter(oca_service: OcaService):
    """Test tag filter building."""
    assert oca_service.build_tag_filter(None, None) == {}
    assert oca_service.build_tag_filter(SCHEMA_ID, None) == {"schema_id": SCHEMA_ID}
    assert oca_service.build_tag_filter(None, CRED_DEF_ID) == {
        "cred_def_id": CRED_DEF_ID
    }
    assert oca_service.build_tag_filter(SCHEMA_ID, CRED_DEF_ID) == {
        "schema_id": SCHEMA_ID,
        "cred_def_id": CRED_DEF_ID,
    }


def test_build_post_filter(oca_service: OcaService, mock_did_info: DIDInfo):
    """Test post filter building."""
    assert oca_service.build_post_filter(None) == {}
    no_did_info = MagicMock(spec=DIDInfo, did=None)
    assert mock_did_info.did == "test-did-123"
    assert mock_did_info
    assert oca_service.build_post_filter(no_did_info) == {}
    assert oca_service.build_post_filter(mock_did_info) == {"owner_did": "test-did-123"}


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info",
    new_callable=AsyncMock,
)
@patch("traction_innkeeper.v1_0.oca.models.OcaRecord.query", new_callable=AsyncMock)
async def test_list_oca_records_as_root(
    mock_query: AsyncMock,
    mock_get_info: AsyncMock,
    oca_service: OcaService,
    mock_issuer_profile,
):
    """Test listing OCA records as root (issuer profile matches service profile)."""
    issuer_profile, _ = mock_issuer_profile
    oca_service._profile = issuer_profile
    mock_get_info.return_value = None
    mock_record = MagicMock(spec=OcaRecord)
    mock_query.return_value = [mock_record]

    schema_id = "schema-1"
    cred_def_id = "cd-1"
    records = await oca_service.list_oca_records(issuer_profile, schema_id, cred_def_id)

    assert records == [mock_record]
    mock_get_info.assert_awaited_once_with(issuer_profile)
    expected_tag_filter = {"schema_id": schema_id, "cred_def_id": cred_def_id}
    # As root, post_filter should be empty
    mock_query.assert_awaited_once_with(
        session=ANY,  # Check session object is passed
        tag_filter=expected_tag_filter,
        post_filter_positive={},
        alt=True,
    )
    assert isinstance(mock_query.call_args.kwargs["session"], AsyncMock)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.oca.oca_service.OcaRecord.query", new_callable=AsyncMock
)
async def test_list_oca_records_as_tenant(
    mock_query: AsyncMock,
    mock_get_info: AsyncMock,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
    mock_did_info,
):
    """Test listing OCA records as a tenant (issuer profile differs from service)."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    oca_service._profile = root_profile
    mock_get_info.return_value = mock_did_info
    mock_record = MagicMock(spec=OcaRecord)
    mock_query.return_value = [mock_record]

    schema_id = "schema-1"
    cred_def_id = "cd-1"
    records = await oca_service.list_oca_records(issuer_profile, schema_id, cred_def_id)

    assert records == [mock_record]
    mock_get_info.assert_awaited_once_with(issuer_profile)
    expected_tag_filter = {"schema_id": schema_id, "cred_def_id": cred_def_id}
    expected_post_filter = {"owner_did": mock_did_info.did}
    mock_query.assert_awaited_once_with(
        session=ANY,
        tag_filter=expected_tag_filter,
        post_filter_positive=expected_post_filter,
        alt=True,
    )


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info")
@patch(
    "traction_innkeeper.v1_0.oca.oca_service.OcaRecord.query", new_callable=AsyncMock
)
async def test_list_oca_records_tenant_no_did(
    mock_query: AsyncMock,
    mock_get_info: AsyncMock,
    oca_service: OcaService,
    mock_issuer_profile,
):
    """Test listing OCA records as tenant fails if no public DID."""
    issuer_profile, _ = mock_issuer_profile
    oca_service._profile = MagicMock(spec=Profile, name="root_profile")
    mock_get_info.return_value = None

    records = await oca_service.list_oca_records(issuer_profile, None, None)

    # Should return empty list as query is skipped
    assert records == []
    mock_get_info.assert_awaited_once_with(issuer_profile)
    mock_query.assert_not_awaited()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.oca.oca_service.OcaRecord.query", new_callable=AsyncMock
)
async def test_find_or_new_oca_record_finds_existing_no_update(
    mock_query: AsyncMock,
    mock_get_info: AsyncMock,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
    mock_did_info,
):
    """Test finding an existing OCA record without updating."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    mock_get_info.return_value = mock_did_info
    mock_existing_rec = MagicMock(spec=OcaRecord)

    # Configure the query mock's return value
    mock_query.return_value = [mock_existing_rec]

    oca_data = {
        "schema_id": SCHEMA_ID,
        "cred_def_id": CRED_DEF_ID,
        "url": "http://old.com",
    }

    record = await oca_service.find_or_new_oca_record(
        issuer_profile, oca_data, update=False
    )

    assert record == mock_existing_rec
    mock_get_info.assert_awaited_once_with(issuer_profile)
    mock_query.assert_awaited_once_with(
        session=root_session,
        tag_filter=ANY,
        post_filter_positive=ANY,
        alt=True,
    )


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaRecord")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info")
async def test_find_or_new_oca_record_finds_existing_and_updates(
    mock_get_info: AsyncMock,
    MockOcaRecord: MagicMock,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
    mock_did_info,
):
    """Test finding an existing OCA record and updating it."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    mock_get_info.return_value = mock_did_info
    mock_existing_rec = MagicMock(spec=OcaRecord)
    mock_existing_rec.url = "http://old.com"
    mock_existing_rec.bundle = {"old": "bundle"}

    # Configure the 'query' classmethod on the mocked OcaRecord class
    MockOcaRecord.query = AsyncMock(return_value=[mock_existing_rec])

    oca_data = {
        "schema_id": SCHEMA_ID,
        "cred_def_id": CRED_DEF_ID,
        "url": "http://new.com",
        "bundle": {"new": "bundle"},
    }

    record = await oca_service.find_or_new_oca_record(
        issuer_profile, oca_data, update=True
    )

    assert record == mock_existing_rec
    MockOcaRecord.query.assert_awaited_once_with(
        session=root_session,
        tag_filter=ANY,
        post_filter_positive=ANY,
        alt=True,
    )
    # Check existing record attributes were modified (on the mock instance returned by query)
    assert mock_existing_rec.url == "http://new.com"
    assert mock_existing_rec.bundle == {"new": "bundle"}

    # Still shouldn't create new instance
    MockOcaRecord.assert_not_called()


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaRecord")
@patch(
    "traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info",
    new_callable=AsyncMock,
)
async def test_find_or_new_oca_record_creates_new(
    mock_get_info,
    MockOcaRecord,
    oca_service: OcaService,
    mock_issuer_profile,
    mock_did_info,
):
    """Test creating a new OCA record when none is found."""
    issuer_profile, _ = mock_issuer_profile
    mock_get_info.return_value = mock_did_info
    MockOcaRecord.query = AsyncMock(return_value=[])
    mock_new_rec_instance = MagicMock(spec=OcaRecord)
    MockOcaRecord.return_value = mock_new_rec_instance

    oca_data = {
        "schema_id": SCHEMA_ID,
        "cred_def_id": CRED_DEF_ID,
        "url": "http://new.com",
    }

    record = await oca_service.find_or_new_oca_record(
        issuer_profile, oca_data, update=True
    )

    assert record == mock_new_rec_instance
    # Check OcaRecord constructor was called correctly
    MockOcaRecord.assert_called_once_with(
        schema_id=SCHEMA_ID,
        cred_def_id=CRED_DEF_ID,
        url="http://new.com",
        bundle=None,
        owner_did=mock_did_info.did,
    )


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did_info")
@patch(
    "traction_innkeeper.v1_0.oca.oca_service.OcaRecord.query", new_callable=AsyncMock
)
async def test_find_or_new_oca_record_duplicate_error(
    mock_query: AsyncMock,
    mock_get_info: AsyncMock,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
    mock_did_info,
):
    """Test duplicate error when finding OCA records."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    mock_get_info.return_value = mock_did_info
    mock_query.return_value = [MagicMock(), MagicMock()]

    oca_data = {"schema_id": SCHEMA_ID, "cred_def_id": CRED_DEF_ID}

    with pytest.raises(StorageDuplicateError):
        await oca_service.find_or_new_oca_record(issuer_profile, oca_data)

    mock_query.assert_awaited_once_with(
        session=root_session,
        tag_filter=ANY,
        post_filter_positive=ANY,
        alt=True,
    )
    mock_get_info.assert_awaited_once_with(issuer_profile)


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.find_or_new_oca_record")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.validate_oca_data")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did")
async def test_create_or_update_oca_record_success(
    mock_get_did,
    mock_validate,
    mock_find_or_new,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
):
    """Test successful creation/update of OCA record."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    mock_get_did.return_value = "test-did-123"
    mock_validate.return_value = True
    mock_rec = AsyncMock(spec=OcaRecord)
    mock_find_or_new.return_value = mock_rec

    oca_data = {"schema_id": SCHEMA_ID, "cred_def_id": "cd1:test-did-123", "url": "u"}

    result = await oca_service.create_or_update_oca_record(issuer_profile, oca_data)

    assert result == mock_rec
    mock_get_did.assert_awaited_once_with(issuer_profile, True)
    mock_validate.assert_called_once_with("test-did-123", oca_data)
    mock_find_or_new.assert_awaited_once_with(issuer_profile, oca_data, True)
    root_profile.session.assert_called_once()
    mock_rec.save.assert_awaited_once_with(
        root_session, reason="Create/Update OCA record"
    )


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.find_or_new_oca_record")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.validate_oca_data")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did")
async def test_create_or_update_oca_record_validation_fails(
    mock_get_did,
    mock_validate,
    mock_find_or_new,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
):
    """Test failure during OCA data validation."""
    _, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    mock_get_did.return_value = "test-did-123"
    mock_validate.side_effect = ValidationError("Invalid data")

    oca_data = {"invalid": "data"}

    with pytest.raises(ValidationError, match="Invalid data"):
        await oca_service.create_or_update_oca_record(issuer_profile, oca_data)

    mock_get_did.assert_awaited_once_with(issuer_profile, True)
    mock_validate.assert_called_once_with("test-did-123", oca_data)
    mock_find_or_new.assert_not_awaited()
    root_session.save.assert_not_awaited()


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaRecord.retrieve_by_id")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did")
async def test_read_oca_record_success(
    mock_get_did,
    mock_retrieve,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
):
    """Test successfully reading an OCA record."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    public_did = "owner-did-match"
    mock_get_did.return_value = public_did
    mock_rec = AsyncMock(spec=OcaRecord, owner_did=public_did)
    mock_retrieve.return_value = mock_rec

    oca_id = OCA_ID
    result = await oca_service.read_oca_record(issuer_profile, oca_id)

    assert result == mock_rec
    mock_get_did.assert_awaited_once_with(issuer_profile, True)
    root_profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(root_session, oca_id)
    # Check save is called (even though read only - maybe for update?)
    mock_rec.save.assert_awaited_once_with(root_session)


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaRecord.retrieve_by_id")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did")
async def test_read_oca_record_did_mismatch(
    mock_get_did,
    mock_retrieve,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
):
    """Test reading OCA record fails due to owner DID mismatch."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    mock_get_did.return_value = "caller-did"
    mock_rec = AsyncMock(spec=OcaRecord, owner_did="different-owner-did")
    mock_retrieve.return_value = mock_rec

    oca_id = OCA_ID
    with pytest.raises(PublicDIDMismatchError):
        await oca_service.read_oca_record(issuer_profile, oca_id)

    mock_get_did.assert_awaited_once_with(issuer_profile, True)
    root_profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(root_session, oca_id)
    mock_rec.save.assert_not_awaited()


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaRecord.retrieve_by_id")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did")
async def test_update_oca_record_success(
    mock_get_did,
    mock_retrieve,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
):
    """Test successfully updating an OCA record."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    public_did = "owner-did-match"
    mock_get_did.return_value = public_did
    mock_rec = AsyncMock(spec=OcaRecord, owner_did=public_did)
    mock_retrieve.return_value = mock_rec

    oca_id = OCA_ID
    update_data = {"url": "http://updated.com", "bundle": None}

    result = await oca_service.update_oca_record(issuer_profile, oca_id, update_data)

    assert result == mock_rec
    assert result.url == "http://updated.com"
    assert result.bundle is None
    mock_get_did.assert_awaited_once_with(issuer_profile, True)
    root_profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(root_session, oca_id, for_update=True)
    mock_rec.save.assert_awaited_once_with(root_session)


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaRecord.retrieve_by_id")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did")
async def test_update_oca_record_did_mismatch(
    mock_get_did,
    mock_retrieve,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
):
    """Test updating OCA record fails due to owner DID mismatch."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    mock_get_did.return_value = "caller-did"
    mock_rec = AsyncMock(spec=OcaRecord, owner_did="different-owner-did")
    mock_retrieve.return_value = mock_rec

    oca_id = OCA_ID
    update_data = {"url": "http://irrelevant.com"}
    with pytest.raises(PublicDIDMismatchError):
        await oca_service.update_oca_record(issuer_profile, oca_id, update_data)

    mock_retrieve.assert_awaited_once_with(root_session, oca_id, for_update=True)
    mock_rec.save.assert_not_awaited()


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaRecord.retrieve_by_id")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did")
async def test_update_oca_record_validation_error(
    mock_get_did,
    mock_retrieve,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
):
    """Test updating OCA record fails validation (no url or bundle)."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    public_did = "owner-did-match"
    mock_get_did.return_value = public_did
    mock_rec = AsyncMock(spec=OcaRecord, owner_did=public_did)
    mock_retrieve.return_value = mock_rec

    oca_id = OCA_ID
    update_data = {}  # Missing url and bundle

    with pytest.raises(ValidationError, match="URL or bundle is required"):
        await oca_service.update_oca_record(issuer_profile, oca_id, update_data)

    mock_retrieve.assert_awaited_once_with(root_session, oca_id, for_update=True)
    mock_rec.save.assert_not_awaited()


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaRecord.retrieve_by_id")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did")
async def test_delete_oca_record_success(
    mock_get_did,
    mock_retrieve,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
):
    """Test successfully deleting an OCA record."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    public_did = "owner-did-match"
    mock_get_did.return_value = public_did
    mock_rec = AsyncMock(spec=OcaRecord, owner_did=public_did)
    # Simulate retrieve succeeding first, then failing after delete
    mock_retrieve.side_effect = [
        mock_rec,
        StorageNotFoundError("Not found after delete"),
    ]

    oca_id = OCA_ID
    result = await oca_service.delete_oca_record(issuer_profile, oca_id)

    assert result is True
    mock_get_did.assert_awaited_once_with(issuer_profile, True)
    assert root_profile.session.call_count == 1  # Only one session context used
    # Check retrieve was called twice (once to get, once to confirm deletion)
    assert mock_retrieve.await_count == 2
    mock_retrieve.assert_has_awaits(
        [
            call(root_session, oca_id, for_update=True),
            call(root_session, oca_id),
        ]
    )
    mock_rec.delete_record.assert_awaited_once_with(root_session)


@pytest.mark.asyncio
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaRecord.retrieve_by_id")
@patch("traction_innkeeper.v1_0.oca.oca_service.OcaService.get_public_did")
async def test_delete_oca_record_did_mismatch(
    mock_get_did,
    mock_retrieve,
    oca_service: OcaService,
    mock_profile,
    mock_issuer_profile,
):
    """Test deleting OCA record fails due to owner DID mismatch."""
    root_profile, root_session = mock_profile
    issuer_profile, _ = mock_issuer_profile
    mock_get_did.return_value = "caller-did"
    mock_rec = AsyncMock(spec=OcaRecord, owner_did="different-owner-did")
    mock_retrieve.return_value = mock_rec

    oca_id = OCA_ID
    with pytest.raises(PublicDIDMismatchError):
        await oca_service.delete_oca_record(issuer_profile, oca_id)

    mock_retrieve.assert_awaited_once_with(root_session, oca_id, for_update=True)
    mock_rec.delete_record.assert_not_awaited()
