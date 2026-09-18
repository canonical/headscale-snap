#!/usr/bin/env python3
"""Steps of the "Release to version track" workflow.

Usage: release_track.py push|release

push:    create/advance branch X.Y at $SHA and tag X.Y.Z if the tag is absent.
release: release the newest store revision per architecture of X.Y.Z to X.Y/edge.
"""

import os
import subprocess
import sys
from pathlib import Path

from release_instructions import SNAP, parse_version

SNAPCRAFT_YAML = "snap/snapcraft.yaml"
STEPS = ("push", "release")


def track_names(table: str) -> set[str]:
    """Return the track names in ``snapcraft tracks`` output.

    ``table`` is "Name Status Creation-Date Version-Pattern" and one row per track.
    """
    rows = (row.split() for row in table.splitlines())
    return {fields[0] for fields in rows if fields and fields[0] != "Name"}


def newest_revisions(table: str, version: str) -> list[str]:
    """Return the newest revision per architecture for ``version``.

    ``table`` is ``snapcraft revisions`` output: "Rev. Uploaded Arches Version Channels",
    newest first, one architecture per row.
    """
    revisions: list[str] = []
    seen_arches: set[str] = set()
    for row in table.splitlines():
        fields = row.split()
        if len(fields) < 4 or not fields[0].isdigit():
            continue
        revision, _, arch, row_version = fields[:4]
        if row_version == version and arch not in seen_arches:
            seen_arches.add(arch)
            revisions.append(revision)
    return revisions


def derive(snapcraft: str) -> tuple[str, str]:
    """Return ``(version, track)`` from snapcraft.yaml text; exit if it is not ``X.Y.Z``."""
    parsed = parse_version(snapcraft)
    if parsed is None:
        sys.exit(f"version: in {SNAPCRAFT_YAML} is not X.Y.Z")
    return parsed


def push(sha: str, version: str, track: str, remote: str) -> None:
    """Push ``sha`` to branch ``track`` (non-force) and to tag ``version`` if absent.

    Raises:
        CalledProcessError: when the branch is already ahead (a newer run pushed first).
    """
    subprocess.run(["git", "push", remote, f"{sha}:refs/heads/{track}"], check=True)
    tag = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--tags", remote, f"refs/tags/{version}"],
        stdout=subprocess.DEVNULL,
    )
    if tag.returncode == 0:
        # Snap-only merges keep the version, so the tag marks its first release.
        print(f"Tag {version} already exists; leaving it in place.")
    elif tag.returncode == 2:  # --exit-code: no matching ref
        subprocess.run(["git", "push", remote, f"{sha}:refs/tags/{version}"], check=True)
    else:
        raise subprocess.CalledProcessError(tag.returncode, tag.args)


def release(version: str, track: str) -> int:
    """Release the newest revisions of ``version`` to ``track``/edge; return an exit code.

    A missing track is a supported outcome (the line was not created), not a failure.
    """
    tracks = subprocess.run(
        ["snapcraft", "tracks", SNAP], stdout=subprocess.PIPE, text=True, check=True
    ).stdout
    if track not in track_names(tracks):
        print(f"::notice::track {track} not created, line not supported; skipping")
        return 0
    table = subprocess.run(
        ["snapcraft", "revisions", SNAP], stdout=subprocess.PIPE, text=True, check=True
    ).stdout
    revisions = newest_revisions(table, version)
    if not revisions:
        print(f"::error::no store revisions found for version {version}")
        return 1
    for revision in revisions:
        subprocess.run(["snapcraft", "release", SNAP, revision, f"{track}/edge"], check=True)
    return 0


def main() -> int:
    """Run the requested step for the version in snap/snapcraft.yaml."""
    if len(sys.argv) != 2 or sys.argv[1] not in STEPS:
        sys.exit("usage: release_track.py push|release")
    version, track = derive(Path(SNAPCRAFT_YAML).read_text(encoding="utf-8"))
    try:
        if sys.argv[1] == "push":
            remote = (
                f"https://x-access-token:{os.environ['GH_TOKEN']}"
                f"@github.com/{os.environ['REPO']}.git"
            )
            push(os.environ["SHA"], version, track, remote)
            return 0
        return release(version, track)
    except subprocess.CalledProcessError as error:
        print(f"::error::{error.cmd[0]} {error.cmd[1]} failed with exit code {error.returncode}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
