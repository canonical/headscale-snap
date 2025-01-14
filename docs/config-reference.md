# Configuration reference

Example configuration can be found in [../snap/local/default-config.yaml](../snap/local/default-config.yaml)
This is also the default configuration created when the snap is first installed.

See https://headscale.net/stable/ref/configuration/ for upstream documentation on configuration.
Note that the Headscale service running in the snap expects to find the configuration file at `/var/snap/headscale/common/config.yaml`;
other paths are not supported.

You are free to edit the configuration file as required, as well as any extra files such as policies or DERP maps.
Please note that any file paths must be within the standard directories that the strictly confined snap is allowed access to though.
See https://snapcraft.io/docs/data-locations for more information.

We recommend putting all file paths within `/var/snap/headscale/common/`.
This is where the config file is found.

The snap also creates `/var/snap/headscale/common/internal/` as a secure directory (only root accessible) for sensitive data.
The default config places all sensitive files there.

Headscale must be restarted manually for any changed config to take affect:

```
sudo snap restart headscale
```
