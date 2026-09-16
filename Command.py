from __future__ import annotations
import getpass
import json
import os
import platform
import shlex
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Shared settings module (single source of truth) lives in System/Commands.
sys.path.insert(0, str(Path(__file__).resolve().parent / "System" / "Commands"))
from core_settings import load_settings  # noqa: E402

# Named colours usable for prompt_color.
COLOR_ANSI = {
    "green": "\033[38;2;0;170;0m",
    "blue": "\033[38;2;0;120;255m",
    "cyan": "\033[38;2;0;200;200m",
    "yellow": "\033[38;2;255;200;0m",
    "red": "\033[38;2;255;60;60m",
    "magenta": "\033[38;2;255;0;255m",
    "white": "\033[38;2;255;255;255m",
}
RESET = "\033[0m"

PYTHON_COMMANDS = {"python", "python3", "py", "python.exe", "python3.exe", "py.exe"}
PIP_COMMANDS = {"pip", "pip3", "python3.pip", "python3-pip", "pip.exe", "pip3.exe"}


class User:
    def __init__(self, username: str, home_dir: Path, permissions: str):
        self.username = username
        self.home_dir = home_dir
        self.permissions = permissions


class LogoutException(Exception):
    pass


class CoreOSCrashHandler:
    """Handles crashes and prevents CoreOS from exiting on errors"""
    
    def __init__(self, coreos_root: Path):
        self.coreos_root = coreos_root.resolve()
        self.crash_log_dir = self.coreos_root / "System" / "logs"
        self.crash_log_dir.mkdir(parents=True, exist_ok=True)
    
    def handle_crash(self, error: Exception, context: str = "") -> None:
        """Handle a crash by logging it and displaying a user-friendly message"""
        crash_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        crash_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Prepare crash information
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()

        # Respect the "enable_logging" setting (default on). If logging is
        # disabled, still show the friendly message but skip writing the file.
        try:
            logging_on = bool(load_settings(root=self.coreos_root).get("enable_logging", True))
        except Exception:
            logging_on = True

        log_file = None
        if logging_on:
            # Log to file
            log_file = self.crash_log_dir / f"crash_{crash_id}.log"
            try:
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(f"CoreOS Crash Report\n")
                    f.write(f"{'=' * 50}\n")
                    f.write(f"Time: {crash_time}\n")
                    f.write(f"Context: {context}\n")
                    f.write(f"Error Type: {error_type}\n")
                    f.write(f"Error Message: {error_message}\n")
                    f.write(f"\nStack Trace:\n")
                    f.write(f"{'-' * 50}\n")
                    f.write(stack_trace)
                    f.write(f"{'-' * 50}\n")
            except Exception:
                pass  # If logging fails, continue anyway
        
        # Display user-friendly error message
        print(f"\n{'!' * 60}")
        print(f"!  CoreOS Error Handler")
        print(f"{'!' * 60}")
        print(f"!  An error occurred: {error_type}")
        print(f"!  {error_message}")
        if context:
            print(f"!  Context: {context}")
        print(f"!")
        if log_file is not None:
            print(f"!  Crash log saved to: {log_file.name}")
        print(f"!  CoreOS will continue running.")
        print(f"{'!' * 60}\n")


