from acapy_client.api_client import ApiClient
from acapy_client.configuration import Configuration

from api.core.config import settings


def get_api_client():
    configuration = Configuration(host="http://traction-agent:8031")
    api_client = ApiClient(configuration=configuration)
    return api_client
