from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(input_pswd: str, stored_hash: str) -> bool:
    try:
        return ph.verify(stored_hash, input_pswd)
    except VerifyMismatchError:
        return False