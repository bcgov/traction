import json
import requests
import pprint
import time

from behave import *
from starlette import status

from v1_api import *
from acapy_wrapper import list_credentials as acapy_wrapper_list_credentials


@step('"{holder}" will have a credential_offer from "{issuer}"')
def step_impl(context, holder: str, issuer: str):
    params = {}
    response = list_holder_credentials(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json

    contact_id = context.config.userdata[holder]["connections"][issuer]["contact_id"]

    assert resp_json["items"][0]["contact"]["contact_id"] == contact_id
    assert resp_json["items"][0]["state"] == "offer_received"

    context.config.userdata[holder]["cred_offers"] = [a for a in resp_json["items"]]


@step('"{holder}" will accept credential_offer from "{issuer}"')
def step_impl(context, holder, issuer):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]

    payload = {}
    if context.table:
        for row in context.table:
            attribute = row["attribute"]
            value = row["value"]
            if attribute == "tags":
                value = row["value"].split(",")
            payload[attribute] = value

    response = accept_holder_credential(context, holder, holder_credential_id, payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["state"] == "request_sent", resp_json
    time.sleep(2)


@step('"{holder}" will reject credential_offer from "{issuer}"')
def step_impl(context, holder: str, issuer: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    payload = {"rejection_comment": "rejecting offer for test reasons"}
    response = reject_holder_credential(context, holder, holder_credential_id, payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["state"] == "offer_received", resp_json
    assert resp_json["item"]["status"] == "Rejected", resp_json
    assert (
        resp_json["item"]["rejection_comment"] == payload["rejection_comment"]
    ), resp_json
    time.sleep(2)


@step('"{holder}" will have a holder credential with status "{cred_status}"')
def step_impl(context, holder: str, cred_status: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    response = get_holder_credential(context, holder, holder_credential_id)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["status"] == cred_status, resp_json


@step('"{prover}" will have a present-proof request for "{schema_name}"')
def step_impl(context, prover: str, schema_name: str):

    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/credentials/holder/request",
        headers=context.config.userdata[prover]["auth_headers"],
    )

    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json) == 1, resp_json
    assert resp_json[0]["presentation"]["present_role"] == "holder", resp_json[0]

    # update presentation_requests list
    context.config.userdata[prover].setdefault("presentation_requests", resp_json)


@step(
    '"{prover}" will have credentials to satisfy the present-proof request for "{schema_name}"'
)
def step_impl(context, prover: str, schema_name: str):

    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/credentials/holder/creds-for-request?pres_req_id="
        + context.config.userdata[prover]["presentation_requests"][0]["presentation"][
            "id"
        ],
        headers=context.config.userdata[prover]["auth_headers"],
    )

    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json) == 1, resp_json


@step(
    '"{prover}" sends the presentation in response to the request for "{schema_name}"'
)
def step_impl(context, prover: str, schema_name: str):

    pres = context.config.userdata[prover]["presentation_requests"][0]["presentation"]
    cred_id = context.config.userdata[prover]["credentials"][schema_name]["referent"]

    # hard code attr_0,
    body = {
        "requested_attributes": {"attr_0": {"cred_id": cred_id, "revealed": True}},
        "requested_predicates": {},
        "self_attested_attributes": {},
    }

    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/credentials/holder/present-credential?pres_req_id="
        + pres["id"],
        json=body,
        headers=context.config.userdata[prover]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__


@step('"{holder}" loads credentials')
def step_impl(context, holder: str):

    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v0/credentials/holder",
        headers=context.config.userdata[holder]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)

    creds = {c["schema_id"].split(":")[2]: c for c in resp_json}

    context.config.userdata[holder].setdefault("credentials", creds)
    pprint.pp(context.config.userdata[holder]["credentials"])


