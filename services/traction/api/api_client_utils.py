from acapy_client_074.api_client import ApiClient
from acapy_client_074.configuration import Configuration

from api.core.config import settings


def get_api_client():
    configuration = Configuration(host=settings.ACAPY_ADMIN_URL)
    api_client = ApiClient(configuration=configuration)
    return api_client
