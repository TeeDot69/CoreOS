#!/usr/bin/env python3
"""Path helpers for CoreOS.

These keep commands from ever revealing the host operating system's absolute
path (e.g. E:\\Coding\\CoreOS\\...) and instead present paths relative to the
CoreOS install root, such as ``CoreOS\\Users\\test``.
"""
from __future__ import annotations

import os
from pathlib import Path


def coreos_root() -> Path:
    """Return the CoreOS install root (falling back to the command's dir)."""
    raw = os.getenv("COREOS_ROOT")
    if raw:
        try:
            return Path(raw).resolve()
        except Exception:
            pass
    return Path.cwd().resolve()


def display_path(path: Path, root: Path | None = None) -> str:
    """Return a display form of *path* that never shows anything above the
    CoreOS root.

    The result always starts with a ``/`` and uses forward slashes, so a
    Windows path like ``E:\\Coding\\CoreOS\\CoreOS\\Users\\test`` is shown as
    ``/CoreOS/Users/test``.

    Examples
    --------
    >>> display_path(Path("E:/Coding/CoreOS/CoreOS/Users/test"))
    '/CoreOS/Users/test'
    >>> display_path(Path("E:/Coding/CoreOS/CoreOS"))
    '/CoreOS'
    """
    try:
        p = Path(path).resolve()
    except Exception:
        p = Path(path)

    if root is None:
        root = coreos_root()
    else:
        try:
            root = Path(root).resolve()
        except Exception:
            root = coreos_root()

    root_name = root.name or str(root)
    try:
        rel = p.relative_to(root)
    except ValueError:
        rel = None

    if rel is not None and str(rel) != ".":
        return f"/{root_name}/{rel}".replace("\\", "/")
    if rel is not None:
        return f"/{root_name}"

    # Outside the CoreOS tree - only ever show the final component(s),
    # never the absolute host path.
    parts = p.parts
    return str(parts[-1]) if parts else str(p)