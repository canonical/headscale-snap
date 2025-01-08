# Configuration reference

Example configuration can be found in ../snap/local/default-config.yaml - this is also the default configuration created when the snap is first installed.
The Headscale service expects to find the configuration file at `/var/snap/headscale/common/config.yaml`.

You are free to edit the configuration file as required.
Please note that any file paths must be within the standard directories that the strictly confined snap is allowed access to though.
See https://snapcraft.io/docs/data-locations for more information.

We recommend putting all paths under `/var/snap/headscale/common/`.
This is where the config file is found.
The snap also creates `/var/snap/headscale/common/internal/` as a secure directory (only root accessible),
where the default config places all sensitive files.

Headscale must be restarted manually for any changed config to take affect:

```
sudo snap restart headscale
```
