import platform
import shutil
import time
import socket
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

def get_network_status() -> dict:
    """Return basic network interface and connection information"""

    interfaces = []

    addresses = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for interface_name, interface_addresses in addresses.items():

        interface_stat = stats.get(interface_name)

        if interface_stat is None:
            continue

        interface_info = {
                "name": interface_name,
                "up": interface_stat.isup,
                "speed_mbps": interface_stat.speed,
                "ipv4": [],
                "ipv6": [],
                }

        for address in interface_addresses:

            if address.family == socket.AF_INET:
                interface_info["ipv4"].append(
                        address.address
                        )

            elif address.family == socket.AF_INET6:
                interface_info["ipv6"].append(
                        address.address
                        )

            interfaces.append(interface_info)

    active_interfaces = [
            interface
            for interface in interfaces
            if interface["up"]
            ]

    return {
            "success": True,
            "hostname": socket.gethostname(),
            "connected": any(
                interface["up"]
                and interface["name"] != "lo"
                for interface in interfaces
                ),
            "interfaces": active_interfaces,
            }

def get_process_status(
        process_name: str = "",
        limit: int = 10,
        sort_by: str = "memory",
        ) -> dict:
    """Inspect currently running processes."""

    limit = min(max(limit, 1), 20)

    if sort_by not in {
            "cpu",
            "memory",
            }:
        sort_by = "memory"

    process_objects = []

    # Prime CPU measurements.
    for process in psutil.process_iter():
        try:
            process.cpu_percent(
                    interval=None
                    )
            process_objects.append(
                    process
                    )

        except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                ):
            continue

    time.sleep(0.2)

    processes = []

    for process in process_objects:

        try:
            info = process.as_dict(
                    attrs=[
                        "pid",
                        "name",
                        "status",
                        "memory_percent",
                        ]
                    )

            name = info.get("name") or ""

            if (
                    process_name
                    and process_name.lower()
                    not in name.lower()
                    ):
                continue

            processes.append(
                    {
                        "pid": info["pid"],
                        "name": name,
                        "status": info["status"],
                        "cpu_percent": round(
                            process.cpu_percent(
                                interval=None
                                ),
                            1,
                            ),
                        "memory_percent": round(
                            info["memory_percent"]
                            or 0,
                            1,
                            ),
                        }
                    )

        except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                ):
            continue

    sort_key = (
            "cpu_percent"
            if sort_by == "cpu"
            else "memory_percent"
            )

    processes.sort(
            key=lambda process: process[
                sort_key
                ],
            reverse=True,
            )

    return {
            "success": True,
            "filter": (
                process_name
                if process_name
                else None
                ),
            "sort_by": sort_by,
            "count": len(processes),
            "processes": processes[:limit],
            }
