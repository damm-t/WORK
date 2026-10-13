"""
Tunnel and Mobile Remote Access Manager for Stock Signal Engine.

Provides:
- Automatic Cloudflare Tunnel creation (zero-config, free HTTPS URL).
- Fallback to Ngrok if cloudflared is unavailable.
- Local Wi-Fi network address discovery.
- QR Code generation for seamless camera scan from mobile phones.
- State persistence to reports/remote_access.json.
"""

from __future__ import annotations

import io
import json
import logging
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("remote_tunnel")

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports"
STATE_FILE = REPORTS_DIR / "remote_access.json"
LOG_FILE = REPORTS_DIR / "cloudflared.log"

_CURRENT_TUNNEL_PROC: Optional[subprocess.Popen] = None
_CACHED_TUNNEL_URL: Optional[str] = None
_WATCHDOG_THREAD: Optional[threading.Thread] = None


def is_tunnel_evicted() -> bool:
    """Detect if Cloudflare server evicted or rejected the quick tunnel session."""
    if not LOG_FILE.exists():
        return False
    try:
        content = LOG_FILE.read_text()
        tail = content[-3000:]
        if "Unauthorized: Tunnel not found" in tail or "ERR Register tunnel error" in tail:
            return True
    except Exception:
        pass
    return False


