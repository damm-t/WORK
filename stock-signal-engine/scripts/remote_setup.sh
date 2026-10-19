#!/bin/bash
# ==============================================================================
#   QUANT DESK — 24/7 REMOTE ENGINE BOOTSTRAP SCRIPT (WSL2 / Ubuntu)
#   Run this script inside your Windows WSL2 (Ubuntu) terminal:
#     bash scripts/remote_setup.sh
# ==============================================================================
set -euo pipefail

echo "==========================================================================="
echo "   🚀 PREPARING 24/7 QUANT DESK RUNTIME (WSL2 / UBUNTU LINUX)"
echo "==========================================================================="

# 1. Update APT and install essential packages
echo "📦 Installing system dependencies (Python 3, OpenSSH, rsync, build tools)..."
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    curl \
    rsync \
    openssh-server \
    git \
    net-tools \
    procps \
    libgomp1

# 2. Configure and start SSH Server
echo "🔐 Configuring OpenSSH Server..."
sudo mkdir -p /var/run/sshd
sudo ssh-keygen -A 2>/dev/null || true

# Ensure PasswordAuthentication is allowed for initial SSH key copying
sudo sed -i 's/^#*PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config 2>/dev/null || true
sudo sed -i 's/^#*PermitRootLogin .*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config 2>/dev/null || true

# Enable systemd for WSL if available, or start ssh service
if [ -d /run/systemd/system ]; then
    sudo systemctl enable ssh 2>/dev/null || true
    sudo systemctl restart ssh 2>/dev/null || true
else
    sudo service ssh restart
    # Auto-start SSH in ~/.bashrc if systemd is not active
    if ! grep -q "service ssh status" ~/.bashrc 2>/dev/null; then
        echo "sudo service ssh status >/dev/null 2>&1 || sudo service ssh start >/dev/null 2>&1" >> ~/.bashrc
    fi
fi

# 3. Setup workspace directory
TARGET_DIR="$HOME/stock-signal-engine"
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

# 4. Create isolated Python virtual environment
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment in $TARGET_DIR/.venv ..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip setuptools wheel
fi

# 5. Detect IP Addresses
LAN_IP=$(hostname -I | awk '{print $1}')
USER_NAME=$(whoami)

echo ""
echo "==========================================================================="
echo "   ✅ 24/7 REMOTE HOST ENVIRONMENT READY!"
echo "==========================================================================="
echo "  • WSL2 Host User : $USER_NAME"
echo "  • Host IP Address: $LAN_IP"
echo "  • Deployment Dir : $TARGET_DIR"
echo "  • SSH Server     : Active (Port 22)"
echo ""
echo "---------------------------------------------------------------------------"
echo "👉 NEXT STEP ON YOUR MAC:"
echo "---------------------------------------------------------------------------"
echo "1. (One-time) Copy your Mac SSH key to this machine:"
echo "   ssh-copy-id $USER_NAME@$LAN_IP"
echo ""
echo "2. Deploy and start all 4 desks from your Mac:"
echo "   ./quant deploy $USER_NAME@$LAN_IP"
echo ""
echo "3. Open the encrypted tunnel to view the cockpit on Mac localhost:8080:"
echo "   ./quant tunnel $USER_NAME@$LAN_IP"
echo "==========================================================================="
