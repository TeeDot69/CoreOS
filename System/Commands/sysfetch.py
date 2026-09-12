import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.getenv("COREOS_ROOT", str(Path(__file__).resolve().parents[2])))

# ASCII art, dear user you can change this
ASCII_ART = [
    "             )bQQb)             ",
    "     vUUv  )bQQQQQQb)  vUUv     ",
    "   )bQQQQG//GQQQQQQG//GQQQQb)   ",
    " <ZQQQQQQQQQQQQQQQQQQQQQQQQQQZ< ",
    "   )bQQQQQQQQQQQQQQQQQQQQQQb)   ",
    "     )bQQQQQQQQQQQQQQQQQQb)     ",
    " <ZQQQQQQQQQQb)  )bQQQQQQQQQQZ< ",
    "QQQQQQQQQQQb)      )bQQQQQQQQQQQ",
    "QQQQQQQQQQQb)      )bQQQQQQQQQQQ",
    " <ZQQQQQQQQQQb)  )bQQQQQQQQQQZ< ",
    "     )bQQQQQQQQQQQQQQQQQQb)     ",
    "   )bQQQQQQQQQQQQQQQQQQQQQQb)   ",
    " <ZQQQQQQQQQQQQQQQQQQQQQQQQQQZ< ",
    "   )bQQQQG//GQQQQQQG//GQQQQb)   ",
    "     vUUv  )bQQQQQQb)  vUUv     ",
    "             )bQQb)             ",
]


def color(text: str) -> str:
    # Direct color codes like the reference implementation
    return f"\033[38;2;57;159;81m{text}\033[0m"


def format_bytes(value: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} PB"


def get_cpu_name() -> str:
    if os.name == "nt":
        try:
            result = subprocess.check_output("wmic cpu get name", shell=True, text=True, stderr=subprocess.STDOUT)
            for line in result.splitlines():
                if line.strip() and not line.startswith("Name"):
                    return line.strip()
        except Exception:
            pass
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or "Unknown CPU"


def get_memory() -> tuple[str, str]:
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
                    return format_bytes(used), format_bytes(total)
            except Exception:
                pass

            try:
                result = subprocess.check_output(
                    "wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value",
                    shell=True,
                    text=True,
                    stderr=subprocess.STDOUT,
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
                    return format_bytes(used), format_bytes(total)
            except Exception:
                pass
            return "Unknown", "Unknown"

        if os.path.exists("/proc/meminfo"):
            total = None
            free = None
            available = None
            with open("/proc/meminfo", "r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    if line.startswith("MemTotal:"):
                        total = int(line.split()[1]) * 1024
                    elif line.startswith("MemAvailable:"):
                        available = int(line.split()[1]) * 1024
                    elif line.startswith("MemFree:"):
                        free = int(line.split()[1]) * 1024
                    if total is not None and (available is not None or free is not None):
                        break
            if total is not None:
                if available is not None:
                    used = total - available
                    return format_bytes(used), format_bytes(total)
                if free is not None:
                    used = total - free
                    return format_bytes(used), format_bytes(total)

        return "Unknown", "Unknown"
    except Exception:
        return "Unknown", "Unknown"


def get_battery() -> str:
    if os.name == "nt":
        try:
            result = subprocess.check_output(
                "wmic path win32_battery get estimatedchargeremaining",
                shell=True,
                text=True,
                stderr=subprocess.STDOUT
            )
            lines = result.strip().splitlines()
            for line in lines:
                line = line.strip()
                if line and line.isdigit():
                    return f"{line}%"
        except Exception:
            pass
        return "N/A"
    
    # Try multiple battery paths for Linux
    battery_paths = [
        "/sys/class/power_supply/BAT0/capacity",
        "/sys/class/power_supply/BAT1/capacity",
        "/sys/class/power_supply/battery/capacity",
    ]
    
    for path in battery_paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                value = handle.read().strip()
                if value.isdigit():
                    return f"{value}%"
        except Exception:
            continue
    
    # Try using upower as fallback
    try:
        result = subprocess.check_output(
            ["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT0"],
            text=True,
            stderr=subprocess.STDOUT
        )
        for line in result.splitlines():
            if "percentage:" in line.lower():
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    
    return "N/A"


def get_gpu() -> str:
    if os.name == "nt":
        try:
            result = subprocess.check_output("wmic path win32_videocontroller get name", shell=True, text=True, stderr=subprocess.STDOUT)
            for line in result.splitlines():
                line = line.strip()
                if line and line != "Name":
                    return line
        except Exception:
            pass
        return "Unknown"
    
    # Try Linux GPU detection
    try:
        result = subprocess.check_output("lspci | grep -i 'vga\\|3d\\|display'", shell=True, text=True, stderr=subprocess.STDOUT)
        lines = result.splitlines()
        if lines:
            # Extract GPU name from lspci output
            line = lines[0]
            if ": " in line:
                return line.split(": ", 1)[1].strip()
            return line.strip()
    except Exception:
        pass
    
    return "Unknown"


def get_packages() -> str:
    try:
        programs_dir = ROOT / "Programs"
        if programs_dir.exists():
            count = len([f for f in programs_dir.glob("*.py") if f.is_file()])
            return str(count)
    except Exception:
        pass
    return "0"


def get_disks() -> list[tuple[str, str, str]]:
    disks = []
    try:
        for index, usage in enumerate(shutil.disk_partitions(all=False)):
            try:
                disk_usage = shutil.disk_usage(usage.mountpoint)
                disks.append((f"Disk {index}", format_bytes(disk_usage.used), format_bytes(disk_usage.free)))
            except Exception:
                pass
    except Exception:
        return []
    if not disks:
        try:
            usage = shutil.disk_usage(ROOT)
            disks.append(("Disk 0", format_bytes(usage.used), format_bytes(usage.free)))
        except Exception:
            pass
    return disks


from core_settings import load_settings

user = os.environ.get("COREOS_USER", "root")
version = os.environ.get("COREOS_VERSION", "1.0")
build = os.environ.get("COREOS_BUILDNUM", "260704")
hostname = load_settings().get("hostname", "CoreOS")

print(f"{user}@{hostname}")
print("-" * 20)
art_lines = ASCII_ART

info_lines = [
    f"OS: CoreOS {version}",
    f"Build: {build}",
    f"CPU: {get_cpu_name()}",
]
ram_used, ram_total = get_memory()
info_lines.append(f"Memory: {ram_used}/{ram_total}")
info_lines.append(f"Packages: {get_packages()}")
info_lines.append(f"GPU: {get_gpu()}")
for disk_name, used, free in get_disks():
    info_lines.append(f"{disk_name}: used={used}, free={free}")
info_lines.append("Shell: CoreOS Shell")
info_lines.append(f"Python: {platform.python_version()}")
info_lines.append(f"Battery: {get_battery()}")

width = max(len(line) for line in art_lines)
for index, art_line in enumerate(art_lines):
    info_line = info_lines[index] if index < len(info_lines) else ""
    print(color(art_line.ljust(width)) + ("  " + color(info_line.split(":", 1)[0] + ":") + " " + info_line.split(":", 1)[1] if ":" in info_line else ""))

for extra in info_lines[len(art_lines):]:
    label = extra.split(":", 1)[0] + ":"
    value = extra.split(":", 1)[1] if ":" in extra else ""
    print(color(label) + " " + value)
