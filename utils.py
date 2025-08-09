import hashlib
import hmac
from typing import Any, Dict

from sanic.log import logger


def verify_signature(data: Dict[str, "Any"], secret_key: str) -> bool:
    sorted_keys = sorted(data.keys())
    message = "".join(f"{data[key]}" for key in sorted_keys if key != "signature")
    message += secret_key

    logger.info(message)

    expected_signature = hashlib.sha256(message.encode()).hexdigest()

    return hmac.compare_digest(expected_signature, data["signature"])


def hash_password(salt: str, password: str) -> str:
    salted = password + salt
    return hashlib.sha512(salted.encode("utf8")).hexdigest()
