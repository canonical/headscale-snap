#!/usr/bin/env python3
"""Render advisory release instructions for a pull request that changes the snap version.

Usage: release_instructions.py <head snapcraft.yaml> <base snapcraft.yaml>

Prints a Markdown sticky-comment body, or nothing when the version is unchanged.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

SNAP = "headscale"
OWNER = "@h-m-quang-ngo"
MARKER = "<!-- release-instructions -->"
CHANNEL_MAP_URL = f"https://api.snapcraft.io/v2/snaps/info/{SNAP}?fields=channel-map"

# Match full X.Y.Z versions
VERSION_RE = re.compile(r"^version:\s*[\"']?((\d+\.\d+)\.\d+)[\"']?\s*$", re.MULTILINE)
FOOTER = "_Advisory only; this does not affect the pull request._"


def parse_version(snapcraft: str) -> tuple[str, str] | None:
    """Return ``(version, track)`` from snapcraft.yaml text, or None if not ``X.Y.Z``."""
    match = VERSION_RE.search(snapcraft)
    return (match.group(1), match.group(2)) if match else None


def render(
    base: tuple[str, str] | None, head: tuple[str, str] | None, tracks: set[str] | None
) -> str:
    """Return the Markdown report; empty when the version is unchanged."""
    if head == base:
        return ""
    if head is None:
        return "\n".join(
            [
                MARKER,
                "### Release instructions",
                "",
                f"cc {OWNER} : cannot derive a `MAJOR.MINOR` track: `version:` in "
                "`snap/snapcraft.yaml` is not `X.Y.Z`.",
                "",
                FOOTER,
            ]
        )

    version, track = head
    exists = tracks is not None and track in tracks
    old = base[1] if base else None
    minor_change = old is not None and old != track
    lines = [MARKER, f"### Release instructions: `{version}` (track `{track}`)", ""]
    if not exists or minor_change:
        lines += [f"cc {OWNER} : attention needed before merge.", ""]

    if exists:
        lines += [f"**Track `{track}` exists.** No store action needed.", ""]
    else:
        if tracks is None:
            lines.append(
                f"**Could not check whether track `{track}` exists** "
                "(Snap Store lookup failed; see the job log)."
            )
        else:
            lines.append(
                f"**Track `{track}` is not visible in the Snap Store.** Either it has not been "
                "created, or it exists but nothing has been released to it yet."
            )
        lines += [
            "",
            "To support this version, a snap owner creates the track: " "",
            "```sh",
            "# Login to Charmhub (Yes, it is Charmhub!)",
            "charmcraft login --export charmhub-creds.dat",
            "# Create the track in the Snap Store",
            f"curl -sS -X POST https://api.charmhub.io/v1/snap/{SNAP}/tracks \\",
            '  -H "Authorization: Macaroon $(base64 -d charmhub-creds.dat)" \\',
            "  -H 'Content-Type: application/json' \\",
            f'  -d \'[{{"name": "{track}", "version-pattern": "{track}.*"}}]\'',
            "```",
            "Refer to: https://canonical.com/juju/docs/charmcraft/latest/howto/manage-tracks/#create-it-yourself",
            "",
            "Declining the version is supported: skip track creation. Even if the track is not created, "
            "the pull request can still merge and `latest/edge` still receives the snap.",
            "",
        ]

    if minor_change:
        lines += [
            f"**Minor line changes: `{old}` -> `{track}`.** After merge, `main` leaves the "
            f"`{old}` line. If branch `{old}` exists, repository admin needs to protect it.",
            "",
        ]
    elif exists:
        lines += [
            "This pull request can merge without further action (subject to normal review and CI).",
            "",
        ]
    lines.append(FOOTER)
    return "\n".join(lines)


def fetch_tracks() -> set[str] | None:
    """Return the tracks visible in the public Snap Store channel map, or None on failure."""
    request = urllib.request.Request(CHANNEL_MAP_URL, headers={"Snap-Device-Series": "16"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return {entry["channel"]["track"] for entry in json.load(response)["channel-map"]}
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Snap Store lookup failed: {error}", file=sys.stderr)
        return None


def main() -> None:
    """Print the report for ``<head snapcraft.yaml> <base snapcraft.yaml>``."""
    head = parse_version(Path(sys.argv[1]).read_text(encoding="utf-8"))
    base = parse_version(Path(sys.argv[2]).read_text(encoding="utf-8"))
    sys.stdout.write(render(base, head, fetch_tracks()))


if __name__ == "__main__":
    main()
