from __future__ import annotations
import os
import platform
import shutil
import time

PKGNAME = "CoreOS.Monitor"
PKGVER = "1.0"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def format_bytes(value: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} PB"


def main() -> None:
    clear_screen()
    print("CoreOS Monitor")
    print("Press Ctrl+C to exit")
    try:
        while True:
            mem = shutil.disk_usage('.')
            print(f"OS: {platform.platform()}")
            print(f"CPU cores: {os.cpu_count()}")
            print(f"Storage total: {format_bytes(mem.total)}, free: {format_bytes(mem.free)}")
            time.sleep(2)
            clear_screen()
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
