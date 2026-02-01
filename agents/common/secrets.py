import os
from typing import Optional
from dotenv import load_dotenv

# Load local .env for developer convenience. In production, prefer real secret stores.
load_dotenv()


def get_secret(name: str, required: bool = True) -> Optional[str]:
    """Retrieve a secret from environment. Do NOT log secret values.

    - If required and missing, raises a ValueError.
    - Returns None if optional and unset.
    """
    val = os.environ.get(name)
    if required and not val:
        raise ValueError(f"Required secret '{name}' is not set in environment")
    return val
