from __future__ import annotations
import os
import platform
import shutil

PKGNAME = "CoreOS.DiskInfo"
PKGVER = "1.0"


def format_bytes(value: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} PB"


def main() -> None:
    try:
        print("CoreOS DiskInfo")
        try:
            partitions = shutil.disk_partitions(all=False)
        except Exception:
            partitions = []
        if not partitions:
            usage = shutil.disk_usage(".")
            print(f"Disk: total={format_bytes(usage.total)}, used={format_bytes(usage.used)}, free={format_bytes(usage.free)}")
            return
        for part in partitions:
            try:
                usage = shutil.disk_usage(part.mountpoint)
                print(f"{part.device} ({part.mountpoint})")
                print(f"  total={format_bytes(usage.total)}, used={format_bytes(usage.used)}, free={format_bytes(usage.free)}")
            except Exception:
                pass
    except KeyboardInterrupt:
        print("\nDiskinfo interrupted.")


if __name__ == "__main__":
    main()
