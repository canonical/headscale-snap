#!/usr/bin/env python3
"""Report config-key drift between our snap default-config and upstream headscale.

Compares dotted key paths between ``snap/local/default-config.yaml``and upstream
``config-example.yaml`` at the git tag matching ``snap/snapcraft.yaml``'s ``version:`` field.

Renders a Markdown report to stdout for a sticky pull-request comment.
"""

import argparse
import re
import sys
import urllib.error
import urllib.request

import yaml

MARKER = "<!-- config-drift-report -->"
UPSTREAM_FILE = "config-example.yaml"
DEFAULT_REPO = "juanfont/headscale"
DEFAULT_CONFIG = "snap/local/default-config.yaml"
DEFAULT_SNAPCRAFT = "snap/snapcraft.yaml"
VERSION_RE = re.compile(r"^version:\s*(\S+)", re.MULTILINE)


def flatten_keys(node: object, prefix: str = "") -> set[str]:
    """Return the set of dotted leaf-key paths in a parsed YAML mapping."""
    paths: set[str] = set()
    if isinstance(node, dict) and node:
        for key, value in node.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            child_paths = flatten_keys(value, child_prefix)
            paths |= child_paths if child_paths else {child_prefix}
    return paths


def read_version(snapcraft_path: str) -> str:
    """Return the raw ``version:`` value from a snapcraft.yaml file."""
    with open(snapcraft_path, encoding="utf-8") as handle:
        match = VERSION_RE.search(handle.read())
    if match is None:
        raise ValueError(f"no `version:` field in `{snapcraft_path}`")
    return match.group(1).strip("\"'")


def load_keys(config_path: str) -> set[str]:
    """Load a YAML mapping file and flatten it to a set of dotted key paths."""
    with open(config_path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"`{config_path}` is not a YAML mapping")
    return flatten_keys(data)


def fetch_upstream_keys(repo: str, version: str) -> tuple[set[str] | None, str | None]:
    """Fetch upstream ``config-example.yaml`` at ``v{version}`` and flatten it."""
    url = f"https://raw.githubusercontent.com/{repo}/v{version}/{UPSTREAM_FILE}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None, f"`{repo}@v{version}` has no `{UPSTREAM_FILE}` (tag not published yet?)"
        return None, f"HTTP {error.code} fetching `{url}`"
    except urllib.error.URLError as error:
        return None, f"could not fetch `{url}`: {error.reason}"
    data = yaml.safe_load(body)
    if not isinstance(data, dict):
        return None, f"`{repo}@v{version}:{UPSTREAM_FILE}` is not a YAML mapping"
    return flatten_keys(data), None


def render(
    version: str,
    repo: str,
    config_path: str,
    removed: set[str],
    added: set[str],
) -> str:
    """Return the Markdown drift report, marker line first."""
    lines = [MARKER, f"### Config drift vs upstream `v{version}`", ""]
    if not removed and not added:
        lines += ["No config-key drift detected against upstream!", ""]
    if removed:
        lines += [
            "**Removed upstream, still in our default-config** "
            "(these will fail `headscale configtest`):",
            *(f"- `{key}`" for key in sorted(removed)),
            "",
        ]
    if added:
        lines += [
            "**New upstream keys not in our default-config** (review whether to expose):",
            *(f"- `{key}`" for key in sorted(added)),
            "",
        ]
    lines += [
        f"Ours: `{config_path}` · Upstream: `{repo}@v{version}:{UPSTREAM_FILE}`",
        "",
        "_Advisory, key-level only: it cannot see a change to a key's accepted "
        "values or semantics. `headscale configtest` in the functional tests "
        "remains the gate._",
    ]
    return "\n".join(lines)


def render_unavailable(version: str, repo: str, reason: str) -> str:
    """Return the report for when the comparison could not be made."""
    return "\n".join(
        [
            MARKER,
            f"### Config drift vs upstream `v{version}`",
            "",
            f"Could not compare against `{repo}`: {reason}",
            "",
            "_Advisory only; this does not affect the pull request._",
        ]
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Report headscale config-key drift for a pull-request comment."
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--snapcraft", default=DEFAULT_SNAPCRAFT)
    parser.add_argument(
        "--version", default=None, help="Override the version read from snapcraft.yaml."
    )
    parser.add_argument("--repo", default=DEFAULT_REPO)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Emit the Markdown report to stdout; always exit 0 (advisory only)."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        version = args.version or read_version(args.snapcraft)
        ours = load_keys(args.config)
        upstream, reason = fetch_upstream_keys(args.repo, version)
    except Exception as error:  # noqa: BLE001 - advisory tool must never fail the PR
        print(render_unavailable(args.version or "unknown", args.repo, str(error)))
        return 0
    if upstream is None:
        print(render_unavailable(version, args.repo, reason))
        return 0
    print(render(version, args.repo, args.config, ours - upstream, upstream - ours))
    return 0


if __name__ == "__main__":
    sys.exit(main())
