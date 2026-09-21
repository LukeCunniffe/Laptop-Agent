import platform
import shutil
import time
import psutil
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

def get_system_status() -> dict:
    """Return a general snapshot of laptop system status."""

    memory = psutil.virtual_memory()

    battery = psutil.sensors_battery()

    boot_time = psutil.boot_time()
    uptime_seconds = int(
            time.time() - boot_time
            )

    uptime_hours = round(
            uptime_seconds / 3600,
            1
            )

    cpu_percent = psutil.cpu_percent(
            interval=0.5
            )

    load_1, load_5, load_15 = psutil.getloadavg()

    result = {
            "success": True,
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": round(
                    memory.total / (1024 ** 3),
                    2
                    ),
                "used_gb": round(
                    memory.used / (1024 ** 3),
                    2
                    ),
                "available_gb": round(
                    memory.available / (1024 ** 3),
                    2
                    ),
                "percent_used": memory.percent,
                },
            "uptime_hours": uptime_hours,
            "load_average": {
                "1_minute": round(load_1, 2),
                "5_minutes": round(load_5, 2),
                "15_minutes": round(load_15, 2),
                },
            }

    if battery is not None:
        result["battery"] = {
                "percent": battery.percent,
                "charging": battery.power_plugged,
                }
    else:
        result["battery"] = {
                "available": False,
                }

    return result
