#!/usr/bin/env python3
"""Single source of truth for CoreOS settings.

Only *functional* settings are included here — every setting listed actually
changes CoreOS behaviour somewhere (shell prompt, ls, rm, date/time, history,
logging, watermark, hostname). Settings that cannot affect behaviour
(e.g. telemetry, font size, update channels) have been removed.

The user's live settings live at ``$COREOS_HOME/settings.json``. This module is
the authority for defaults, types, choices and ordering. Components read
settings through :func:`load_settings` / :func:`get`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_SETTINGS = {
    # ---- System ----
    "hostname": "CoreOS",
    "date_format": "ISO",
    "time_format": "24h",
    "enable_logging": True,
    # ---- Appearance ----
    "prompt_color": "green",
    "prompt_style": "default",
    "show_watermark": True,
    "bell_enabled": False,
    # ---- Files & Editor ----
    "show_hidden_files": False,
    "list_directories_first": True,
    "confirm_delete": True,
    # ---- Shell ----
    "history_size": 100,
    "startup_command": "",
}

TYPES = {
    "hostname": "str",
    "date_format": "choice",
    "time_format": "choice",
    "enable_logging": "bool",
    "prompt_color": "choice",
    "prompt_style": "choice",
    "show_watermark": "bool",
    "bell_enabled": "bool",
    "show_hidden_files": "bool",
    "list_directories_first": "bool",
    "confirm_delete": "bool",
    "history_size": "int",
    "startup_command": "str",
}

CHOICES = {
    "date_format": ["ISO", "US", "EU"],
    "time_format": ["24h", "12h"],
    "prompt_color": ["green", "blue", "cyan", "yellow", "red", "magenta", "white"],
    "prompt_style": ["default", "minimal", "full"],
}

# Grouped so menus can present related settings together.
CATEGORIES = [
    ("System", ["hostname", "date_format", "time_format", "enable_logging"]),
    ("Appearance", ["prompt_color", "prompt_style", "show_watermark", "bell_enabled"]),
    ("Files & Editor", ["show_hidden_files", "list_directories_first", "confirm_delete"]),
    ("Shell", ["history_size", "startup_command"]),
]

ORDER = [key for _cat, keys in CATEGORIES for key in keys]


def coreos_root() -> Path:
    raw = os.getenv("COREOS_ROOT")
    if raw:
        try:
            return Path(raw).resolve()
        except Exception:
            pass
    return Path.cwd().resolve()


def user_home() -> Path:
    raw = os.getenv("COREOS_HOME")
    if raw:
        return Path(raw)
    user = os.getenv("COREOS_USER", "root")
    return coreos_root() / "Users" / user


def system_defaults_file(root: Path | None = None) -> Path:
    return (root or coreos_root()) / "System" / "settings" / "default_settings.json"


def user_settings_file(home: Path | None = None) -> Path:
    return (home or user_home()) / "settings.json"


def _coerce(key: str, value) -> object:
    """Return *value* only if it is valid for *key*, else the default."""
    kind = TYPES.get(key, "str")
    default = DEFAULT_SETTINGS[key]
    if kind == "bool":
        return value if isinstance(value, bool) else default
    if kind == "int":
        return value if isinstance(value, int) and not isinstance(value, bool) else default
    if kind == "choice":
        if isinstance(value, str) and value in CHOICES.get(key, [value]):
            return value
        return default
    return value if isinstance(value, str) else default


def load_settings(root: Path | None = None, home: Path | None = None) -> dict:
    """Return the effective settings dict (only recognised keys)."""
    settings = dict(DEFAULT_SETTINGS)

    # Optional shipped defaults file (System/settings/default_settings.json).
    df = system_defaults_file(root)
    if df.exists():
        try:
            data = json.loads(df.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for key in ORDER:
                    if key in data:
                        settings[key] = _coerce(key, data[key])
        except Exception:
            pass

    # Per-user live overrides.
    uf = user_settings_file(home)
    if uf.exists():
        try:
            data = json.loads(uf.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for key in ORDER:
                    if key in data:
                        settings[key] = _coerce(key, data[key])
        except Exception:
            pass

    return settings


def get(key: str, root: Path | None = None, home: Path | None = None):
    """Typed value for one setting, with a safe default fallback."""
    return load_settings(root, home).get(key, DEFAULT_SETTINGS[key])


def display_value(value) -> str:
    """Human-friendly value for menus / listings."""
    if isinstance(value, bool):
        return "on" if value else "off"
    if isinstance(value, str) and value == "":
        return "(empty)"
    return str(value)