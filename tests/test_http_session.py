from agents.common.http import get_session


def test_session_has_user_agent():
    s = get_session()
    assert "User-Agent" in s.headers
