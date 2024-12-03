# Headscale snap

This repository provides a strictly confined snap package for [Headscale](https://github.com/juanfont/headscale).

Please see the listing for [Headscale on the Snap Store](https://snapcraft.io/headscale) for user documentation.

## Local development

You can build the snap locally with:

```
snapcraft --use-lxd
```

The locally built snap must be installed in dangerous mode (because there are no signatures from the Snap Store):

```
sudo snap install --dangerous headscale_*.snap
```


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
