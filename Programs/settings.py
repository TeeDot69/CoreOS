from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Make the shared settings schema importable (it lives in System/Commands).
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "System" / "Commands"))

from core_settings import CATEGORIES, CHOICES, DEFAULT_SETTINGS, ORDER, TYPES  # noqa: E402
from core_settings import display_value, load_settings, user_settings_file  # noqa: E402

PKGNAME = "CoreOS.Settings"
PKGVER = "1.1"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def save_settings(settings: dict) -> bool:
    try:
        path = user_settings_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(settings, indent=4, sort_keys=True), encoding="utf-8"
        )
        return True
    except Exception:
        return False


def pause() -> None:
    input("\nPress Enter to return to the menu...")


def render_indexed_choices(settings: dict, key: str) -> None:
    print(f"  Current : {display_value(settings[key])}")
    print(f"  Choices :")
    for i, opt in enumerate(CHOICES[key], 1):
        marker = " *" if opt == settings[key] else ""
        print(f"    [{i}] {opt}{marker}")


def choose_bool(settings: dict, key: str) -> bool:
    print(f"  Current : {'on' if settings[key] else 'off'}")
    print("  [1] On")
    print("  [2] Off")
    opt = input("\n  Choice (1/2): ").strip().lower()
    if opt == "1" or opt in ("on", "yes", "y"):
        settings[key] = True
    elif opt == "2" or opt in ("off", "no", "n"):
        settings[key] = False
    else:
        print("  No change.")
        return False
    return True


def choose_choice(settings: dict, key: str) -> bool:
    render_indexed_choices(settings, key)
    opt = input("\n  Choice (number): ").strip()
    if opt.isdigit():
        idx = int(opt) - 1
        opts = CHOICES[key]
        if 0 <= idx < len(opts):
            settings[key] = opts[idx]
            return True
    print("  No change.")
    return False


def choose_scalar(settings: dict, key: str) -> bool:
    kind = TYPES[key]
    print(f"  Current : {display_value(settings[key])}   (type: {kind})")
    raw = input("\n  New value (leave empty to cancel): ").strip()
    if raw == "":
        return False
    try:
        if kind == "int":
            settings[key] = int(raw)
        else:  # str
            if raw == "":
                raise ValueError
            settings[key] = raw
        return True
    except ValueError:
        print("  Invalid value — no change made.")
        return False


def edit_setting(settings: dict, key: str) -> None:
    clear_screen()
    print("=" * 52)
    print(f"  Edit: {key}")
    print("=" * 52)
    kind = TYPES[key]

    if kind == "bool":
        changed = choose_bool(settings, key)
    elif kind == "choice":
        changed = choose_choice(settings, key)
    else:
        changed = choose_scalar(settings, key)

    if changed and save_settings(settings):
        print(f"\n  Saved: {key} = {display_value(settings[key])}")
    else:
        print(f"\n  {key} unchanged.")
    pause()


def render_menu(settings: dict) -> None:
    clear_screen()
    print("=" * 52)
    print(f"          CoreOS Settings  v{PKGVER}")
    print("=" * 52)

    n = 1
    labels = {}
    for cat_name, keys in CATEGORIES:
        print(f"\n  -- {cat_name} --")
        for key in keys:
            labels[n] = key
            val = display_value(settings[key])
            suffix = ""
            if TYPES[key] == "choice":
                suffix = f"   [{', '.join(CHOICES[key])}]"
            print(f"    [{n:>2}] {key:<22} : {val}{suffix}")
            n += 1

    print("\n" + "-" * 52)
    print("  Enter a number to change that setting.")
    print("  [A] Reset ALL to defaults      [X] Exit")
    print("-" * 52)
    return labels


def run() -> None:
    while True:
        settings = load_settings()
        labels = render_menu(settings)
        choice = input("\n  Select> ").strip().lower()

        if choice in {"x", "exit", "q", "quit"}:
            break
        if choice in {"a", "reset"}:
            settings = dict(DEFAULT_SETTINGS)
            if save_settings(settings):
                print("\n  All settings reset to defaults.")
            else:
                print("\n  Could not write settings file.")
            pause()
            continue
        if choice.isdigit():
            key = labels.get(int(choice))
            if key is not None:
                edit_setting(settings, key)
                continue
        print("\n  Unknown selection.")
        pause()


def main() -> None:
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n  Settings closed. Changes are saved as you make them.")


if __name__ == "__main__":
    main()