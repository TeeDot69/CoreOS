from __future__ import annotations
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import getpass
from pathlib import Path

OSNAME = "CoreOS"
VERSION = "1.0"
BUILDNUM = "2607.4"

ROOT_DIR = Path(__file__).resolve().parent
COREOS_DIR = ROOT_DIR
PROGRAMSDIR = COREOS_DIR / "Programs"
CMDSDIR = COREOS_DIR / "System" / "Commands"
CMDINTERPETER = COREOS_DIR / "Command.py"
USERDATA_DIR = COREOS_DIR / "System" / "userdata"
USERS_DIR = COREOS_DIR / "Users"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def format_bytes(value: int) -> str:
    for suffix in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or suffix == "TB":
            return f"{value:.1f} {suffix}"
        value /= 1024
    return f"{value:.1f} PB"


def get_memory_info() -> tuple[str, str]:
    try:
        if sys.platform == "win32":
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
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
            total = status.ullTotalPhys
            free = status.ullAvailPhys
            return format_bytes(total), format_bytes(free)
        else:
            if hasattr(os, "sysconf"):
                total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
                free = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_AVPHYS_PAGES")
                return format_bytes(total), format_bytes(free)
    except Exception:
        pass
    return "Unknown", "Unknown"


def get_storage_info() -> tuple[str, str]:
    try:
        usage = shutil.disk_usage(COREOS_DIR)
        return format_bytes(usage.total), format_bytes(usage.free)
    except Exception:
        return "Unknown", "Unknown"


def get_hardware_report() -> str:
    total_ram, free_ram = get_memory_info()
    total_storage, free_storage = get_storage_info()
    parts = [
        f"CPU: {os.cpu_count() or 1} cores",
        f"RAM: total={total_ram}, free={free_ram}",
        f"Storage: total={total_storage}, free={free_storage}",
        f"OS: {platform.platform()}",
        f"Python: {platform.python_version()}"
    ]
    return "\n".join(parts)


def ensure_directories() -> None:
    COREOS_DIR.mkdir(parents=True, exist_ok=True)
    PROGRAMSDIR.mkdir(parents=True, exist_ok=True)
    CMDSDIR.mkdir(parents=True, exist_ok=True)
    USERDATA_DIR.mkdir(parents=True, exist_ok=True)
    USERS_DIR.mkdir(parents=True, exist_ok=True)


def load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def boot_system() -> None:
    ensure_directories()
    clear_screen()
    print(f"Starting {OSNAME} {VERSION}")
    print("Verifying Hardware\n")
    print(get_hardware_report())
    print()


def main() -> None:
    boot_system()
    login_module = load_module_from_path("coreos_login", COREOS_DIR / "System" / "login.py")
    login_manager = login_module.LoginManager(USERDATA_DIR, USERS_DIR)
    user = login_manager.authenticate()
    clear_screen()
    print(f"{OSNAME} {VERSION} [Build {BUILDNUM}]")
    print("(C) 2019-2026 TDot Technologies Co.\n")

    command_module = load_module_from_path("coreos_command", CMDINTERPETER)
    while True:
        shell = command_module.CommandInterpreter(
            commands_dir=CMDSDIR,
            programs_dir=PROGRAMSDIR,
            coreos_root=COREOS_DIR,
            user=user,
            version=VERSION,
            buildnum=BUILDNUM,
            account_manager=login_manager,
        )
        try:
            shell.run()
            break
        except command_module.LogoutException:
            clear_screen()
            user = login_manager.authenticate()
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting CoreOS.")
        sys.exit(0)
