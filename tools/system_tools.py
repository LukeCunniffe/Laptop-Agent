import platform
import shutil
from pathlib import Path

def get_system_info() -> dict:
    """Return basic information about the computer."""

    return {
            "operating_system": platform.system(),
            "os_version": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            }

def get_disk_usage() -> dict:
    """Return disk usage information for the home filesystem."""

    total, used, free = shutil.disk_usage(Path.home())

    gb = 1024 ** 3

    return {
            "total_gb": round(total / gb, 2),
            "used_gb": round(used / gb, 2),
            "free_gb": round(free / gb, 2),
            "percent_used": round((used / total) * 100, 1),
            }
