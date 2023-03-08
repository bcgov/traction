import time

import requests
from random_word import RandomWords

r = RandomWords()
"""
install these dependencies - poetry, pip, whatever...

requests = "^2.28.2"
Random-Word = "^1.0.11"

script is based on running acapy with traction plugins using the default local environment.

see https://github.com/bcgov/traction/tree/develop/scripts
"""
CONFIG = {
    "local": {
        "proxyUrl": "http://localhost:8032",
        "innkeeperTenantId": "innkeeper",
        "innkeeperWalletKey": "change-me",
        "webhookUrl": None,
    }
}

_env = "local"

PROXY_URL = CONFIG[_env]["proxyUrl"]
INNKEEPER_TENANT_ID = CONFIG[_env]["innkeeperTenantId"]
INNKEEPER_WALLET_KEY = CONFIG[_env]["innkeeperWalletKey"]
WEBHOOK_URL = CONFIG[_env]["webhookUrl"]


def wait_a_bit(secs: int = 1):
    total = secs
    print(f"... wait {total} seconds ...")
    time.sleep(total)


if __name__ == "__main__":
    print(f"using {_env} @ {PROXY_URL}\n")
    # ==============================================
    print("\nlog in innkeeper tenant...\n")

    # get innkeeper token
    data = {
        "wallet_key": INNKEEPER_WALLET_KEY,
    }
    res = requests.post(
        f"{PROXY_URL}/multitenancy/tenant/{INNKEEPER_TENANT_ID}/token", json=data
    )
    innkeeper_token = res.json()["token"]
    print(f"innkeeper_token = {innkeeper_token}")

    # ==============================================
    print("\ncreate a reservation (issuer)...\n")

    reservation_name = r.get_random_word()
    print(f"reservation_name = {reservation_name}")
    data = {
        "contact_email": "fake@bad.good",
        "contact_name": reservation_name,
        "contact_phone": "555-5555",
        "tenant_name": reservation_name,
        "tenant_reason": "testing...",
    }
    res = requests.post(f"{PROXY_URL}/multitenancy/reservations", json=data)
    reservation_id = res.json()["reservation_id"]
    print(f"reservation_id = {reservation_id}")

    print("\ninnkeeper approve the reservation...\n")

    data = {
        "state_notes": "go for it",
    }
    innkeeper_headers = {"Authorization": f"Bearer {innkeeper_token}"}
    res = requests.put(
        f"{PROXY_URL}/innkeeper/reservations/{reservation_id}/approve",
        headers=innkeeper_headers,
        json=data,
    )
    reservation_pwd = res.json()["reservation_pwd"]
    print(reservation_pwd)

    print("\ntenant (issuer) check-in and get keys (token)...\n")

    data = {
        "reservation_pwd": reservation_pwd,
    }
    res = requests.post(
        f"{PROXY_URL}/multitenancy/reservations/{reservation_id}/check-in", json=data
    )
    reservation_result = res.json()
    print(f"reservation_result = {reservation_result}")
    issr_token = reservation_result["token"]
    print(f"issr_token = {issr_token}")
    issuer_headers = {"Authorization": f"Bearer {issr_token}"}

    # ==============================================
    print("\ntenant (issuer) connect with endorser...\n")

    data = None
    res = requests.get(
        f"{PROXY_URL}/tenant/endorser-connection", headers=issuer_headers, json=data
    )
    # we expect a 404 not found...
    print(
        f"expect 404 since we do not have an existing connection... {res.status_code} - {res.reason}"
    )

    data = None
    res = requests.post(
        f"{PROXY_URL}/tenant/endorser-connection", headers=issuer_headers, json=data
    )
    set_endorser_connection_result = res.json()
    print(f"set_endorser_connection_result = {set_endorser_connection_result}")

    wait_a_bit(20)

    data = None
    res = requests.get(
        f"{PROXY_URL}/tenant/endorser-connection", headers=issuer_headers, json=data
    )
    # now we expect there to be a connection
    get_endorser_connection_result = res.json()
    print(f"get_endorser_connection_result = {get_endorser_connection_result}")

    # ==============================================
    print("\ntenant (issuer) create public did...\n")

    data = {"method": "sov", "options": {"key_type": "ed25519"}}
    res = requests.post(
        f"{PROXY_URL}/wallet/did/create", headers=issuer_headers, json=data
    )
    wallet_did_create_result = res.json()["result"]
    print(f"wallet_did_create_result = {wallet_did_create_result}")
    wallet_create_did = wallet_did_create_result["did"]
    wallet_create_verkey = wallet_did_create_result["verkey"]
    print(f"wallet_create_did = {wallet_create_did}")
    print(f"wallet_create_verkey = {wallet_create_verkey}")

    # register did
    data = None
    params = {
        "did": wallet_create_did,
        "verkey": wallet_create_verkey,
    }
    res = requests.post(
        f"{PROXY_URL}/tenant/register-public-did", headers=issuer_headers, params=params
    )
    register_public_did_response = res.json()
    print(f"register_public_did_response = {register_public_did_response}")

    wait_a_bit(10)

    # public did
    data = None
    params = {
        "did": wallet_create_did,
    }
    res = requests.post(
        f"{PROXY_URL}/wallet/did/public",
        headers=issuer_headers,
        params=params,
        timeout=120,
    )
    wallet_public_did_response = res.json()
    print(f"wallet_public_did_response = {wallet_public_did_response}")

    wait_a_bit(10)

    # get public did
    res = requests.get(
        f"{PROXY_URL}/wallet/did/public", headers=issuer_headers, json=data
    )
    wallet_public_did_result = res.json()["result"]
    print(f"wallet_public_did_result = {wallet_public_did_result}")
    issuer_public_did = wallet_public_did_result["did"]
    print(f"wallet_public_did = {issuer_public_did}")

    # ==============================================

    wait_a_bit(10)

    print("\ntenant (issuer) create schema...\n")

    # create a schema
    schema_name = r.get_random_word()
    print(f"schema_name = {schema_name}")
    data = {
        "attributes": ["score"],
        "schema_name": schema_name,
        "schema_version": "0.0.1",
    }
    res = requests.post(f"{PROXY_URL}/schemas", headers=issuer_headers, json=data)
    schema_create_response = res.json()
    print(f"schema_create_response = {schema_create_response}")
    schema_id = schema_create_response["sent"]["schema_id"]
    print(f"schema_id = {schema_id}")

    wait_a_bit(30)

    # ==============================================
    print("\ntenant (issuer) create a cred def (revocable)...\n")

    creddef_tag = r.get_random_word()
    print(f"creddef_tag = {creddef_tag}")
    data = {
        "schema_id": schema_id,
        "tag": creddef_tag,
        "revocation_registry_size": 4,
        "support_revocation": True,
    }
    res = requests.post(
        f"{PROXY_URL}/credential-definitions",
        headers=issuer_headers,
        json=data,
        timeout=120,
    )
    creddef_create_response = res.json()
    print(f"creddef_create_response = {creddef_create_response}")
    cred_def_id = creddef_create_response["sent"]["credential_definition_id"]
    print(f"cred_def_id = {cred_def_id}")

    wait_a_bit(30)
    # ==============================================
    print("\ntenant (issuer) create a cred def (non-revocable)...\n")

    creddef_tag = r.get_random_word()
    print(f"creddef_tag = {creddef_tag}")
    data = {
        "schema_id": schema_id,
        "tag": creddef_tag,
        "support_revocation": False,
    }
    res = requests.post(
        f"{PROXY_URL}/credential-definitions", headers=issuer_headers, json=data
    )
    creddef_nr_create_response = res.json()
    print(f"creddef_nr_create_response = {creddef_nr_create_response}")
    nr_cred_def_id = creddef_nr_create_response["sent"]["credential_definition_id"]
    print(f"nr_cred_def_id = {nr_cred_def_id}")

    wait_a_bit(20)

    # ============== HOLDER

    # ==============================================
    print("\ncreate a reservation (holder)...\n")

    reservation_name = r.get_random_word()
    print(f"reservation_name = {reservation_name}")
    data = {
        "contact_email": "fake@bad.good",
        "contact_name": reservation_name,
        "contact_phone": "555-5555",
        "tenant_name": reservation_name,
        "tenant_reason": "testing...",
    }
    res = requests.post(f"{PROXY_URL}/multitenancy/reservations", json=data)
    reservation_id = res.json()["reservation_id"]
    print(f"reservation_id = {reservation_id}")

    print("\ninnkeeper approve the reservation...\n")

    data = {
        "state_notes": "go for it",
    }
    innkeeper_headers = {"Authorization": f"Bearer {innkeeper_token}"}
    res = requests.put(
        f"{PROXY_URL}/innkeeper/reservations/{reservation_id}/approve",
        headers=innkeeper_headers,
        json=data,
    )
    reservation_pwd = res.json()["reservation_pwd"]
    print(reservation_pwd)

    print("\ntenant (holder) check-in and get keys (token)...\n")

    data = {
        "reservation_pwd": reservation_pwd,
    }
    res = requests.post(
        f"{PROXY_URL}/multitenancy/reservations/{reservation_id}/check-in", json=data
    )
    reservation_result = res.json()
    print(f"reservation_result = {reservation_result}")
    hldr_token = reservation_result["token"]
    print(f"hldr_token = {hldr_token}")
    holder_headers = {"Authorization": f"Bearer {hldr_token}"}

    if WEBHOOK_URL:
        print("\ntenant (holder) set webhook url...\n")

        data = {"wallet_webhook_urls": [WEBHOOK_URL]}
        res = requests.put(
            f"{PROXY_URL}/tenant/wallet", headers=holder_headers, json=data
        )
        set_holder_webhook_result = res.json()
        print(f"set_holder_webhook_result = {set_holder_webhook_result}")

    print("\ntenant (holder) connect to issuer via their public did...\n")

    data = None
    res = requests.post(
        f"{PROXY_URL}/didexchange/create-request?their_public_did={issuer_public_did}&alias=issuer&my_label=holder",
        headers=holder_headers,
        json=data,
    )
    set_issuer_connection_result = res.json()
    print(f"set_issuer_connection_result = {set_issuer_connection_result}")
    holder_to_issuer_connection_id = set_issuer_connection_result["connection_id"]
    print(f"holder_to_issuer_connection_id = {holder_to_issuer_connection_id}")

    wait_a_bit(2)

    # get connection with issuer
    res = requests.get(
        f"{PROXY_URL}/connections/{holder_to_issuer_connection_id}",
        headers=holder_headers,
        json=data,
    )
    holder_to_issuer_connection_result = res.json()
    print(f"connection_result = {holder_to_issuer_connection_result}")

    # get issuer's connections
    res = requests.get(f"{PROXY_URL}/connections", headers=issuer_headers, json=data)
    issuer_connections_result = res.json()
    print(f"issuer_connections_result = {issuer_connections_result}")
    issuer_to_holder_connection_id = None
    for conn in issuer_connections_result["results"]:
        if conn.get("their_label") and conn.get("their_label") == "holder":
            issuer_to_holder_connection_id = conn.get("connection_id")
    print(f"issuer_to_holder_connection_id = {issuer_to_holder_connection_id}")
    # =====================

    print("tenant (issuer) make credential offer to holder...\n")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records", headers=issuer_headers, json=data
    )
    issue_credentials_list_result = res.json()
    print(f"issue_credentials_list_result = {issue_credentials_list_result}")

    # DO NOT remove this exchange when done, we want historical record
    data = {
        "auto_issue": True,
        "auto_remove": False,
        "comment": "just testing things out",
        "connection_id": issuer_to_holder_connection_id,
        "cred_def_id": cred_def_id,
        "credential_preview": {
            "@type": "issue-credential/1.0/credential-preview",
            "attributes": [{"name": "score", "value": "99"}],
        },
        "trace": False,
    }
    print("\nsending offer...\n")
    res = requests.post(
        f"{PROXY_URL}/issue-credential/send-offer", headers=issuer_headers, json=data
    )
    send_offer_result = res.json()
    print(f"send_offer_result = {send_offer_result}\n")

    wait_a_bit(5)

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=issuer&state=offer_sent",
        headers=issuer_headers,
        json=data,
    )
    issuer_offer_sent_list_result = res.json()
    print(
        f"issuer_offer_sent_list_result count= {len(issuer_offer_sent_list_result['results'])}"
    )
    print(f"issuer_offer_sent_list_result = {issuer_offer_sent_list_result}")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=holder&state=offer_received",
        headers=holder_headers,
        json=data,
    )
    holder_offer_received_list_result = res.json()
    print(
        f"holder_offer_received_list_result count= {len(holder_offer_received_list_result['results'])}"
    )
    print(f"holder_offer_received_list_result = {holder_offer_received_list_result}")
    credential_offer_exchange_id = holder_offer_received_list_result["results"][0][
        "credential_exchange_id"
    ]
    print(f"credential_offer_exchange_id = {credential_offer_exchange_id}")

    data = None
    res = requests.get(f"{PROXY_URL}/credentials", headers=holder_headers, json=data)
    holder_credentials_list_result = res.json()
    print(
        f"holder_credentials_list_result count= {len(holder_credentials_list_result['results'])}"
    )
    print(f"holder_credentials_list_result = {holder_credentials_list_result}")

    # accept offer
    print("\naccepting offer...\n")
    data = None
    res = requests.post(
        f"{PROXY_URL}/issue-credential/records/{credential_offer_exchange_id}/send-request",
        headers=holder_headers,
        json=data,
    )
    accept_offer_result = res.json()
    print(f"accept_offer_result = {accept_offer_result}\n")

    wait_a_bit(5)

    print("\ncheck storage...\n")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=issuer&state=offer_sent",
        headers=issuer_headers,
        json=data,
    )
    issuer_offer_sent_list_result = res.json()
    print(
        f"issuer_offer_sent_list_result count= {len(issuer_offer_sent_list_result['results'])}"
    )
    print(f"issuer_offer_sent_list_result = {issuer_offer_sent_list_result}")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=holder&state=offer_received",
        headers=holder_headers,
        json=data,
    )
    holder_offer_received_list_result = res.json()
    print(
        f"holder_offer_received_list_result count= {len(holder_offer_received_list_result['results'])}"
    )
    print(f"holder_offer_received_list_result = {holder_offer_received_list_result}")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=issuer",
        headers=issuer_headers,
        json=data,
    )
    issue_credentials_list_result = res.json()
    print(
        f"issue_credentials_list_result count= {len(issue_credentials_list_result['results'])}"
    )
    print(f"issue_credentials_list_result = {issue_credentials_list_result}")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=holder",
        headers=holder_headers,
        json=data,
    )
    holder_issuer_credentials_list_result = res.json()
    print(
        f"holder_issuer_credentials_list_result count= {len(holder_issuer_credentials_list_result['results'])}"
    )
    print(
        f"holder_issuer_credentials_list_result = {holder_issuer_credentials_list_result}"
    )

    data = None
    res = requests.get(f"{PROXY_URL}/credentials", headers=holder_headers, json=data)
    holder_credentials_list_result = res.json()
    print(
        f"holder_credentials_list_result count= {len(holder_credentials_list_result['results'])}"
    )
    print(f"holder_credentials_list_result = {holder_credentials_list_result}")

    print("\ntenant (issuer) check revocation registry...\n")

    data = None
    res = requests.get(
        f"{PROXY_URL}/revocation/registries/created", headers=issuer_headers, json=data
    )
    revoc_registry_list_result = res.json()
    print(
        f"revoc_registry_list_result count= {len(revoc_registry_list_result['rev_reg_ids'])}"
    )
    print(f"revoc_registry_list_result = {revoc_registry_list_result}")

    print("\ntenant (issuer) revoked issued credential...\n")

    # make sure the credential exchange is acked before revoking...
    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=issuer&state=credential_acked",
        headers=issuer_headers,
        json=data,
    )
    acked_issued_credentials_list_result = res.json()
    print(
        f"acked_issued_credentials_list_result count= {len(acked_issued_credentials_list_result['results'])}"
    )
    print(
        f"acked_issued_credentials_list_result = {acked_issued_credentials_list_result}"
    )
    issuer_acked_issued_credential = acked_issued_credentials_list_result["results"][0]
    print(f"issuer_acked_issued_credential = {issuer_acked_issued_credential}")

    cred_ex_id = issuer_acked_issued_credential["credential_exchange_id"]
    cred_rev_id = issuer_acked_issued_credential["revocation_id"]
    rev_reg_id = issuer_acked_issued_credential["revoc_reg_id"]
    data = {
        "comment": "testing revocation...",
        "connection_id": issuer_to_holder_connection_id,
        "rev_reg_id": rev_reg_id,
        "cred_rev_id": cred_rev_id,
        "publish": True,
        "notify": True,
    }
    res = requests.post(
        f"{PROXY_URL}/revocation/revoke", headers=issuer_headers, json=data
    )
    revocation_result = res.json()
    print(f"revocation_result = {revocation_result}")

    wait_a_bit(5)

    # two different ways to make the same call... by cred exchange id
    data = None
    res = requests.get(
        f"{PROXY_URL}/revocation/credential-record?cred_ex_id={cred_ex_id}",
        headers=issuer_headers,
        json=data,
    )
    get_credex_revocation_result = res.json()
    print(f"get_credex_revocation_result (cred_ex_id) = {get_credex_revocation_result}")

    # or by revocation ids
    data = None
    res = requests.get(
        f"{PROXY_URL}/revocation/credential-record?cred_rev_id={cred_rev_id}&rev_reg_id={rev_reg_id}",
        headers=issuer_headers,
        json=data,
    )
    get_credex_revocation_result = res.json()
    print(
        f"get_credex_revocation_result (cred_rev_id & rev_reg_id) = {get_credex_revocation_result}"
    )

    # make sure the credential exchange is acked before revoking...
    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=issuer&state=credential_revoked",
        headers=issuer_headers,
        json=data,
    )
    issuer_revoked_credentials_list_result = res.json()
    print(
        f"issuer_revoked_credentials_list_result count= {len(issuer_revoked_credentials_list_result['results'])}"
    )
    print(
        f"issuer_revoked_credentials_list_result = {issuer_revoked_credentials_list_result}"
    )

    # ======== TEST holder reject!

    # DO NOT remove this exchange when done, we want historical record
    data = {
        "auto_issue": True,
        "auto_remove": False,
        "comment": "you should reject this",
        "connection_id": issuer_to_holder_connection_id,
        "cred_def_id": cred_def_id,
        "credential_preview": {
            "@type": "issue-credential/1.0/credential-preview",
            "attributes": [{"name": "score", "value": "0"}],
        },
        "trace": False,
    }
    print("\nsending offer (to be rejected)...\n")
    res = requests.post(
        f"{PROXY_URL}/issue-credential/send-offer", headers=issuer_headers, json=data
    )
    send_offer_result = res.json()
    print(f"send_offer_result = {send_offer_result}\n")

    wait_a_bit(5)

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=holder&state=offer_received",
        headers=holder_headers,
        json=data,
    )
    holder_offer_received_list_result = res.json()
    print(
        f"holder_offer_received_list_result count= {len(holder_offer_received_list_result['results'])}"
    )
    print(f"holder_offer_received_list_result = {holder_offer_received_list_result}")
    credential_offer_exchange_id = holder_offer_received_list_result["results"][0][
        "credential_exchange_id"
    ]
    print(f"credential_offer_exchange_id = {credential_offer_exchange_id}")

    # reject offer
    print("\nrejecting offer...\n")
    data = {"description": "this is not my score"}
    res = requests.post(
        f"{PROXY_URL}/issue-credential/records/{credential_offer_exchange_id}/problem-report",
        headers=holder_headers,
        json=data,
    )
    reject_offer_result = res.json()
    print(f"reject_offer_result = {reject_offer_result}\n")

    wait_a_bit(5)

    print("\ncheck storage...\n")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=issuer&state=abandoned",
        headers=issuer_headers,
        json=data,
    )
    issuer_abandoned_list_result = res.json()
    print(
        f"issuer_abandoned_list_result count= {len(issuer_abandoned_list_result['results'])}"
    )
    print(f"issuer_abandoned_list_result = {issuer_abandoned_list_result}")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=holder&state=abandoned",
        headers=holder_headers,
        json=data,
    )
    holder_abandoned_list_result = res.json()
    print(
        f"holder_abandoned_list_result count= {len(holder_abandoned_list_result['results'])}"
    )
    print(f"holder_abandoned_list_result = {holder_abandoned_list_result}")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=holder&state=credential_revoked",
        headers=holder_headers,
        json=data,
    )
    holder_revoked_list_result = res.json()
    print(
        f"holder_revoked_list_result count= {len(holder_revoked_list_result['results'])}"
    )
    print(f"holder_revoked_list_result = {holder_revoked_list_result}")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=issuer",
        headers=issuer_headers,
        json=data,
    )
    issue_credentials_list_result = res.json()
    print(
        f"issue_credentials_list_result count= {len(issue_credentials_list_result['results'])}"
    )
    print(f"issue_credentials_list_result = {issue_credentials_list_result}")

    data = None
    res = requests.get(
        f"{PROXY_URL}/issue-credential/records?role=holder",
        headers=holder_headers,
        json=data,
    )
    holder_issuer_credentials_list_result = res.json()
    print(
        f"holder_issuer_credentials_list_result count= {len(holder_issuer_credentials_list_result['results'])}"
    )
    print(
        f"holder_issuer_credentials_list_result = {holder_issuer_credentials_list_result}"
    )