@step('"{holder}" will have {count:d} holder credential(s)')
def step_impl(context, holder: str, count: int):
    params = {}
    response = list_holder_credentials(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["total"] == count, resp_json


@step('"{holder}" can find holder credential by alias "{alias}"')
def step_impl(context, holder: str, alias: str):
    params = {"alias": alias}
    response = list_holder_credentials(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["alias"] == alias


@step('"{holder}" can find holder credential by tags "{tags}"')
def step_impl(context, holder: str, tags: str):
    params = {"tags": tags}
    response = list_holder_credentials(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    _tags = [x.strip() for x in tags.split(",")]
    for t in _tags:
        assert t in resp_json["items"][0]["tags"]


@step('"{holder}" can get holder credential by holder_credential_id')
def step_impl(context, holder: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    response = get_holder_credential(context, holder, holder_credential_id)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["holder_credential_id"] == holder_credential_id


@step('"{holder}" can update holder credential')
def step_impl(context, holder: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    payload = {"holder_credential_id": holder_credential_id}

    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        payload[attribute] = value

    response = update_holder_credential(context, holder, holder_credential_id, payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["holder_credential_id"] == holder_credential_id
    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        assert item[attribute] == value


@step('"{holder}" can soft delete holder credential')
def step_impl(context, holder: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    response = delete_holder_credential(context, holder, holder_credential_id)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["holder_credential_id"] == holder_credential_id
    assert item["deleted"]
    assert item["status"] == "Deleted"

    response = acapy_wrapper_list_credentials(context, holder)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    pprint.pp(resp_json)


@step('"{holder}" can hard delete holder credential')
def step_impl(context, holder: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    pprint.pp(context.config.userdata[holder]["cred_offers"][0])
    params = {"hard": True}
    response = delete_holder_credential(context, holder, holder_credential_id, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item is None


@step('"{holder}" has {count:d} credential(s) in wallet')
def step_impl(context, holder: str, count: int):
    response = acapy_wrapper_list_credentials(context, holder)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    results = resp_json["results"]
    assert len(results) == count, resp_json


@then('"{holder}" cannot find holder credential by alias "{alias}"')
def step_impl(context, holder: str, alias: str):
    params = {"alias": alias}
    response = list_holder_credentials(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@step('"{holder}" cannot get holder credential by holder_credential_id')
def step_impl(context, holder: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    response = get_holder_credential(context, holder, holder_credential_id)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__


@step('"{holder}" can find holder credential by alias "{alias}" with deleted flag')
def step_impl(context, holder: str, alias: str):
    params = {"alias": alias, "deleted": True}
    response = list_holder_credentials(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["alias"] == alias
    assert resp_json["items"][0]["deleted"]
    assert resp_json["items"][0]["status"] == "Deleted"


@step('"{holder}" cannot find holder credential by alias "{alias}" with deleted flag')
def step_impl(context, holder: str, alias: str):
    params = {"alias": alias, "deleted": True}
    response = list_holder_credentials(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@step('"{holder}" can get holder credential with deleted flag')
def step_impl(context, holder: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    params = {"deleted": True}
    response = get_holder_credential(context, holder, holder_credential_id, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["holder_credential_id"] == holder_credential_id
    assert resp_json["item"]["deleted"]
    assert resp_json["item"]["status"] == "Deleted"


@step('"{holder}" cannot get holder credential with deleted flag')
def step_impl(context, holder: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    params = {"deleted": True}
    response = get_holder_credential(context, holder, holder_credential_id, params)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__


@step('"{holder}" cannot reject an accepted offer')
def step_impl(context, holder: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    response = reject_holder_credential(context, holder, holder_credential_id)
    assert response.status_code == status.HTTP_409_CONFLICT, response.__dict__


@step('"{holder}" cannot accept an accepted offer')
def step_impl(context, holder: str):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0][
        "holder_credential_id"
    ]
    response = accept_holder_credential(context, holder, holder_credential_id)
    assert response.status_code == status.HTTP_409_CONFLICT, response.__dict__


@step('"{holder}" will have a holder presentation with status "{pres_status}"')
def step_impl(context, holder: str, pres_status: str):
    params = {"status": pres_status}
    response = list_holder_presentations(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    pprint.pp(resp_json)
    assert resp_json["count"] == 1, resp_json
    # store result, use for update and delete
    context.config.userdata[holder].setdefault(
        "holder_presentations", resp_json["items"]
    )


@then('"{holder}" can update holder presentation')
def step_impl(context, holder: str):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    payload = {"holder_presentation_id": holder_presentation_id}

    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        payload[attribute] = value

    response = update_holder_presentation(
        context, holder, holder_presentation_id, payload
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["holder_presentation_id"] == holder_presentation_id
    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        assert item[attribute] == value


@step('"{holder}" can soft delete holder presentation')
def step_impl(context, holder: str):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    response = delete_holder_presentation(context, holder, holder_presentation_id)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["holder_presentation_id"] == holder_presentation_id
    assert item["deleted"]
    assert item["status"] == "Deleted"


@step('"{holder}" will have {count:d} holder presentation(s)')
def step_impl(context, holder: str, count: int):
    params = {}
    response = list_holder_presentations(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["total"] == count, resp_json
    # store result, use for update and delete
    context.config.userdata[holder].setdefault(
        "holder_presentations", resp_json["items"]
    )


@step('"{holder}" can find holder presentation by alias "{alias}"')
def step_impl(context, holder: str, alias: str):
    params = {"alias": alias}
    response = list_holder_presentations(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["alias"] == alias


@step('"{holder}" can find holder presentation by tags "{tags}"')
def step_impl(context, holder: str, tags: str):
    params = {"tags": tags}
    response = list_holder_presentations(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    _tags = [x.strip() for x in tags.split(",")]
    for t in _tags:
        assert t in resp_json["items"][0]["tags"]


@then('"{holder}" cannot find holder presentation by alias "{alias}"')
def step_impl(context, holder: str, alias: str):
    params = {"alias": alias}
    response = list_holder_presentations(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@step('"{holder}" cannot get holder presentation by holder_presentation_id')
def step_impl(context, holder: str):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    response = get_holder_presentation(context, holder, holder_presentation_id)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__


@step('"{holder}" can find holder presentation by alias "{alias}" with deleted flag')
def step_impl(context, holder: str, alias: str):
    params = {"alias": alias, "deleted": True}
    response = list_holder_presentations(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["alias"] == alias
    assert resp_json["items"][0]["deleted"]
    assert resp_json["items"][0]["status"] == "Deleted"


@step('"{holder}" cannot find holder presentation by alias "{alias}" with deleted flag')
def step_impl(context, holder: str, alias: str):
    params = {"alias": alias, "deleted": True}
    response = list_holder_presentations(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@step('"{holder}" can get holder presentation with deleted flag')
def step_impl(context, holder: str):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    params = {"deleted": True}
    response = get_holder_presentation(context, holder, holder_presentation_id, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["holder_presentation_id"] == holder_presentation_id
    assert resp_json["item"]["deleted"]
    assert resp_json["item"]["status"] == "Deleted"


@step('"{holder}" cannot get holder presentation with deleted flag')
def step_impl(context, holder: str):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    params = {"deleted": True}
    response = get_holder_presentation(context, holder, holder_presentation_id, params)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__


@step('"{holder}" can find {count:d} credential(s) for holder presentation')
def step_impl(context, holder: str, count: int):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    response = list_credentials_for_request(context, holder, holder_presentation_id)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    pprint.pp(resp_json)
    assert resp_json["total"] == count, resp_json
    # store result, use for update and delete
    context.config.userdata[holder].setdefault(
        "holder_presentations_credentials", resp_json["items"]
    )


@then('"{holder}" will reject presentation from "{alias}"')
def step_impl(context, holder: str, alias: str):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    payload = {"rejection_comment": "rejecting request for test reasons"}
    if context.table:
        for row in context.table:
            attribute = row["attribute"]
            value = row["value"]
            if attribute == "tags":
                value = row["value"].split(",")
            payload[attribute] = value

    response = reject_holder_presentation(
        context, holder, holder_presentation_id, payload
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["state"] == "request_received", resp_json
    assert item["status"] == "Rejected", resp_json
    assert item["rejection_comment"] == payload["rejection_comment"], resp_json

    if context.table:
        for row in context.table:
            attribute = row["attribute"]
            value = row["value"]
            if attribute == "tags":
                value = row["value"].split(",")

            assert item[attribute] == value


@then('"{holder}" will send presentation from request for "{schema_name}"')
def step_impl(context, holder: str, schema_name: str):
    holder_presentation_id, response = send_valid_presentation(context, holder)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["state"] == "presentation_sent", resp_json
    assert item["presentation"] is not None, resp_json

    if context.table:
        for row in context.table:
            attribute = row["attribute"]
            value = row["value"]
            if attribute == "tags":
                value = row["value"].split(",")

            assert item[attribute] == value


@step('"{holder}" can get holder presentation by holder_presentation_id')
def step_impl(context, holder: str):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    params = {"acapy": True}
    response = get_holder_presentation(context, holder, holder_presentation_id, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    pprint.pp(resp_json)
    assert resp_json["item"]["holder_presentation_id"] == holder_presentation_id
    assert resp_json["item"]["acapy"] is not None, resp_json
    assert resp_json["item"]["acapy"]["presentation_exchange"] is not None, resp_json
    assert resp_json["item"]["presentation"] is not None, resp_json


@step('"{holder}" cannot reject an sent presentation')
def step_impl(context, holder: str):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    response = reject_holder_presentation(context, holder, holder_presentation_id)
    assert response.status_code == status.HTTP_409_CONFLICT, response.__dict__


@step('"{holder}" cannot send an sent presentation')
def step_impl(context, holder: str):
    holder_presentation_id, response = send_valid_presentation(context, holder)
    assert response.status_code == status.HTTP_409_CONFLICT, response.__dict__


def send_valid_presentation(context, holder):
    holder_presentation_id = context.config.userdata[holder]["holder_presentations"][0][
        "holder_presentation_id"
    ]
    cred_id = context.config.userdata[holder]["holder_presentations_credentials"][0][
        "cred_info"
    ]["referent"]
    # hard code attr_0,
    presentation = {
        "requested_attributes": {"attr_0": {"cred_id": cred_id, "revealed": True}},
        "requested_predicates": {},
        "self_attested_attributes": {},
    }
    payload = {
        "holder_presentation_id": holder_presentation_id,
        "presentation": presentation,
    }
    if context.table:
        for row in context.table:
            attribute = row["attribute"]
            value = row["value"]
            if attribute == "tags":
                value = row["value"].split(",")
            payload[attribute] = value
    response = send_holder_presentation(
        context, holder, holder_presentation_id, payload
    )
    return holder_presentation_id, response
