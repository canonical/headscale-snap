# Headscale snap

This repository provides a strictly confined snap package for [Headscale](https://github.com/juanfont/headscale).

For user documentation, please see the listing for [Headscale on the Snap Store](https://snapcraft.io/headscale),
and reference [docs/](./docs/) in this repo.

## Local development

You can build the snap locally with:

```
snapcraft --use-lxd
```

The locally built snap must be installed in dangerous mode (because there are no signatures from the Snap Store):

```
sudo snap install --dangerous headscale_*.snap
```


## License

This packaging repository is released under the BSD 3-Clause "New" or "Revised" license.

Headscale is released under the BSD 3-Clause "New" or "Revised" license.
Please see the upstream repository for more information: https://github.com/juanfont/headscale
