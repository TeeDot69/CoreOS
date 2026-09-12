from __future__ import annotations
import os
import sys
from pathlib import Path

PKGNAME = "CoreOS.Todo"
PKGVER = "1.0"

HOME = Path(os.getenv("COREOS_HOME", "."))
DOCS_DIR = HOME / "Documents"
DOCS_DIR.mkdir(exist_ok=True)
FILE = DOCS_DIR / "todo.txt"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def main() -> None:
    clear_screen()
    tasks = []
    if FILE.exists():
        tasks = FILE.read_text(encoding="utf-8").splitlines()
    
    changed = False
    
    try:
        while True:
            clear_screen()
            print(f"CoreOS Todo - {FILE}")
            print("=" * 40)
            if tasks:
                for index, task in enumerate(tasks, 1):
                    print(f"[{index}] {task}")
            else:
                print("(empty)")
            
            print("\n" + "=" * 40)
            print("Commands: add <task>, del <num>, save, exit (or Ctrl+C)")
            if changed:
                print("* unsaved changes")
            
            command = input("todo> ").strip()
            
            if command in {"exit", "quit"}:
                if changed:
                    print("\nUnsaved changes. Save before exit? (y/n)")
                    if input().strip().lower() == "y":
                        FILE.write_text("\n".join(tasks) + ("\n" if tasks else ""), encoding="utf-8")
                        print("Saved!")
                break
            
            if command.startswith("add "):
                task = command[4:].strip()
                if task:
                    tasks.append(task)
                    changed = True
                    print(f"Added: {task}")
                    input("Press Enter...")
            
            elif command.startswith("del "):
                try:
                    index = int(command[4:]) - 1
                    if 0 <= index < len(tasks):
                        deleted = tasks.pop(index)
                        changed = True
                        print(f"Deleted: {deleted}")
                        input("Press Enter...")
                    else:
                        print(f"Invalid task number")
                        input("Press Enter...")
                except ValueError:
                    print("Usage: del <number>")
                    input("Press Enter...")
            
            elif command == "save":
                FILE.write_text("\n".join(tasks) + ("\n" if tasks else ""), encoding="utf-8")
                changed = False
                print(f"Saved to {FILE}")
                input("Press Enter...")
    except KeyboardInterrupt:
        print("\n\nTodo interrupted.")
        if changed:
            print("Changes were not saved.")


if __name__ == "__main__":
    main()
