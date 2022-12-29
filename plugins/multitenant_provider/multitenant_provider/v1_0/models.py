from typing import List, Optional

from aries_cloudagent.core.profile import ProfileSession
from aries_cloudagent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from aries_cloudagent.messaging.valid import UUIDFour
from aries_cloudagent.storage.error import StorageDuplicateError, StorageNotFoundError
from aries_cloudagent.wallet.models.wallet_record import (
    WalletRecord,
    WalletRecordSchema,
)
from marshmallow import fields
from marshmallow.utils import EXCLUDE


class WalletTokenRecord(BaseRecord):
    """Multitenant Provider Wallet Token(s) Record."""

    class Meta:
        """WalletTokenRecord Meta."""

        schema_class = "WalletTokenRecordSchema"

    RECORD_TYPE = "wallet_token"
    RECORD_ID_NAME = "wallet_token_id"
    TAG_NAMES = {
        "wallet_id",
    }

    def __init__(
        self,
        *,
        wallet_token_id: str = None,
        wallet_id: str = None,
        issued_at_claims: Optional[List] = [],
        wallet_key_salt: str = None,
        wallet_key_hash: str = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(wallet_token_id, **kwargs)
        self.wallet_id = wallet_id
        self._issued_at_claims = issued_at_claims
        self.wallet_key_salt = wallet_key_salt
        self.wallet_key_hash = wallet_key_hash

    @property
    def wallet_token_id(self) -> Optional[str]:
        """Return record id."""
        return self._id

    @property
    def issued_at_claims(self):
        return self._issued_at_claims

    def add_issued_at_claims(self, iat):
        self._issued_at_claims.append(iat)

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "wallet_id",
                "issued_at_claims",
                "wallet_key_salt",
                "wallet_key_hash",
            )
        }

    @classmethod
    async def query_by_wallet_id(
        cls,
        session: ProfileSession,
        wallet_id: str,
    ) -> "WalletTokenRecord":
        """Retrieve WalletTokenRecord by wallet_id.
        Args:
            session: the profile session to use
            wallet_id: the wallet_id by which to filter
        """
        tag_filter = {
            **{"wallet_id": wallet_id for _ in [""] if wallet_id},
        }

        result = await cls.query(session, tag_filter)
        if len(result) > 1:
            raise StorageDuplicateError(
                "More than one WalletTokenRecord was found for the given wallet_id"
            )
        if not result:
            raise StorageNotFoundError(
                "No WalletTokenRecord found for the given wallet_id"
            )
        return result[0]


class WalletTokenRecordSchema(BaseRecordSchema):
    """Multitenant Provider Wallet Token(s) Record Schema."""

    class Meta:
        """WalletTokenSchema Meta."""

        model_class = "WalletTokenRecord"
        unknown = EXCLUDE

    wallet_token_id = fields.Str(
        required=True,
        description="Wallet Token Record identifier",
        example=UUIDFour.EXAMPLE,
    )

    wallet_id = fields.Str(
        required=False,
        description="Wallet Record identifier",
        example=UUIDFour.EXAMPLE,
    )
