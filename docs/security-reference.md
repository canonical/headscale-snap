# Security

The snap is strictly confined, and requires the following interfaces:

* network: general network access.
* network-bind: required for listening on a network interface.

The configuration provided by default stores all sensitive data under `/var/snap/headscale/common/internal/`,
which is only accessible by the root user.
However note that you are free to modify the configuration as you wish;
care should be taken to audit the configuration in use.

The snap itself does not directly use any cryptographic functionality.
Please see upstream docs for information about security of Headscale itself.

## Security hardening guidance

The scope of Headscale's configuration is quite large,
covering TLS, DNS, OpenID Connect auth, embedded DERP server, and sensitive file paths.
The [default configuration](../snap/local/default-config.yaml) provides defaults with the aim of being secure:
- TLS certificates from Letsencrypt
- OIDC disabled
- embedded DERP server disabled
- all listen addresses bound to localhost
- sensitive file paths pointing to a root-owned directory with '700' permissions (`/var/snap/headscale/common/internal/`)
- DNS with example configuration with a base domain that **should be updated** (the default is `example.com`) and DNS resolvers pointing to the [1.1.1.1](https://en.wikipedia.org/wiki/1.1.1.1) DNS service

When crafting your configuration for Headscale and preparing to manage and host it,
we recommend:

- Read through the [default configuration](../snap/local/default-config.yaml) for examples of of file paths and such.
- Read through the upstream configuration reference at https://headscale.net/stable/ref/configuration/ .
- Become familiar with Tailscale concepts that may impact secure operation of a Tailscale network, such as [ACLs](https://tailscale.com/kb/1018/acls) for permissions or [custom DERP servers](https://tailscale.com/kb/1118/custom-derp-servers) (Headscale ships an embedded DERP server if required).
- Headscale is smaller in scope than the official Tailscale coordinate server, in that it provides only a single tailnet. The concept of users with Headscale is different, and all users are part of the same tailnet.
- Additionally, many actions require access to the Headscale admin command line (eg. authenticating nodes, generating auth keys, managing users). There is a [remote cli](https://headscale.net/stable/ref/remote-cli/), which is configured for localhost access only by default. Take care if exposing this to a network.
