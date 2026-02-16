from modules.system_tools import SystemTools


def test_system_info_message() -> None:
    system_tools = SystemTools()
    message = system_tools.system_info()
    assert "Permintaan system info diterima" in message