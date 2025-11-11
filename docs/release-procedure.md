# Headscale Snap Release Procedure

This document outlines how we publish and promote the Headscale snap on Snapcraft, ensuring a predictable flow from development to production while containing risk from upstream breaking changes.

## Automatic release to latest/edge

Whenever a new commit lands in the main branch, the CI pipeline automatically builds and releases a fresh snap to the latest/edge channel. 

## Promotion to latest/candidate

After internal validation confirms that the build behaves as expected, we promote it from latest/edge to latest/candidate.

## Promotion to dedicated track's stable channel

After further validation, we promote it to dedicated track's stable channel. There are two situations.

### Case #1: Bugfix releases

If the release contains only bugfixes, we promote it into the corresponding minor version’s stable track.
Example: a fix for the 0.26, it goes to 0.26/stable.

### Case #2: New minor versions

If the release introduces a new minor version, we create a new dedicated track.
Example: for version 0.27, we create and publish to 0.27/stable.

# Production usage guidance

While creating a track per minor version is not common, Headscale’s upstream sometimes introduces breaking changes between minor releases. Maintaining isolated tracks protects production environments from unexpected disruption and gives operators a clear upgrade path.

Production sites should stick on a specific version’s stable channel (for example, 0.26/stable) to ensure consistent behavior. Before migrating to a different stable track, review the [release notes](https://github.com/juanfont/headscale/releases) and handle any breaking changes that may require operational adjustments.
