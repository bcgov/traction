
from typing import List, Optional

from marshmallow.utils import EXCLUDE

from aries_cloudagent.wallet.models.wallet_record import WalletRecord, WalletRecordSchema



class TokensWalletRecord(WalletRecord):
    class Meta:
        """TokensWalletRecord metadata."""

        schema_class = "TokensWalletRecordSchema"

    def __init__(
        self,
        *,
        wallet_id: str = None,
        key_management_mode: str = None,
        settings: dict = None,
        # MTODO: how to make this a tag without making it
        # a constructor param
        wallet_name: str = None,
        jwt_iat: Optional[int] = None,
        issued_at_claims: Optional[List] = [],
        **kwargs,
    ):
        """Initialize a new TokensWalletRecord."""
        super().__init__(wallet_id=wallet_id, key_management_mode=key_management_mode, settings=settings, wallet_name=wallet_name, jwt_iat=jwt_iat, **kwargs)
        self._issued_at_claims = issued_at_claims
    
    @property
    def issued_at_claims(self):
        return self._issued_at_claims

    def add_issued_at_claims(self, iat):
        self._issued_at_claims.append(iat)


class TokensWalletRecordSchema(WalletRecordSchema):
    """Schema to allow serialization/deserialization of record."""

    class Meta:
        """TokensWalletRecord metadata."""

        model_class = "TokensWalletRecord"
        unknown = EXCLUDE