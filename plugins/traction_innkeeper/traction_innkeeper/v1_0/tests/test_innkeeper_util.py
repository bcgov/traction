import pytest
import datetime
from unittest.mock import MagicMock, AsyncMock, patch

import bcrypt

from traction_innkeeper.v1_0.innkeeper.models import (
    ReservationRecord,
    TenantAuthenticationApiRecord,
)
from traction_innkeeper.v1_0.innkeeper.tenant_manager import TenantManager

from traction_innkeeper.v1_0.innkeeper.utils import (
    ReservationException,
    approve_reservation,
    create_api_key,
    generate_api_key_data,
    generate_reservation_token_data,
    refresh_registration_token,
)


# Mock the TenantRecord states if not easily importable or for isolation
class MockTenantRecord:
    STATE_ACTIVE: str = "active"
    STATE_DELETED: str = "deleted"


def test_generate_api_key_data():
    """
    Test the generation of API key data.
    Verifies types and that the hash matches the generated key.
    """
    key, salt, hash_val = generate_api_key_data()
    # Check types
    assert isinstance(key, str)
    assert isinstance(salt, bytes)
    assert isinstance(hash_val, bytes)
    # Check that values are generated
    assert key
    assert salt
    assert hash_val
    # Verify that the generated hash matches the key using the salt
    assert bcrypt.checkpw(key.encode("utf-8"), hash_val) is True
    # Verify that a different password doesn't match
    assert bcrypt.checkpw(b"wrongpassword", hash_val) is False


def test_generate_reservation_token_data():
    """
    Test the generation of reservation token data.
    Verifies types, hash matching, and expiry calculation.
    """
    test_expiry_minutes = 30
    pwd, salt, hash_val, expiry = generate_reservation_token_data(test_expiry_minutes)

    # Check types
    assert isinstance(pwd, str)
    assert isinstance(salt, bytes)
    assert isinstance(hash_val, bytes)
    assert isinstance(expiry, datetime.datetime)

    # Check that values are generated
    assert pwd
    assert salt
    assert hash_val
    assert expiry

    # Verify password hash
    assert bcrypt.checkpw(pwd.encode("utf-8"), hash_val) is True

    # Verify expiry time (allow for a small delta due to execution time)
    now_utc = datetime.datetime.now(datetime.timezone.utc).replace(
        tzinfo=None
    )  # Ensure comparison is offset-naive like the function's output
    expected_expiry = now_utc + datetime.timedelta(minutes=test_expiry_minutes)
    # Check if the generated expiry is within a reasonable range (e.g., 1 minute) of the expected time
    time_difference = abs(expiry - expected_expiry)
    assert time_difference < datetime.timedelta(minutes=1)

    # Check expiry is in the future relative to now
    assert expiry > now_utc


@pytest.mark.asyncio
async def test_create_api_key_success():
    """Test successful API key creation."""
    # 1. Mock the TenantAuthenticationApiRecord instance
    mock_rec = AsyncMock(spec=TenantAuthenticationApiRecord)
    mock_rec.state = MockTenantRecord.STATE_ACTIVE  # Set state to non-deleted
    mock_rec.tenant_authentication_api_id = "test-api-rec-id-123"
    # We will store the generated salt/hash here during the test
    mock_rec.api_key_token_salt = None
    mock_rec.api_key_token_hash = None

    # Mock the save method (async)
    mock_rec.save = AsyncMock()

    # 2. Mock the TenantManager and its profile session context manager
    mock_manager = MagicMock()
    mock_session = AsyncMock()  # Mock the session object yielded by the context manager
    mock_profile = MagicMock()
    # Configure the async context manager mock
    mock_profile.session = MagicMock()
    mock_profile.session.return_value.__aenter__.return_value = mock_session
    mock_profile.session.return_value.__aexit__.return_value = (
        None  # Or AsyncMock() if needed
    )
    mock_manager.profile = mock_profile

    # 3. Call the function under test
    generated_key, returned_id = await create_api_key(mock_rec, mock_manager)

    # 4. Assertions
    assert isinstance(generated_key, str)
    assert len(generated_key) > 0  # Key should be generated
    assert returned_id == "test-api-rec-id-123"

    # Check that record attributes were set
    assert mock_rec.api_key_token_salt is not None
    assert mock_rec.api_key_token_hash is not None

    # Verify the generated key matches the hash stored on the mock record
    assert bcrypt.checkpw(
        generated_key.encode("utf-8"),
        mock_rec.api_key_token_hash.encode(
            "utf-8"
        ),  # Assuming stored hash is str, adjust if bytes
    )

    # Check that save was called within the session context
    mock_rec.save.assert_awaited_once_with(mock_session)


