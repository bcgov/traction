import base64
import json
import logging
import urllib
from urllib.parse import urlparse, parse_qs, unquote_plus, urlunparse, ParseResultBytes
from aiohttp import (
    ClientSession,
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)

invitation_param_names = ["c_i", "d_m", "oob"]

CONNECTION_INVITATION_TYPES = [
    "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/invitation",
    "https://didcomm.org/connections/1.0/invitation",
]

OOB_INVITATION_TYPES = [
    "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/out-of-band/1.0/invitation",
    "https://didcomm.org/out-of-band/1.0/invitation",
]


class CheckInvitationResult(BaseModel):
    invitation: dict = None
    invitation_block: str = None
    label: str = None


class ParseInvitationResult(CheckInvitationResult):
    oob: bool = False
    parsed: bool = False


async def check_invitation(invitation_uri: str) -> CheckInvitationResult:
    url = uri_to_url(invitation_uri, True)
    if url:
        invitation_block = parse_invitation_block(url)
        if not invitation_block:
            invitation_block = await parse_invitation_block_from_redirect(url)

        invitation = parse_invitation(invitation_block)
        logger.info(invitation)

        return CheckInvitationResult(**invitation.dict())

    return None


async def parse_invitation_block_from_redirect(url):
    async with ClientSession() as client_session:
        async with client_session.get(urlunparse(url), allow_redirects=False) as resp:
            location = resp.headers.get("location")
            if location:
                location_url = uri_to_url(location, False)
                if location_url:
                    return parse_invitation_block(location_url)

    return None


def parse_invitation(invitation_block: str) -> ParseInvitationResult:
    result = ParseInvitationResult()

    if invitation_block:
        decoded_block = decode_invitation_block(invitation_block)
        block = json.loads(decoded_block)
        result.invitation = block
        result.invitation_block = decoded_block
        invitation_type = block.get("@type")
        if invitation_type in CONNECTION_INVITATION_TYPES:
            result.parsed = True
            result.label = block.get("label")
        elif invitation_type in OOB_INVITATION_TYPES:
            result.parsed = True
            result.label = block.get("label")
            result.oob = True
        else:
            logger.error("unknown invitation type")

    return result


def parse_invitation_block(url):
    qs = parse_qs(url.query)
    for p in invitation_param_names:
        invitation_block = qs.get(p)
        if invitation_block and len(invitation_block) == 1:
            return unquote_plus(invitation_block[0])

    return None


def decode_invitation_block(invitation_block):
    if invitation_block:
        return base64.b64decode(invitation_block).decode("utf-8")

    return None


def uri_to_url(invitation_uri: str, decode: bool | None = False) -> ParseResultBytes:
    result = None

    parsed_url = parse_uri(invitation_uri, decode)

    if parsed_url.scheme == "http" or parsed_url.scheme == "https":
        result = parsed_url
    else:
        # we only care about the query portion of this url
        # so we can parse out the invitation block
        q = parsed_url.query
        result = urlparse(f"https://placeholder.co?{q}") if q else None

    return result


def parse_uri(invitation_uri: str, decode: bool | None = False) -> ParseResultBytes:
    decoded_uri = invitation_uri
    if decode:
        decoded_uri = urllib.parse.unquote(decoded_uri)

    return urlparse(decoded_uri)
