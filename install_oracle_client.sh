#!/bin/bash

# Oracle Instant Client ARM64 Recovery Script for PROMISE AI
# This script installs the Oracle Instant Client and dependencies
# Run this after environment resets when Oracle connection fails

set -e

echo "======================================"
echo "🔧 Oracle ARM64 Client Recovery Script"
echo "======================================"
echo ""

# Check architecture
ARCH=$(uname -m)
echo "✓ Detected architecture: $ARCH"

if [ "$ARCH" != "aarch64" ]; then
    echo "❌ ERROR: This script is for ARM64 (aarch64) architecture only"
    exit 1
fi

# Install system dependencies
echo ""
echo "📦 Step 1/4: Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq unzip file libaio1 > /dev/null 2>&1
echo "✓ Installed: unzip, file, libaio1"

# Download Oracle Instant Client
echo ""
echo "📥 Step 2/4: Downloading Oracle Instant Client 19.23 (ARM64)..."
cd /tmp
if [ ! -f "instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip" ]; then
    wget -q https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip
    echo "✓ Downloaded Oracle client package"
else
    echo "✓ Package already exists in /tmp"
fi

# Extract Oracle Instant Client
echo ""
echo "📂 Step 3/4: Extracting to /opt/oracle/..."
mkdir -p /opt/oracle
unzip -q -o instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip -d /opt/oracle/
echo "✓ Extracted to /opt/oracle/instantclient_19_23/"

# Configure environment
echo ""
echo "⚙️  Step 4/4: Configuring environment..."
export LD_LIBRARY_PATH=/opt/oracle/instantclient_19_23:$LD_LIBRARY_PATH
echo "✓ Set LD_LIBRARY_PATH"

# Verify installation
echo ""
echo "🔍 Verifying installation..."
if [ -f "/opt/oracle/instantclient_19_23/libclntsh.so" ]; then
    echo "✓ libclntsh.so found"
    file /opt/oracle/instantclient_19_23/libclntsh.so | grep -q "ARM aarch64" && echo "✓ Correct architecture (ARM64)"
else
    echo "❌ ERROR: libclntsh.so not found!"
    exit 1
fi

# Check dependencies
echo ""
echo "🔍 Checking library dependencies..."
ldd /opt/oracle/instantclient_19_23/libclntsh.so | grep -q "libaio" && echo "✓ libaio linked correctly"

echo ""
echo "======================================"
echo "✅ Oracle Client Installation Complete!"
echo "======================================"
echo ""
echo "📝 Next Steps:"
echo "1. Restart backend: sudo supervisorctl restart backend"
echo "2. Check logs: tail -f /var/log/supervisor/backend.err.log"
echo "3. Test connection: curl http://localhost:8001/api/datasets"
echo ""
