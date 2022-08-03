"""Acapy Service.

This service is for reading data from AcaPy / Wallet.
These calls will NOT return api_client objects, as they have difficulty being marshalled
 through Pydantic and FastAPI, instead they will return a simple JSON object.

"""
import json
import logging
from json import JSONDecodeError
from uuid import UUID

from urllib3 import HTTPResponse

from acapy_client import ApiException
from acapy_client.api.basicmessage_api import BasicmessageApi
from acapy_client.api.connection_api import ConnectionApi
from acapy_client.api.credentials_api import CredentialsApi
from acapy_client.api.did_exchange_api import DidExchangeApi
from acapy_client.api.issue_credential_v1_0_api import IssueCredentialV10Api
from acapy_client.api.ledger_api import LedgerApi
from acapy_client.api.multitenancy_api import MultitenancyApi
from acapy_client.api.out_of_band_api import OutOfBandApi
from acapy_client.api.revocation_api import RevocationApi
from acapy_client.api.wallet_api import WalletApi
from api.api_client_utils import get_api_client
from acapy_client.api.credential_definition_api import CredentialDefinitionApi
from acapy_client.api.endorse_transaction_api import EndorseTransactionApi
from acapy_client.api.schema_api import SchemaApi
from acapy_client.api.present_proof_v1_0_api import PresentProofV10Api

endorse_api = EndorseTransactionApi(api_client=get_api_client())
schema_api = SchemaApi(api_client=get_api_client())
cred_def_api = CredentialDefinitionApi(api_client=get_api_client())
present_proof_api = PresentProofV10Api(api_client=get_api_client())
issue_cred_v10_api = IssueCredentialV10Api(api_client=get_api_client())
revoc_api = RevocationApi(api_client=get_api_client())
basicmessage_api = BasicmessageApi(api_client=get_api_client())
connection_api = ConnectionApi(api_client=get_api_client())
did_exchange_api = DidExchangeApi(api_client=get_api_client())
out_of_band_api = OutOfBandApi(api_client=get_api_client())
credentials_api = CredentialsApi(api_client=get_api_client())
ledger_api = LedgerApi(api_client=get_api_client())
wallet_api = WalletApi(api_client=get_api_client())
multitenancy_api = MultitenancyApi(api_client=get_api_client())

logger = logging.getLogger(__name__)


def get_connection_json(connection_id: UUID):
    logger.info(f"> get_connection_json({connection_id})")
    try:
        response = connection_api.connections_conn_id_get(
            conn_id=str(connection_id), _preload_content=False
        )
        result = response_to_json(response, "connections_conn_id_get")
        logger.info(f"< get_connection_json({connection_id}): {result is not None}")
        return result
    except ApiException:
        logger.error(f"! get_connection_json({connection_id})", exc_info=True)


def get_presentation_exchange_json(pres_exch_id: UUID):
    logger.info(f"> get_presentation_exchange_json({pres_exch_id})")
    try:
        response = present_proof_api.present_proof_records_pres_ex_id_get(
            pres_ex_id=str(pres_exch_id), _preload_content=False
        )
        result = response_to_json(response, "present_proof_records_pres_ex_id_get")
        logger.info(
            f"< get_presentation_exchange_json({pres_exch_id}): {result is not None}"
        )
        return result
    except ApiException:
        logger.error(f"! get_presentation_exchange_json({pres_exch_id})", exc_info=True)


def get_credential_exchange_json(cred_ex_id: UUID):
    logger.info(f"> get_credential_exchange_json({cred_ex_id})")
    try:
        response = issue_cred_v10_api.issue_credential_records_cred_ex_id_get(
            cred_ex_id=str(cred_ex_id), _preload_content=False
        )
        result = response_to_json(response, "issue_credential_records_cred_ex_id_get")
        logger.info(
            f"< get_credential_exchange_json({cred_ex_id}): {result is not None}"
        )
        return result
    except ApiException:
        logger.error(f"! get_credential_exchange_json({cred_ex_id})", exc_info=True)


def get_credential_json(credential_id: str):
    logger.info(f"> get_credential_json({credential_id})")
    try:
        response = credentials_api.credential_credential_id_get(
            credential_id=credential_id, _preload_content=False
        )
        result = response_to_json(response, "credential_credential_id_get")
        logger.info(f"< get_credential_json({credential_id}): {result is not None}")
        return result
    except ApiException:
        logger.error(f"! get_credential_json({credential_id})", exc_info=True)


def response_to_json(response: HTTPResponse, method_name: str | None = "api"):
    try:
        logger.debug(f" {method_name} response = {response}")
        result = json.loads(response.data.decode("utf-8"))
        logger.debug(f" {method_name} json = {result}")
        return result
    except JSONDecodeError:
        logger.error("! response_to_json", exc_info=True)
        return None
