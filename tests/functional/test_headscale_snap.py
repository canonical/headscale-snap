import subprocess


class TestHeadscaleSnap:
    """Test suite for headscale snap installation and basic functionality."""

    def test_config_validation(self) -> None:
        """Test that the default configuration passes headscale configtest."""
        result = subprocess.run(
            "sudo headscale configtest".split(), capture_output=True, text=True
        )

        assert result.returncode == 0, (
            f"headscale configtest failed with return code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_service_active(self) -> None:
        """Test that the headscaled service is active."""
        service_name = "snap.headscale.headscaled.service"
        result = subprocess.run(
            f"sudo systemctl is-active {service_name}".split(), capture_output=True, text=True
        )

        assert result.returncode == 0, (
            f"{service_name} is not active\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
