from config import Config

def get_acapy_headers() -> dict:
    return {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": Config.ACAPY_ADMIN_URL_API_KEY
            }