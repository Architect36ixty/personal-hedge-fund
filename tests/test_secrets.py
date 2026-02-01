import os
from agents.common.secrets import get_secret


def test_get_secret_optional():
    # Ensure optional returns None when not set
    os.environ.pop("SOME_MISSING_SECRET", None)
    assert get_secret("SOME_MISSING_SECRET", required=False) is None


def test_get_secret_required_raises():
    os.environ.pop("SOME_MISSING_SECRET2", None)
    try:
        get_secret("SOME_MISSING_SECRET2", required=True)
        assert False, "Expected ValueError"
    except ValueError:
        assert True
