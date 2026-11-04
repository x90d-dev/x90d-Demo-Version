from cmd_chat import format_banner, parse_command


def test_parse_plain_message():
    parsed = parse_command("jelaskan feature dalam machine learning")

    assert parsed["type"] == "message"
    assert parsed["message"] == "jelaskan feature dalam machine learning"


def test_parse_mode_alias_coding():
    parsed = parse_command("/mode developer")

    assert parsed == {"type": "mode", "mode": "coding"}


def test_parse_agent_alias():
    parsed = parse_command("/agent agen")

    assert parsed == {"type": "agent", "agent_profile": "agent"}


def test_parse_clear_and_exit_commands():
    assert parse_command("/clear")["type"] == "clear"
    assert parse_command("/exit")["type"] == "exit"


def test_parse_status_keeps_current_values():
    parsed = parse_command("/status", current_mode="coding", current_agent="agent")

    assert parsed["type"] == "status"
    assert parsed["mode"] == "coding"
    assert parsed["agent_profile"] == "agent"


def test_parse_unknown_mode_returns_error():
    parsed = parse_command("/mode berat")

    assert parsed["type"] == "error"
    assert "Mode tidak dikenal" in parsed["message"]


def test_banner_mentions_cmd_chat():
    banner = format_banner()

    assert "CoreChiperAgent CMD Chat" in banner
    assert "/help" in banner
