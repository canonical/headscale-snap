"""Unit tests for .github/scripts/release_instructions.py."""

from release_instructions import MARKER, OWNER, parse_version, render

TRACKS = {"0.26", "0.27", "latest"}
V0271 = ("0.27.1", "0.27")


def test_parse_version():
    assert parse_version("name: headscale\nversion: 0.29.3\n") == ("0.29.3", "0.29")
    assert parse_version("version: '0.29.3'\n") == ("0.29.3", "0.29")
    assert parse_version("version: 0.29.3-beta\n") is None
    assert parse_version("version: 1.0\n") is None
    assert parse_version("parts:\n  x:\n    version: 1.2.3\n") is None


def test_unchanged_version_renders_nothing():
    assert render(V0271, V0271, TRACKS) == ""


def test_minor_bump_with_missing_track():
    report = render(V0271, ("0.29.3", "0.29"), TRACKS)
    assert report.startswith(MARKER)
    assert "`0.29.3` (track `0.29`)" in report
    assert f"cc {OWNER}" in report
    assert "**Track `0.29` is not visible in the Snap Store.**" in report
    assert "https://api.charmhub.io/v1/snap/headscale/tracks" in report
    assert '-d \'[{"name": "0.29", "version-pattern": "0.29.*"}]\'' in report
    assert "`0.27` -> `0.29`" in report
    assert "If branch `0.27` exists, repository admin needs to protect it." in report
    assert "can merge without further action" not in report


def test_patch_bump_with_existing_track():
    report = render(V0271, ("0.27.2", "0.27"), TRACKS)
    assert "**Track `0.27` exists.**" in report
    assert "can merge without further action" in report
    assert "cc " not in report
    assert "curl" not in report
    assert "Minor line changes" not in report


def test_store_lookup_failed():
    report = render(V0271, ("0.27.2", "0.27"), None)
    assert "Could not check whether track `0.27` exists" in report
    assert "curl" in report
    assert f"cc {OWNER}" in report


def test_invalid_version_not_echoed():
    head = parse_version("version: 0.27.2`@team/everyone`\n")
    report = render(V0271, head, TRACKS)
    assert "cannot derive a `MAJOR.MINOR` track" in report
    assert "@team/everyone" not in report