@pytest.mark.asyncio
async def test_create_api_key_deleted_tenant():
    """Test API key creation fails for a deleted tenant."""
    # 1. Mock the TenantAuthenticationApiRecord instance
    mock_rec = MagicMock(
        spec=TenantAuthenticationApiRecord
    )  # No async methods needed here
    mock_rec.state = MockTenantRecord.STATE_DELETED  # Set state to deleted

    # 2. Mock the TenantManager (profile not strictly needed as it should fail early)
    mock_manager = MagicMock()

    # 3. Call the function and assert ValueError is raised
    with pytest.raises(ValueError, match="Tenant is disabled"):
        await create_api_key(mock_rec, mock_manager)

    # 4. Assert save was NOT called (optional but good practice)
    # If mock_rec had an async save mock setup, you'd assert it wasn't called:
    # mock_rec.save.assert_not_awaited()


# Mock the ReservationRecord states if not easily importable
class MockReservationRecord:
    STATE_REQUESTED: str = "requested"
    STATE_APPROVED: str = "approved"
    STATE_DENIED: str = "denied"  # Example other state


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.innkeeper.utils.generate_reservation_token_data"
)  # Patch the helper function
async def test_approve_reservation_success(mock_generate_token_data):
    """Test successful reservation approval."""
    # 1. Configure Mock for generate_reservation_token_data
    test_pwd = "test-password-123"
    test_salt = bcrypt.gensalt()
    test_hash = bcrypt.hashpw(test_pwd.encode("utf-8"), test_salt)
    test_expiry = datetime.datetime.now(datetime.timezone.utc).replace(
        tzinfo=None
    ) + datetime.timedelta(minutes=60)
    mock_generate_token_data.return_value = (
        test_pwd,
        test_salt,
        test_hash,
        test_expiry,
    )

    # 2. Mock ReservationRecord instance
    mock_rec = AsyncMock(spec=ReservationRecord)
    mock_rec.reservation_id = "res-123"
    mock_rec.state = MockReservationRecord.STATE_REQUESTED  # Correct initial state
    mock_rec.reservation_token_salt = None
    mock_rec.reservation_token_hash = None
    mock_rec.reservation_token_expiry = None
    mock_rec.state_notes = None
    mock_rec.save = AsyncMock()  # Mock the save method

    # 3. Mock TenantManager and session
    mock_manager = MagicMock(spec=TenantManager)
    mock_manager._config = MagicMock()
    mock_manager._config.reservation = MagicMock()
    # Mock the config value needed by the patched function (via manager)
    mock_manager._config.reservation.expiry_minutes = 60
    mock_session = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.session.return_value.__aenter__.return_value = mock_session
    mock_profile.session.return_value.__aexit__.return_value = None
    mock_manager.profile = mock_profile

    # 4. Mock ReservationRecord class method retrieve_by_reservation_id
    with patch.object(
        ReservationRecord, "retrieve_by_reservation_id", return_value=mock_rec
    ) as mock_retrieve:
        # 5. Call the function
        reservation_id = "res-123"
        state_notes = "Approved by test"
        returned_pwd = await approve_reservation(
            reservation_id, state_notes, mock_manager
        )

        # 6. Assertions
        mock_retrieve.assert_awaited_once_with(
            mock_session, reservation_id, for_update=True
        )
        mock_generate_token_data.assert_called_once_with(60)  # Check expiry used

        # Check record attributes were updated before save
        assert mock_rec.state == MockReservationRecord.STATE_APPROVED
        assert mock_rec.state_notes == state_notes
        assert mock_rec.reservation_token_salt == test_salt.decode("utf-8")
        assert mock_rec.reservation_token_hash == test_hash.decode("utf-8")
        assert mock_rec.reservation_token_expiry == test_expiry

        # Check save was called
        mock_rec.save.assert_awaited_once_with(mock_session)

        # Check correct password was returned
        assert returned_pwd == test_pwd


