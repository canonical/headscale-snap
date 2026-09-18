"""Unit tests for .github/scripts/release_track.py."""

import os
import subprocess

import pytest
from release_track import derive, newest_revisions, push, release, track_names

# `snapcraft revisions headscale` on 2026-09-15.
REVISIONS = """\
Rev.    Uploaded              Arches    Version    Channels
67      2026-02-27T11:59:29Z  amd64     0.27.1     latest/edge*
66      2026-02-27T11:59:27Z  arm64     0.27.1     latest/edge*
65      2026-01-27T07:18:19Z  arm64     0.27.1     0.27/stable*,latest/candidate*,latest/edge
64      2026-01-27T07:17:31Z  amd64     0.27.1     0.27/stable*,latest/candidate*,latest/edge
59      2025-12-15T08:11:44Z  arm64     0.26.1     latest/edge
"""

# `snapcraft tracks headscale` on 2026-09-15.
TRACKS = """\
Name    Status    Creation-Date         Version-Pattern
latest  active    -                     -
0.26    active    2025-11-06T10:26:46Z  -
0.27    default   2026-01-23T03:52:51Z  -
"""

# Logs its arguments and prints the captured tables. $TRACKS_FAIL / $REVISIONS_FAIL /
# $RELEASE_FAIL make that subcommand exit 1 with an error on stderr.
FAKE_SNAPCRAFT = """\
#!/bin/sh
echo "$*" >> "$SNAPCRAFT_LOG"
fail() { echo "Store operation failed: $1" >&2; exit 1; }
case "$1" in
  tracks) [ -n "$TRACKS_FAIL" ] && fail tracks; cat "$FIXTURES/tracks.txt" ;;
  revisions) [ -n "$REVISIONS_FAIL" ] && fail revisions; cat "$FIXTURES/revisions.txt" ;;
  release) [ -n "$RELEASE_FAIL" ] && fail release; echo released ;;
esac
"""


def git(cwd, *args):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def remote_refs(remote):
    out = git(remote, "for-each-ref", "--format=%(refname) %(objectname)")
    return dict(line.split() for line in out.splitlines())


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Return a bare remote and two consecutive commits, with cwd in the work tree."""
    remote, work = tmp_path / "remote.git", tmp_path / "work"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    git(tmp_path, "init", "-q", str(work))
    shas = []
    for message in ("first", "second"):
        git(
            work,
            *("-c", "user.name=test", "-c", "user.email=test@example.com"),
            *("-c", "commit.gpgsign=false"),
            *("commit", "-q", "--allow-empty", "-m", message),
        )
        shas.append(git(work, "rev-parse", "HEAD"))
    monkeypatch.chdir(work)
    return str(remote), shas


@pytest.fixture
def snapcraft_calls(tmp_path, monkeypatch):
    """Put a fake snapcraft first on PATH; return a function listing its calls."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "snapcraft"
    fake.write_text(FAKE_SNAPCRAFT)
    fake.chmod(0o755)
    (tmp_path / "tracks.txt").write_text(TRACKS)
    (tmp_path / "revisions.txt").write_text(REVISIONS)
    log = tmp_path / "calls.log"
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("SNAPCRAFT_LOG", str(log))
    monkeypatch.setenv("FIXTURES", str(tmp_path))
    return lambda: log.read_text().splitlines() if log.exists() else []


def test_newest_revisions():
    assert newest_revisions(REVISIONS, "0.27.1") == ["67", "66"]
    assert newest_revisions(REVISIONS, "0.26.1") == ["59"]
    assert newest_revisions(REVISIONS, "9.9.9") == []


def test_track_names():
    assert track_names(TRACKS) == {"latest", "0.26", "0.27"}


def test_derive():
    assert derive("name: headscale\nversion: 0.29.3\n") == ("0.29.3", "0.29")
    with pytest.raises(SystemExit):
        derive("version: 1.0\n")


def test_push_creates_advances_and_rejects_stale(repo):
    remote, (first, second) = repo
    push(first, "0.27.1", "0.27", remote)
    assert remote_refs(remote) == {"refs/heads/0.27": first, "refs/tags/0.27.1": first}

    push(first, "0.27.1", "0.27", remote)  # re-run of the same commit is a no-op
    push(second, "0.27.1", "0.27", remote)  # same-version merge: branch advances, tag stays
    assert remote_refs(remote) == {"refs/heads/0.27": second, "refs/tags/0.27.1": first}

    with pytest.raises(subprocess.CalledProcessError):  # stale run behind a newer one
        push(first, "0.27.1", "0.27", remote)


def test_release_success(snapcraft_calls):
    assert release("0.27.1", "0.27") == 0
    assert snapcraft_calls() == [
        "tracks headscale",
        "revisions headscale",
        "release headscale 67 0.27/edge",
        "release headscale 66 0.27/edge",
    ]


def test_release_missing_track_is_a_clean_skip(snapcraft_calls):
    assert release("0.29.3", "0.29") == 0
    assert snapcraft_calls() == ["tracks headscale"]


def test_release_no_revisions(snapcraft_calls):
    assert release("0.27.9", "0.27") == 1
    assert snapcraft_calls() == ["tracks headscale", "revisions headscale"]


@pytest.mark.parametrize("failing", ["TRACKS_FAIL", "REVISIONS_FAIL", "RELEASE_FAIL"])
def test_release_store_failure_raises(snapcraft_calls, monkeypatch, failing):
    monkeypatch.setenv(failing, "1")
    with pytest.raises(subprocess.CalledProcessError):
        release("0.27.1", "0.27")
    assert snapcraft_calls()[-1].split()[0] == failing.split("_")[0].lower()
