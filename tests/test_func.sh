#!/bin/bash
set -e

echo "=== Headscale Snap Simple Configuration Check ==="

if [ ! -f "$TEST_SNAP" ]; then
    echo "Snap file not found at: $TEST_SNAP"
    exit 1
fi

echo "Testing: $TEST_SNAP"

# Clean up any existing installation and data if present
echo ""
echo "=== Cleaning up any existing headscale snap installation... ==="
if snap list headscale &> /dev/null; then
    echo "Removing existing headscale snap..."
    sudo snap remove headscale --purge
    sleep 2
fi

if [ -d "/var/snap/headscale" ]; then
    echo "Removing leftover snap data directory..."
    sudo rm -rf /var/snap/headscale
fi

echo ""
echo "=== Installing snap... ==="
sudo snap install --dangerous "$TEST_SNAP"

# Run config test
echo ""
echo "=== Running headscale configtest... ==="
sudo headscale configtest

# Verify the service started successfully
echo ""
echo "=== Verifying service status... ==="
sleep 2

# Check if the service is active
if ! systemctl is-active --quiet snap.headscale.headscaled.service; then
    echo "Headscale service is not running!"
    sudo journalctl -u snap.headscale.headscaled.service -n 20
    sudo snap remove headscale --purge
    exit 1
fi

echo "Service is running successfully"

# Show recent logs
echo "=== Recent service logs ==="
sudo journalctl -u snap.headscale.headscaled.service -n 5 --no-pager

# Cleanup
echo ""
echo "=== Cleaning up... ==="
sudo snap remove headscale --purge

echo ""
echo "=== All tests passed! ==="