class CommandInterpreter:
    def __init__(
        self,
        commands_dir: Path,
        programs_dir: Path,
        coreos_root: Path,
        user: User,
        version: str,
        buildnum: int,
        account_manager=None,
    ):
        self.commands_dir = commands_dir
        self.programs_dir = programs_dir
        self.coreos_root = coreos_root
        self.user = user
        self.version = version
        self.buildnum = buildnum
        self.account_manager = account_manager
        self.cwd = user.home_dir
        self.history: list[str] = []
        self.coreos_root = coreos_root.resolve()
        self.crash_handler = CoreOSCrashHandler(coreos_root)
        self.startup_run = False

    def run_startup_command(self) -> None:
        """Run the configured startup_command (once per shell session)."""
        if self.startup_run:
            return
        self.startup_run = True
        try:
            sc = load_settings(root=self.coreos_root, home=self.user.home_dir).get("startup_command", "")
            sc = str(sc).strip()
        except Exception:
            return
        if sc:
            self.history.append(sc)
            self.execute_command(sc)

    def get_full_prompt_dir(self) -> str:
        """Absolute-style CoreOS-relative path for the 'full' prompt style."""
        try:
            cwd_res = self.cwd.resolve()
            root_res = self.coreos_root.resolve()
            rel = cwd_res.relative_to(root_res)
            return f"/{root_res.name}/{rel}".replace("\\", "/")
        except Exception:
            try:
                return f"/{self.coreos_root.name}/{self.cwd.resolve().name}"
            except Exception:
                return self.get_prompt_dir()

    def run(self) -> None:
        self.run_startup_command()
        while True:
            try:
                settings = load_settings(root=self.coreos_root, home=self.user.home_dir)
                hostname = str(settings.get("hostname", "CoreOS"))
                style = str(settings.get("prompt_style", "default"))
                color = COLOR_ANSI.get(str(settings.get("prompt_color", "green")), COLOR_ANSI["green"])
                bell = bool(settings.get("bell_enabled", False))
                history_size = int(settings.get("history_size", 100))

                prompt_dir = self.get_prompt_dir()

                if style == "minimal":
                    prompt = f"{color}{prompt_dir}{RESET}$ "
                elif style == "full":
                    prompt = f"{color}{self.user.username}@{hostname}:{RESET} {self.get_full_prompt_dir()}{RESET}$ "
                else:  # default
                    prompt = f"{color}{self.user.username}@{hostname}:{RESET} {prompt_dir}{RESET}$ "

                try:
                    command = input(prompt).strip()
                except EOFError:
                    print()
                    break
                if not command:
                    continue
                self.history.append(command)
                if len(self.history) > max(history_size, 0):
                    self.history = self.history[-history_size:] if history_size > 0 else []
                result = self.execute_command(command)
                if result is False and bell:
                    print("\a", end="", flush=True)
            except SystemExit:
                raise
            except LogoutException:
                raise
            except Exception as e:
                self.crash_handler.handle_crash(e, context="Shell main loop")

    def get_prompt_dir(self) -> str:
        try:
            if self.cwd == self.user.home_dir:
                return "~"
            if self.cwd.is_relative_to(self.user.home_dir):
                rel = self.cwd.relative_to(self.user.home_dir)
                return f"~/{rel}" if str(rel) != "." else "~"
            if self.cwd == self.coreos_root:
                return "coreosroot"
            if self.cwd.is_relative_to(self.coreos_root):
                return str(self.cwd.relative_to(self.coreos_root))
        except Exception:
            pass
        return str(self.cwd)

    def execute_command(self, command_line: str) -> None:
        try:
            parts = shlex.split(command_line, posix=True)
            if not parts:
                return
            cmd = parts[0].lower()
            args = parts[1:]

            # Core shell commands
            if cmd == "exit":
                raise SystemExit
            if cmd == "logout":
                raise LogoutException
            if cmd == "su":
                self.switch_user(args)
                return
            if cmd == "cd":
                self.change_directory(args)
                return
            if cmd == "help":
                self.print_help()
                return
            if cmd == "sudo":
                self.run_sudo(args)
                return
            if cmd == "history":
                self.cmd_history()
                return

            if cmd in PYTHON_COMMANDS or cmd in PIP_COMMANDS:
                self.run_python_tool(cmd, args)
                return

            # User management
            if cmd == "adduser":
                self.add_user(args)
                return
            if cmd == "remuser":
                self.remove_user(args)
                return

            # Alias
            if cmd == "calc":
                cmd = "calculator"

            # Try program first, then command scripts
            if self.run_program(cmd, args):
                return
            if self.run_command_script(cmd, args):
                return

            print(f"Command not found: {cmd}")
            return False
        except SystemExit:
            raise
        except LogoutException:
            raise
        except Exception as e:
            self.crash_handler.handle_crash(e, context=f"Command: {command_line}")
            return False

    def print_help(self) -> None:
        help_text = {
            "cd": "cd [directory] - Change directory",
            "ls": "ls [directory] - List directory contents",
            "pwd": "Print working directory",
            "clear": "Clear screen (Windows: cls)",
            "cls": "Clear screen",
            "mk": "mk <filename> - Create empty file",
            "mkdir": "mkdir <directory> - Create directory",
            "rm": "rm <file> - Remove file",
            "rmdir": "rmdir <directory> - Remove empty directory",
            "cat": "cat <file> - Print file contents",
            "copy": "copy <source> <destination> - Copy file",
            "mv": "mv <source> <destination> - Move/rename file",
            "find": "find [directory] - Find files and directories",
            "grep": "grep <pattern> <file> - Search file for pattern",
            "head": "head <file> - Print first 10 lines",
            "tail": "tail <file> - Print last 10 lines",
            "sort": "sort <file> - Print sorted lines",
            "tree": "tree [directory] - Display directory tree",
            "wc": "wc <file> - Count lines in file",
            "date": "Print current date (ISO format)",
            "time": "Print current time",
            "echo": "echo <text> - Print text",
            "whoami": "Print current username",
            "uname": "Print system information",
            "env": "Print CoreOS environment variables",
            "wget": "wget <url> [dest] - Download file",
            "programs": "List all available programs",
            "sysfetch": "Display system information",
            "history": "Show command history",
            "sudo": "sudo <command> - Run with elevated privileges",
            "su": "su [username] - Switch user with password prompt",
            "logout": "Logout current user and return to login prompt",
            "adduser": "adduser <name> <password> [-su] - Create user",
            "remuser": "remuser <name> - Remove user",
            "help": "Show this help message",
            "exit": "Exit CoreOS",
            "python": "Run the system Python interpreter or a Python command",
            "python3": "Alias for the system Python interpreter",
            "pip": "Run pip for the system Python interpreter",
            "pip3": "Alias for pip",
        }
        print("\n=== COMMANDS ===")
        for cmd in sorted(help_text.keys()):
            print(f"{cmd:12} - {help_text[cmd]}")
        print("\n=== PROGRAMS ===")
        print("Run any .py file from Programs folder by name (without .py)")
        print("Examples: calculator, todo, edit, diskinfo, monitor, netinfo")
        print("Use 'programs' command to list all available programs")
        print("\n=== DOCUMENTATION ===")
        print("Read program usage guide: cat System/PROGRAMS.txt")
        print("Or use your editor: edit System/PROGRAMS.txt")

    def build_script_environment(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                "COREOS_USER": self.user.username,
                "COREOS_HOME": str(self.user.home_dir),
                "COREOS_ROOT": str(self.coreos_root),
                "COREOS_VERSION": self.version,
                "COREOS_BUILDNUM": str(self.buildnum),
                "PWD": str(self.cwd),
            }
        )
        return env

    def run_python_tool(self, command: str, args: list[str]) -> None:
        """Run the host Python interpreter or its matching pip module."""
        if command in PIP_COMMANDS:
            package_name = "Python3.Pip"
            executable = [sys.executable, "-m", "pip"]
        else:
            package_name = "Python3"
            executable = [sys.executable]

        try:
            result = subprocess.run(
                [*executable, *args],
                cwd=self.cwd,
                env=self.build_script_environment(),
            )
            if result.returncode != 0:
                print(
                    f"Package {package_name} "
                    f"(version {self.get_python_package_version(package_name)}) "
                    f"exited with code {result.returncode}"
                )
        except KeyboardInterrupt:
            print(f"\n{package_name} interrupted.")
        except Exception as e:
            self.crash_handler.handle_crash(e, context=f"Package: {package_name}")

    def get_python_package_version(self, package_name: str) -> str:
        """Return the version reported by the host Python runtime or pip."""
        if package_name == "Python3":
            return platform.python_version()
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                check=False,
                env=self.build_script_environment(),
            )
            fields = result.stdout.split()
            if len(fields) > 1 and fields[0].lower() == "pip":
                return fields[1]
        except Exception:
            pass
        return "unknown"

    def read_package_info(self, path: Path) -> tuple[str, str]:
        pkg_name = None
        pkg_ver = None
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    if "PKGNAME" in line and "=" in line:
                        pkg_name = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if "PKGVER" in line and "=" in line:
                        pkg_ver = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if pkg_name and pkg_ver:
                        break
        except Exception:
            pass
        return pkg_name or path.stem, pkg_ver or ""

    def run_sudo(self, args: list[str]) -> None:
        try:
            if not args:
                print("Usage: sudo <command>")
                return
            if self.user.permissions != "su" and self.user.username != "root":
                print("Permission denied")
                return
            self.execute_command(" ".join(args))
        except Exception as e:
            self.crash_handler.handle_crash(e, context="Sudo command")

    def cmd_history(self) -> None:
        for index, item in enumerate(self.history, 1):
            print(f"{index}  {item}")

    def add_user(self, args: list[str]) -> None:
        try:
            if self.user.permissions != "su" and self.user.username != "root":
                print("Permission denied")
                return
            if len(args) < 2:
                print("Usage: adduser <name> <password> [-su]")
                return
            username = args[0]
            password = args[1]
            permissions = "su" if len(args) > 2 and args[2] == "-su" else "user"
            if self.account_manager is None:
                print("Account manager unavailable")
                return
            if self.account_manager.create_account(username, password, permissions):
                print(f"User created: {username}")
            else:
                print("Failed to create user")
        except Exception as e:
            self.crash_handler.handle_crash(e, context="Add user")

    def remove_user(self, args: list[str]) -> None:
        try:
            if self.user.permissions != "su" and self.user.username != "root":
                print("Permission denied")
                return
            if len(args) < 1:
                print("Usage: remuser <name>")
                return
            username = args[0]
            password = getpass.getpass("Password: ")
            if self.account_manager is None:
                print("Account manager unavailable")
                return
            if self.account_manager.remove_account(username, password):
                print(f"User removed: {username}")
            else:
                print("Failed to remove user")
        except Exception as e:
            self.crash_handler.handle_crash(e, context="Remove user")

    def switch_user(self, args: list[str]) -> None:
        try:
            if self.account_manager is None:
                print("Account manager unavailable")
                return
            if len(args) >= 1:
                username = args[0]
            else:
                username = input("Switch user: ").strip()
            password = getpass.getpass("Password: ")
            new_user = self.account_manager.authenticate_user(username, password)
            if new_user is None:
                print("Authentication failed: invalid username or password")
                return
            self.user = new_user
            self.cwd = new_user.home_dir
            print(f"Switched to user: {new_user.username}")
        except Exception as e:
            self.crash_handler.handle_crash(e, context="User switch")

    def change_directory(self, args: list[str]) -> None:
        try:
            if len(args) == 0:
                target = self.user.home_dir
            else:
                target = Path(args[0])
                if not target.is_absolute():
                    target = self.cwd / target
            target = target.resolve()
            if self.is_within_coreos(target):
                if target.exists() and target.is_dir():
                    self.cwd = target
                else:
                    print(f"Directory not found: {args[0]}")
            else:
                print("Access denied: Outside CoreOS directory")
        except Exception as e:
            self.crash_handler.handle_crash(e, context="Change directory")

    def is_within_coreos(self, path: Path) -> bool:
        try:
            path = path.resolve()
            return self.coreos_root == path or self.coreos_root in path.parents
        except RuntimeError:
            return False

    def run_program(self, cmd: str, args: list[str]) -> bool:
        if self.is_python_program(cmd):
            return self.execute_python_program(cmd, args)
        return False

    def run_command_script(self, cmd: str, args: list[str]) -> bool:
        if cmd.startswith("./"):
            script_path = (self.cwd / cmd[2:]).resolve()
            if not self.is_within_coreos(script_path):
                print("Access denied: Outside CoreOS directory")
                return True
            if script_path.exists() and script_path.is_file():
                self.execute_script(script_path, args)
                return True
            return False

        candidate_names = [cmd, f"{cmd}.py", f"{cmd}.bat", f"{cmd}.sh", f"{cmd}.bash"]
        for name in candidate_names:
            script_path = (self.commands_dir / name).resolve()
            if script_path.exists() and script_path.is_file() and self.is_within_coreos(script_path):
                self.execute_script(script_path, args)
                return True
        return False

    def is_python_program(self, cmd: str) -> bool:
        candidate = self.programs_dir / f"{cmd}.py"
        if candidate.exists():
            return True
        local_candidate = self.cwd / f"{cmd}.py"
        if local_candidate.exists():
            return True
        return False

    def execute_python_program(self, cmd: str, args: list[str]) -> bool:
        candidate = self.programs_dir / f"{cmd}.py"
        if not candidate.exists():
            candidate = self.cwd / f"{cmd}.py"
        if not candidate.exists():
            return False
        if not self.is_within_coreos(candidate):
            print("Access denied: Outside CoreOS directory")
            return True
        
        try:
            # Stream output directly to the terminal (inherited stdio) so that
            # interactive programs (settings, calculator, todo, edit) display
            # their menus/prompts live instead of buffering all output until
            # the program exits.
            result = subprocess.run(
                [sys.executable, str(candidate), *args],
                cwd=self.cwd,
                env=self.build_script_environment(),
            )
            # Only print exit message if program exited with error
            if result.returncode != 0:
                pkg_name, pkg_ver = self.read_package_info(candidate)
                if pkg_name:
                    print(f"Program {pkg_name} exited with code {result.returncode}")
        except KeyboardInterrupt:
            print("\nProgram interrupted.")
        except Exception as e:
            self.crash_handler.handle_crash(e, context=f"Program: {cmd}")
        
        return True

    def execute_script(self, path: Path, args: list[str]) -> None:
        ext = path.suffix.lower()
        env = self.build_script_environment()
        try:
            # Inherit stdio so scripts stream output live and interactive
            # prompts (e.g. rm/rmdir confirmation) actually display.
            if ext == ".py":
                subprocess.run([sys.executable, str(path), *args], cwd=self.cwd, env=env)
            elif ext == ".bat" and os.name == "nt":
                subprocess.run([str(path), *args], cwd=self.cwd, env=env, shell=True)
            elif ext in {".sh", ".bash"}:
                subprocess.run(["bash", str(path), *args], cwd=self.cwd, env=env)
            else:
                subprocess.run([str(path), *args], cwd=self.cwd, env=env, shell=True)
        except KeyboardInterrupt:
            print("\nScript interrupted.")
        except Exception as e:
            self.crash_handler.handle_crash(e, context=f"Script: {path.name}")