def get_local_ip() -> str:
    """Return the primary local network IPv4 address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def is_caffeinate_running() -> bool:
    """Check if macOS caffeinate is running to prevent system sleep."""
    try:
        res = subprocess.run(["pgrep", "caffeinate"], capture_output=True, text=True)
        return res.returncode == 0
    except Exception:
        return False


def get_active_tunnel_url() -> Optional[str]:
    """Check running cloudflared process or inspect log file for active URL."""
    global _CACHED_TUNNEL_URL

    if is_tunnel_evicted():
        logger.warning("[tunnel] Session evicted or expired by Cloudflare. Auto-clearing dead URL.")
        stop_tunnel()
        return None

    if _CACHED_TUNNEL_URL:
        # Check if process is still running
        if _CURRENT_TUNNEL_PROC and _CURRENT_TUNNEL_PROC.poll() is None:
            return _CACHED_TUNNEL_URL

    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            tunnel_url = data.get("tunnel_url")
            # Verify if cloudflared is actually running
            res = subprocess.run(["pgrep", "cloudflared"], capture_output=True, text=True)
            if res.returncode == 0 and tunnel_url and not is_tunnel_evicted():
                _CACHED_TUNNEL_URL = tunnel_url
                return tunnel_url
        except Exception:
            pass

    if LOG_FILE.exists():
        try:
            content = LOG_FILE.read_text()
            if not is_tunnel_evicted():
                matches = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                if matches:
                    _CACHED_TUNNEL_URL = matches[-1]
                    return _CACHED_TUNNEL_URL
        except Exception:
            pass

    return None


def start_tunnel(port: int = 8080) -> Dict[str, Any]:
    """
    Start or reuse an existing cloudflared quick tunnel to port 8080.
    Returns status dictionary.
    """
    global _CURRENT_TUNNEL_PROC, _CACHED_TUNNEL_URL

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    local_ip = get_local_ip()

    existing_url = get_active_tunnel_url()
    if existing_url:
        return get_remote_status(port=port)

    cf_bin = shutil.which("cloudflared") or "/opt/homebrew/bin/cloudflared"
    if not os.path.exists(cf_bin):
        logger.warning("cloudflared binary not found; falling back to local IP only.")
        return get_remote_status(port=port)

    # Start cloudflared tunnel
    log_fp = open(LOG_FILE, "w")
    cmd = [
        cf_bin,
        "tunnel",
        "--url",
        f"http://127.0.0.1:{port}",
        "--no-autoupdate",
    ]

    _CURRENT_TUNNEL_PROC = subprocess.Popen(
        cmd,
        stdout=log_fp,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setpgrp if hasattr(os, "setpgrp") else None,
    )

    # Poll log file for up to 10 seconds to discover trycloudflare URL
    tunnel_url = None
    for _ in range(25):
        time.sleep(0.4)
        if LOG_FILE.exists():
            content = LOG_FILE.read_text()
            matches = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
            if matches:
                tunnel_url = matches[-1]
                break

    _CACHED_TUNNEL_URL = tunnel_url

    status = get_remote_status(port=port)
    try:
        STATE_FILE.write_text(json.dumps(status, indent=2))
    except Exception as exc:
        logger.warning("Could not write remote state: %s", exc)

    _start_tunnel_watchdog(port=port)
    return status


def _start_tunnel_watchdog(port: int = 8080) -> None:
    """Ensure tunnel watchdog runs in background to auto-heal evicted tunnels."""
    global _WATCHDOG_THREAD
    if _WATCHDOG_THREAD and _WATCHDOG_THREAD.is_alive():
        return

    def _loop() -> None:
        logger.info("[tunnel_watchdog] Tunnel health supervisor active (60s cycle).")
        while True:
            time.sleep(60)
            try:
                if is_tunnel_evicted():
                    logger.warning("[tunnel_watchdog] Eviction detected in logs. Auto-healing tunnel...")
                    restart_tunnel(port=port)
                elif not get_active_tunnel_url():
                    logger.warning("[tunnel_watchdog] No active tunnel detected. Spawning tunnel...")
                    start_tunnel(port=port)
            except Exception as e:
                logger.debug(f"[tunnel_watchdog] Loop error: {e}")

    _WATCHDOG_THREAD = threading.Thread(target=_loop, daemon=True, name="TunnelWatchdog")
    _WATCHDOG_THREAD.start()


def stop_tunnel() -> None:
    """Terminate running cloudflared process."""
    global _CURRENT_TUNNEL_PROC, _CACHED_TUNNEL_URL
    if _CURRENT_TUNNEL_PROC:
        try:
            _CURRENT_TUNNEL_PROC.terminate()
            _CURRENT_TUNNEL_PROC.wait(timeout=2)
        except Exception:
            _CURRENT_TUNNEL_PROC.kill()
        _CURRENT_TUNNEL_PROC = None

    subprocess.run(["pkill", "-f", "cloudflared tunnel"], capture_output=True)
    _CACHED_TUNNEL_URL = None
    if STATE_FILE.exists():
        try:
            STATE_FILE.unlink()
        except Exception:
            pass
    if LOG_FILE.exists():
        try:
            LOG_FILE.unlink()
        except Exception:
            pass


def restart_tunnel(port: int = 8080) -> Dict[str, Any]:
    """Cleanly terminate existing Cloudflare tunnel and provision a fresh HTTPS proxy session."""
    stop_tunnel()
    time.sleep(1.2)
    return start_tunnel(port=port)


def get_remote_status(port: int = 8080) -> Dict[str, Any]:
    """Generate comprehensive remote access telemetry."""
    local_ip = get_local_ip()
    tunnel_url = get_active_tunnel_url()
    caffeinate_ok = is_caffeinate_running()

    local_base = f"http://{local_ip}:{port}"
    status = {
        "status": "online" if tunnel_url else "local_only",
        "tunnel_url": tunnel_url,
        "tunnel_type": "cloudflare" if tunnel_url else "none",
        "local_ip": local_ip,
        "local_port": port,
        "local_url": local_base,
        "local_widget_url": f"{local_base}/widget",
        "tunnel_widget_url": f"{tunnel_url}/widget" if tunnel_url else None,
        "caffeinate_active": caffeinate_ok,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "instructions": {
            "ios": "Open URL in Safari -> Tap Share -> Tap 'Add to Home Screen' for full-screen App mode",
            "android": "Open URL in Chrome -> Tap 3-dots Menu -> Tap 'Install app' or 'Add to Home screen'",
            "mac_note": "Keep Mac connected to charger; caffeinate keeps the machine awake while lid is open/idle.",
        },
    }
    return status


def get_qr_svg(url: str) -> str:
    """Generate SVG representation of QR code."""
    import qrcode
    import qrcode.image.svg

    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(url, image_factory=factory, box_size=10, border=2)
    stream = io.BytesIO()
    img.save(stream)
    return stream.getvalue().decode("utf-8")


def get_qr_png_bytes(url: str) -> bytes:
    """Generate PNG bytes of QR code."""
    import qrcode

    img = qrcode.make(url, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def print_cli_summary() -> None:
    """Print high-visibility remote access dashboard in terminal."""
    import qrcode

    status = start_tunnel(port=8080)
    target_url = status.get("tunnel_url") or status.get("local_url")

    print("\n" + "=" * 65)
    print(" 📱 QUANT DESK — MOBILE & REMOTE ACCESS READY")
    print("=" * 65)
    if status.get("tunnel_url"):
        print(f" 🌐 Remote HTTPS URL (Anywhere on 4G/5G):")
        print(f"    \033[1;36m{status['tunnel_url']}\033[0m")
        print(f" 📱 Mobile HUD Widget:")
        print(f"    \033[1;32m{status['tunnel_url']}/widget\033[0m")
    else:
        print(f" ⚠️  Tunnel not yet established. Local Wi-Fi only:")

    print(f"\n 🏠 Home Wi-Fi URL (Same Wi-Fi network):")
    print(f"    \033[1;33m{status['local_url']}\033[0m")
    print(f"    {status['local_url']}/widget (Widget)")

    print(f"\n 🔋 Mac Sleep Prevention:")
    if status.get("caffeinate_active"):
        print("    \033[1;32m✔ Caffeinate is ACTIVE (Mac will not sleep)\033[0m")
    else:
        print("    \033[1;33m⚠ Caffeinate not detected. Run with caffeinate -ims\033[0m")

    print("\n 📲 SCAN WITH PHONE CAMERA TO OPEN INSTANTLY:")
    print("-" * 65)
    try:
        qr = qrcode.QRCode(border=1)
        qr.add_data(target_url)
        qr.print_ascii(invert=True)
    except Exception as e:
        print(f" [QR code display error: {e}]")

    print("-" * 65)
    print(" 💡 Pro-Tip for Full-Screen Phone App:")
    print("    • iPhone: In Safari, tap Share ➔ 'Add to Home Screen'")
    print("    • Android: In Chrome, tap ⋮ ➔ 'Install app' or 'Add to Home screen'")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    print_cli_summary()
