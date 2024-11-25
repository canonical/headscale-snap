# Headscale snap

This repository contains the snap package sources for [Headscale](https://github.com/juanfont/headscale).

## Build the snap


You can build the snap locally with:

```
snapcraft --use-lxd
```

## Confinement

The snap is strictly confined, and requires the following interfaces:

- [network](https://snapcraft.io/docs/network-interface): general network access.
- [network-bind](https://snapcraft.io/docs/network-bind-interface): required for listening on a network interface.

## Usage

TODO: expand this

- There is `headscaled`, a snap service which runs `headscale serve`.
- There is also the `headscale` command, to manage headscale.
- A config file must be placed in `/var/snap/headscale/current/.headscale/config.yaml`.
  - TODO: should this be in the snap common dir instead?
  - Contents must update paths to be in a snap data dir for headscale (most paths are `/var/run/headscale/*` by default).

## License

This packaging repository is released under the BSD 3-Clause "New" or "Revised" license.

Headscale is released under the BSD 3-Clause "New" or "Revised" license.
Please see the upstream repository for more information: https://github.com/juanfont/headscale