@pytest.mark.asyncio
async def test_approve_reservation_wrong_state():
    """Test reservation approval fails if not in requested state."""
    # 1. Mock ReservationRecord instance with wrong state
    mock_rec = AsyncMock(spec=ReservationRecord)
    mock_rec.reservation_id = "res-456"
    mock_rec.state = MockReservationRecord.STATE_DENIED  # Incorrect initial state
    mock_rec.save = AsyncMock()

    # 2. Mock TenantManager and session
    mock_manager = MagicMock(spec=TenantManager)
    mock_session = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.session.return_value.__aenter__.return_value = mock_session
    mock_profile.session.return_value.__aexit__.return_value = None
    mock_manager.profile = mock_profile

    # 3. Mock ReservationRecord retrieval
    with patch.object(
        ReservationRecord, "retrieve_by_reservation_id", return_value=mock_rec
    ):
        # 4. Call and assert exception
        with pytest.raises(
            ReservationException,
            match=f"Reservation state is currently '{MockReservationRecord.STATE_DENIED}'",
        ):
            await approve_reservation("res-456", "notes", mock_manager)

        # 5. Assert save was not called
        mock_rec.save.assert_not_awaited()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.innkeeper.utils.uuid"
)  # Patch uuid module used inside refresh function
@patch(
    "traction_innkeeper.v1_0.innkeeper.utils.bcrypt"
)  # Patch bcrypt module used inside refresh function
@patch(
    "traction_innkeeper.v1_0.innkeeper.utils.datetime"
)  # Patch datetime module used inside refresh function
async def test_refresh_registration_token_success(
    mock_datetime, mock_bcrypt, mock_uuid
):
    """Test successful token refresh."""
    # 1. Configure mocks for token generation primitives
    test_new_pwd_uuid = "new-uuid-pwd-456"
    mock_uuid.uuid4.return_value.hex = test_new_pwd_uuid

    test_new_salt = b"$2b$12$abcdefghijklmnopqrstuvwx."  # Example salt bytes
    mock_bcrypt.gensalt.return_value = test_new_salt

    test_new_hash = (
        b"$2b$12$abcdefghijklmnopqrstuvwx.hashedpasswordvalue"  # Example hash bytes
    )
    mock_bcrypt.hashpw.return_value = test_new_hash

    fixed_now = datetime.datetime(2023, 10, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_datetime.utcnow.return_value = fixed_now.replace(
        tzinfo=None
    )  # utcnow returns naive
    mock_datetime.now.return_value = fixed_now  # If needed elsewhere
    # Keep timedelta available
    mock_datetime.timedelta = datetime.timedelta

    # 2. Mock ReservationRecord instance
    mock_rec = AsyncMock(spec=ReservationRecord)
    mock_rec.reservation_id = "res-789"
    mock_rec.state = MockReservationRecord.STATE_APPROVED  # Correct initial state
    mock_rec.reservation_token_salt = "old_salt"
    mock_rec.reservation_token_hash = "old_hash"
    mock_rec.reservation_token_expiry = fixed_now - datetime.timedelta(
        days=1
    )  # Old expiry
    mock_rec.save = AsyncMock()

    # 3. Mock TenantManager and session/config
    mock_manager = MagicMock(spec=TenantManager)
    mock_manager._config = MagicMock()
    mock_manager._config.reservation = MagicMock()
    mock_manager._config.reservation.expiry_minutes = 45  # Example expiry
    mock_session = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.session.return_value.__aenter__.return_value = mock_session
    mock_profile.session.return_value.__aexit__.return_value = None
    mock_manager.profile = mock_profile

    # 4. Mock ReservationRecord retrieval
    with patch.object(
        ReservationRecord, "retrieve_by_reservation_id", return_value=mock_rec
    ) as mock_retrieve:
        # 5. Call the function
        reservation_id = "res-789"
        returned_pwd = await refresh_registration_token(reservation_id, mock_manager)

        # 6. Assertions
        mock_retrieve.assert_awaited_once_with(
            mock_session, reservation_id, for_update=True
        )

        # Check token generation calls
        mock_uuid.uuid4.assert_called_once()
        mock_bcrypt.gensalt.assert_called_once()
        mock_bcrypt.hashpw.assert_called_once_with(
            test_new_pwd_uuid.encode("utf-8"), test_new_salt
        )
        mock_datetime.utcnow.assert_called_once()  # Used for expiry calculation

        # Check record attributes were updated
        expected_expiry = fixed_now.replace(tzinfo=None) + datetime.timedelta(
            minutes=45
        )
        assert mock_rec.reservation_token_salt == test_new_salt.decode("utf-8")
        assert mock_rec.reservation_token_hash == test_new_hash.decode("utf-8")
        assert mock_rec.reservation_token_expiry == expected_expiry

        # Check save was called
        mock_rec.save.assert_awaited_once_with(mock_session)

        # Check correct new password was returned
        assert returned_pwd == test_new_pwd_uuid


@pytest.mark.asyncio
async def test_refresh_registration_token_wrong_state():
    """Test token refresh fails if not in approved state."""
    # 1. Mock ReservationRecord instance with wrong state
    mock_rec = AsyncMock(spec=ReservationRecord)
    mock_rec.reservation_id = "res-111"
    mock_rec.state = MockReservationRecord.STATE_REQUESTED  # Incorrect state
    mock_rec.save = AsyncMock()

    # 2. Mock TenantManager and session
    mock_manager = MagicMock(spec=TenantManager)
    mock_manager._config = MagicMock()
    mock_manager._config.reservation = MagicMock()
    # Config needed even if check fails early
    mock_manager._config.reservation.expiry_minutes = 30
    mock_session = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.session.return_value.__aenter__.return_value = mock_session
    mock_profile.session.return_value.__aexit__.return_value = None
    mock_manager.profile = mock_profile

    # 3. Mock ReservationRecord retrieval
    with patch.object(
        ReservationRecord, "retrieve_by_reservation_id", return_value=mock_rec
    ):
        # 4. Call and assert exception
        with pytest.raises(
            ReservationException, match="Only approved reservations can refresh tokens"
        ):
            await refresh_registration_token("res-111", mock_manager)

        # 5. Assert save was not called
        mock_rec.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_refresh_registration_token_retrieval_fails():
    """Test token refresh fails if reservation retrieval fails."""
    # 1. Mock TenantManager and session
    mock_manager = MagicMock(spec=TenantManager)
    mock_manager._config = MagicMock()
    mock_manager._config.reservation = MagicMock()
    mock_manager._config.reservation.expiry_minutes = 30
    mock_session = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.session.return_value.__aenter__.return_value = mock_session
    mock_profile.session.return_value.__aexit__.return_value = None
    mock_manager.profile = mock_profile

    # 2. Mock ReservationRecord retrieval to raise an error
    with patch.object(
        ReservationRecord,
        "retrieve_by_reservation_id",
        side_effect=Exception("DB error"),
    ) as mock_retrieve:
        # 3. Call and assert exception
        with pytest.raises(
            ReservationException, match="Could not retrieve reservation record."
        ):
            await refresh_registration_token("res-222", mock_manager)

        # Check retrieval was attempted
        mock_retrieve.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_registration_token_save_fails():
    """Test token refresh fails if saving the record fails."""
    # (Setup mocks for uuid, bcrypt, datetime as in the success case)
    # ... (Copy mocks for uuid, bcrypt, datetime from success test) ...

    # 1. Mock ReservationRecord instance
    mock_rec = AsyncMock(spec=ReservationRecord)
    mock_rec.reservation_id = "res-333"
    mock_rec.state = MockReservationRecord.STATE_APPROVED
    # Mock save to raise an error
    mock_rec.save = AsyncMock(side_effect=Exception("Save failed"))

    # 2. Mock TenantManager and session/config
    # ... (Copy mocks for manager, config, session from success test) ...
    mock_manager = MagicMock(spec=TenantManager)
    mock_manager._config = MagicMock()
    mock_manager._config.reservation = MagicMock()
    mock_manager._config.reservation.expiry_minutes = 30
    mock_session = AsyncMock()
    mock_profile = MagicMock()
    mock_profile.session.return_value.__aenter__.return_value = mock_session
    mock_profile.session.return_value.__aexit__.return_value = None
    mock_manager.profile = mock_profile

    # 3. Mock ReservationRecord retrieval
    with patch.object(
        ReservationRecord, "retrieve_by_reservation_id", return_value=mock_rec
    ):
        # Use patches for token generation primitives like in success case
        with patch("traction_innkeeper.v1_0.innkeeper.utils.uuid"), patch(
            "traction_innkeeper.v1_0.innkeeper.utils.bcrypt"
        ), patch("traction_innkeeper.v1_0.innkeeper.utils.datetime"):
            # 4. Call and assert exception
            with pytest.raises(
                ReservationException, match="Could not update reservation record."
            ):
                await refresh_registration_token("res-333", mock_manager)

            # 5. Assert save was attempted
            mock_rec.save.assert_awaited_once_with(mock_session)
