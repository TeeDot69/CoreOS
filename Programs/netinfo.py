from __future__ import annotations
import socket

PKGNAME = "CoreOS.NetInfo"
PKGVER = "1.0"


def main() -> None:
    try:
        print("CoreOS NetInfo")
        try:
            hostname = socket.gethostname()
            addr = socket.gethostbyname(hostname)
            print(f"Hostname: {hostname}")
            print(f"IP Address: {addr}")
        except Exception as exc:
            print(f"Network info error: {exc}")
    except KeyboardInterrupt:
        print("\nNetinfo interrupted.")


if __name__ == "__main__":
    main()
