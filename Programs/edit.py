from __future__ import annotations
import os
import sys
from pathlib import Path

PKGNAME = "CoreOS.Edit"
PKGVER = "1.0"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def read_file(path: Path) -> list[str]:
    if path.exists():
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text.rstrip('\n').split('\n') if text.strip() else [""]
    return [""]


def display_file(path: Path, lines: list[str], original_lines: list[str]) -> None:
    clear_screen()
    # Show relative path from COREOS_ROOT if possible
    coreos_root = Path(os.getenv("COREOS_ROOT", "."))
    try:
        display_path = path.relative_to(coreos_root)
    except ValueError:
        display_path = path
    print(f"CoreOS Edit - {display_path}")
    changed = lines != original_lines
    print(f"Lines: {len(lines)} {'[MODIFIED]' if changed else ''}")
    print("-" * 60)
    
    if lines:
        for i, line in enumerate(lines, 1):
            print(f"{i:3} | {line}")
    else:
        print("(empty file)")
    
    print("-" * 60)
    print("Commands: add <num> <text>  del <num>  edit <num> <text>  view  save  exit")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Usage: edit <filename>")
        sys.exit(1)
    
    path = Path(args[0])
    if not path.is_absolute():
        path = Path(os.getenv("PWD", ".")) / path
    
    lines = read_file(path)
    original_lines = lines.copy()
    
    while True:
        display_file(path, lines, original_lines)
        
        try:
            cmd = input("\n> ").strip()
        except EOFError:
            break
        
        if not cmd:
            continue
        
        parts = cmd.split(maxsplit=2)
        action = parts[0].lower()
        
        if action in {"exit", "quit"}:
            if lines != original_lines:
                print("\nFile has unsaved changes!")
                print("Save? (y/n): ", end="")
                if input().strip().lower() == "y":
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("\n".join(lines) + "\n" if lines else "", encoding="utf-8")
                    # Show relative path from COREOS_ROOT if possible
                    coreos_root = Path(os.getenv("COREOS_ROOT", "."))
                    try:
                        display_path = path.relative_to(coreos_root)
                    except ValueError:
                        display_path = path
                    print(f"Saved to {display_path}")
                else:
                    print("Discarded changes")
            break
        
        elif action == "view":
            continue
        
        elif action == "save":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(lines) + "\n" if lines else "", encoding="utf-8")
            original_lines = lines.copy()
            # Show relative path from COREOS_ROOT if possible
            coreos_root = Path(os.getenv("COREOS_ROOT", "."))
            try:
                display_path = path.relative_to(coreos_root)
            except ValueError:
                display_path = path
            print(f"Saved to {display_path}")
            input("Press Enter...")
        
        elif action == "add":
            if len(parts) < 3:
                print("Usage: add <line_num> <text>")
                input("Press Enter...")
                continue
            
            try:
                line_num = int(parts[1])
                text = parts[2]
                
                if line_num < 1 or line_num > len(lines) + 1:
                    print(f"Invalid line number (1-{len(lines) + 1})")
                    input("Press Enter...")
                    continue
                
                lines.insert(line_num - 1, text)
                print(f"Added at line {line_num}")
                input("Press Enter...")
            except ValueError:
                print("Line number must be a valid integer")
                input("Press Enter...")
        
        elif action == "del":
            if len(parts) < 2:
                print("Usage: del <line_num>")
                input("Press Enter...")
                continue
            
            try:
                line_num = int(parts[1])
                if 1 <= line_num <= len(lines):
                    deleted = lines.pop(line_num - 1)
                    print(f"Deleted line {line_num}: {deleted}")
                    input("Press Enter...")
                else:
                    print(f"Invalid line number (1-{len(lines)})")
                    input("Press Enter...")
            except ValueError:
                print("Line number must be a valid integer")
                input("Press Enter...")
        
        elif action == "edit":
            if len(parts) < 3:
                print("Usage: edit <line_num> <new_text>")
                input("Press Enter...")
                continue
            
            try:
                line_num = int(parts[1])
                new_text = parts[2]
                
                if 1 <= line_num <= len(lines):
                    old_text = lines[line_num - 1]
                    lines[line_num - 1] = new_text
                    print(f"Changed line {line_num}")
                    print(f"  Was: {old_text}")
                    print(f"  Now: {new_text}")
                    input("Press Enter...")
                else:
                    print(f"Invalid line number (1-{len(lines)})")
                    input("Press Enter...")
            except ValueError:
                print("Line number must be a valid integer")
                input("Press Enter...")
        
        else:
            print(f"Unknown command: {action}")
            input("Press Enter...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nEdit cancelled.")
