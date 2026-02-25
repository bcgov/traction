"""Bcrypt 5.x compatibility: limit password to 72 bytes to avoid ValueError."""

import logging

# Bcrypt 5.0+ raises ValueError for passwords longer than 72 bytes
BCRYPT_MAX_PASSWORD_BYTES = 72

LOGGER = logging.getLogger(__name__)


def limit_for_bcrypt(password_bytes: bytes) -> bytes:
    """Truncate password to 72 bytes for bcrypt 5.x compatibility."""
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        LOGGER.warning(
            "Password or key input exceeded 72 bytes (bcrypt limit); truncated to 72 bytes for hashing. "
            "Original length: %d bytes.",
            len(password_bytes),
        )
        return password_bytes[:BCRYPT_MAX_PASSWORD_BYTES]
    return password_bytes
