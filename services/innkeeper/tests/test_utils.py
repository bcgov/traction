from api.utils import hash_password, check_password

PASSWORD = "password"


def test_hash_password():
    hashed_password = hash_password(PASSWORD)
    assert check_password(PASSWORD, hashed_password)
