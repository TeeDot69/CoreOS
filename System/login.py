from __future__ import annotations
import json
import os
import shutil
import getpass
from pathlib import Path


class User:
    def __init__(self, username: str, home_dir: Path, permissions: str):
        self.username = username
        self.home_dir = home_dir
        self.permissions = permissions


class LoginManager:
    def __init__(self, userdata_dir: Path, users_dir: Path):
        self.userdata_dir = userdata_dir
        self.users_dir = users_dir
        self.root_account = self.userdata_dir / "root.json"
        self.userdata_dir.mkdir(parents=True, exist_ok=True)
        self.users_dir.mkdir(parents=True, exist_ok=True)

    def authenticate(self) -> User:
        self._ensure_first_boot_setup()
        while True:
            username = input("Login: ").strip()
            password = getpass.getpass("Password: ")
            user_file = self.userdata_dir / f"{username}.json"
            if not user_file.exists():
                print("Login failed: invalid username or password")
                continue
            try:
                with user_file.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
            except Exception:
                print("Login failed: account data corrupted")
                continue

            if data.get("password") != password:
                print("Login failed: invalid username or password")
                continue

            home_dir = self.users_dir / username
            return User(username=username, home_dir=home_dir, permissions=data.get("permissions", "user"))

    def authenticate_user(self, username: str, password: str) -> User | None:
        user_file = self.userdata_dir / f"{username}.json"
        if not user_file.exists():
            return None
        try:
            with user_file.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            return None
        if data.get("password") != password:
            return None
        home_dir = self.users_dir / username
        return User(username=username, home_dir=home_dir, permissions=data.get("permissions", "user"))

    def _ensure_first_boot_setup(self) -> None:
        if not self.root_account.exists():
            print("First time boot detected.")
            self._create_root_account()
            self._create_initial_user_account()
        elif not self._has_user_accounts():
            self._create_initial_user_account()

    def _create_root_account(self) -> None:
        while True:
            password = getpass.getpass("Root password: ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("Passwords do not match. Try again.")
                continue
            if not password:
                print("Password cannot be empty.")
                continue
            root_data = {
                "username": "root",
                "directory": str(self.users_dir / "root"),
                "permissions": "su",
                "password": password,
            }
            self._save_user_data(root_data)
            self._ensure_user_dir("root")
            break

    def _create_initial_user_account(self) -> None:
        print("Create a normal user account.")
        while True:
            username = input("Username: ").strip()
            if not username:
                print("Username cannot be empty.")
                continue
            if username.lower() == "root":
                print("Username 'root' is reserved.")
                continue
            break
        while True:
            password = getpass.getpass("Password: ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("Passwords do not match. Try again.")
                continue
            if not password:
                print("Password cannot be empty.")
                continue
            break
        make_su = input("Make this user a super user? (y/N): ").strip().lower() in {"y", "yes"}
        self.create_account(username, password, "su" if make_su else "user")

    def _has_user_accounts(self) -> bool:
        return any(path.name != "root.json" for path in self.userdata_dir.glob("*.json"))

    def _ensure_user_dir(self, username: str) -> None:
        user_dir = self.users_dir / username
        user_dir.mkdir(parents=True, exist_ok=True)
        for sub in ["documents", "downloads", "pictures", "videos", "music"]:
            (user_dir / sub).mkdir(exist_ok=True)

    def create_account(self, username: str, password: str, permissions: str = "user") -> bool:
        if not username or username.lower() == "root":
            return False
        account_path = self.userdata_dir / f"{username}.json"
        if account_path.exists():
            return False
        self._save_user_data(
            {
                "username": username,
                "directory": str(self.users_dir / username),
                "permissions": permissions,
                "password": password,
            }
        )
        self._ensure_user_dir(username)
        return True

    def remove_account(self, username: str, password: str) -> bool:
        account_path = self.userdata_dir / f"{username}.json"
        if not account_path.exists():
            return False
        try:
            with account_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            return False
        if data.get("password") != password:
            return False
        account_path.unlink(missing_ok=True)
        user_dir = self.users_dir / username
        if user_dir.exists():
            shutil.rmtree(user_dir)
        return True

    def _save_user_data(self, data: dict) -> None:
        self.userdata_dir.mkdir(parents=True, exist_ok=True)
        path = self.userdata_dir / f"{data['username']}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
