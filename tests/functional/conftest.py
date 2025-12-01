import os
import subprocess
import time

import pytest


@pytest.fixture(scope="session", autouse=True)
def install_headscale_snap():
    """Install the headscale snap for testing."""
    test_snap = os.environ.get("TEST_SNAP")

    # Clean up any existing installation and data
    result = subprocess.run(
        "snap list headscale".split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    if result.returncode == 0:
        subprocess.check_call("sudo snap remove headscale --purge".split())
        time.sleep(2)

    if os.path.exists("/var/snap/headscale"):
        subprocess.check_call("sudo rm -rf /var/snap/headscale".split())

    # Install the snap
    subprocess.check_call(f"sudo snap install --dangerous {test_snap}".split())
    time.sleep(2)

    yield

    subprocess.check_call("sudo snap remove headscale --purge".split())
