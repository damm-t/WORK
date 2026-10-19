"""
Atomic JSON State File Persistence with POSIX File Locking
===========================================================
Provides crash-safe and concurrency-safe read/write operations for
multi-process state files (e.g. crypto, futures, forex, autopilot).
Uses fcntl.flock on macOS / Linux and atomic file replacement.
"""

from __future__ import annotations

try:
    import fcntl
except ImportError:
    fcntl = None

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def atomic_json_read(path: Path | str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Reads JSON from path using a shared lock (LOCK_SH) on POSIX.
    Returns default or empty dict if file does not exist or is invalid.
    """
    p = Path(path)
    if not p.exists():
        return default if default is not None else {}

    try:
        with open(p, "r", encoding="utf-8") as f:
            if fcntl:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    return json.load(f)
                finally:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass
            else:
                return json.load(f)
    except Exception as e:
        logger.warning(f"[json_state] Failed to read {p}: {e}")
        return default if default is not None else {}


def atomic_json_write(path: Path | str, data: Any, indent: int = 2) -> None:
    """
    Writes data to a temporary file with an exclusive lock (LOCK_EX) on POSIX,
    flushes and fsyncs, then atomically renames to the destination path.
    Prevents torn reads and multi-process corruption.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = p.with_suffix(f".tmp.{os.getpid()}")

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            if fcntl:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    json.dump(data, f, indent=indent, default=str)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass
            else:
                json.dump(data, f, indent=indent, default=str)
                f.flush()
                os.fsync(f.fileno())
        os.replace(tmp_path, p)
    except Exception as e:
        logger.error(f"[json_state] Failed to atomically write {p}: {e}")
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        raise
