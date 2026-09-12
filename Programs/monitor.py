from __future__ import annotations
import os
import platform
import shutil
import time
import subprocess
from pathlib import Path

PKGNAME = "CoreOS.Monitor"
PKGVER = "2.0"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def format_bytes(value: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} PB"


def get_cpu_usage() -> float:
    """Get CPU usage percentage"""
    try:
        if os.name == "nt":
            # Windows: Use wmic to get CPU load
            result = subprocess.check_output(
                "wmic cpu get loadpercentage",
                shell=True,
                text=True,
                stderr=subprocess.STDOUT
            )
            for line in result.splitlines():
                line = line.strip()
                if line and line.isdigit():
                    return float(line)
        else:
            # Linux: Read from /proc/stat
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                parts = line.split()
                if parts[0] == 'cpu':
                    user = int(parts[1])
                    nice = int(parts[2])
                    system = int(parts[3])
                    idle = int(parts[4])
                    iowait = int(parts[5]) if len(parts) > 5 else 0
                    total = user + nice + system + idle + iowait
                    idle_total = idle + iowait
                    if total > 0:
                        return ((total - idle_total) / total) * 100
    except Exception:
        pass
    return 0.0


def get_memory_usage() -> tuple[str, str, float]:
    """Get memory usage (used, total, percentage)"""
    try:
        if os.name == "nt":
            try:
                import ctypes

                class MemoryStatus(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                status = MemoryStatus()
                status.dwLength = ctypes.sizeof(status)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                    total = status.ullTotalPhys
                    free = status.ullAvailPhys
                    used = total - free
                    percentage = status.dwMemoryLoad
                    return format_bytes(used), format_bytes(total), percentage
            except Exception:
                pass

            try:
                result = subprocess.check_output(
                    "wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value",
                    shell=True,
                    text=True,
                    stderr=subprocess.STDOUT
                )
                total = None
                free = None
                for line in result.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("TotalVisibleMemorySize="):
                        total = int(line.split("=", 1)[1].strip()) * 1024
                    elif line.startswith("FreePhysicalMemory="):
                        free = int(line.split("=", 1)[1].strip()) * 1024
                if total is not None and free is not None:
                    used = total - free
                    percentage = (used / total) * 100
                    return format_bytes(used), format_bytes(total), percentage
            except Exception:
                pass
        else:
            # Linux: Read from /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total = None
                available = None
                for line in lines:
                    if line.startswith('MemTotal:'):
                        total = int(line.split()[1]) * 1024
                    elif line.startswith('MemAvailable:'):
                        available = int(line.split()[1]) * 1024
                    if total and available:
                        break
                
                if total and available:
                    used = total - available
                    percentage = (used / total) * 100
                    return format_bytes(used), format_bytes(total), percentage
    except Exception:
        pass
    
    return "Unknown", "Unknown", 0.0


def get_storage_usage() -> tuple[str, str, float]:
    """Get storage usage (used, total, percentage)"""
    try:
        mem = shutil.disk_usage('.')
        percentage = (mem.used / mem.total) * 100
        return format_bytes(mem.used), format_bytes(mem.total), percentage
    except Exception:
        pass
    return "Unknown", "Unknown", 0.0


def main() -> None:
    clear_screen()
    print("CoreOS Monitor")
    print("Press Ctrl+C to exit")
    try:
        while True:
            clear_screen()
            print("=" * 50)
            print("CoreOS System Monitor")
            print("=" * 50)
            
            # CPU Info
            cpu_usage = get_cpu_usage()
            cpu_cores = os.cpu_count() or 1
            print(f"\nCPU:")
            print(f"  Cores: {cpu_cores}")
            print(f"  Usage: {cpu_usage:.1f}%")
            
            # Memory Info
            mem_used, mem_total, mem_percent = get_memory_usage()
            print(f"\nMemory (RAM):")
            print(f"  Used: {mem_used} / {mem_total}")
            print(f"  Usage: {mem_percent:.1f}%")
            
            # Storage Info
            storage_used, storage_total, storage_percent = get_storage_usage()
            print(f"\nStorage:")
            print(f"  Used: {storage_used} / {storage_total}")
            print(f"  Usage: {storage_percent:.1f}%")
            
            print("\n" + "=" * 50)
            print("Press Ctrl+C to exit")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")


if __name__ == "__main__":
    main()
