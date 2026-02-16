import psutil

from modules.system_tools import SystemTools


def test_system_info_message() -> None:
    class DummyMemory:
        total = 8 * 1024**3
        used = 4 * 1024**3
        percent = 50.0

    class DummyProcess:
        def __init__(self, name: str) -> None:
            self.info = {"name": name}

    original_cpu_percent = psutil.cpu_percent
    original_virtual_memory = psutil.virtual_memory
    original_process_iter = psutil.process_iter

    psutil.cpu_percent = lambda interval=0.0: 33.3
    psutil.virtual_memory = lambda: DummyMemory()
    psutil.process_iter = lambda attrs: [DummyProcess("chrome.exe"), DummyProcess("code.exe")]

    system_tools = SystemTools()
    try:
        message = system_tools.system_info()
    finally:
        psutil.cpu_percent = original_cpu_percent
        psutil.virtual_memory = original_virtual_memory
        psutil.process_iter = original_process_iter

    assert "Informasi Sistem" in message
    assert "CPU Usage: 33.3%" in message
    assert "RAM Usage: 50.0%" in message
    assert "chrome.exe" in message
    assert "code.exe" in message