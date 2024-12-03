# Configuration reference

Headscale takes a configuration file.
This snap manages the configuration file for you, and automatically includes the `-c <path-to-managed-config-file>` option to headscale and the headscale service.
This is to make it simpler to manage configuration, and to manage options that can be opinionated within the context of the snap.

You can modify configuration options for the server with snap configuration.
The following configuration options are currently supported:

* `server-url`: The url clients will connect to. [default: `"http://127.0.0.1:8080"`]
* `listen-addr`: Address to bind to on the server. [default: `"127.0.0.1:8080"`]
* `metrics-listen-addr`: Address to listen to /metrics (you may want to keep this endpoint private). [default: `"127.0.0.1:9090"`]
* `grpc-listen-addr`: Address to listen for gRPC. [default: `"127.0.0.1:50443"`]
* `prefixes.v4`: IPv4 prefixes to allocate tailnet addresses from (must be a subnet of 100.64.0.0/10). [default: `"100.64.0.0/10"`]
* `prefixes.v6`: IPv6 prefixes to allocate tailnet addresses from (must be a subnet of fd7a:115c:a1e0::/48). [default: `"fd7a:115c:a1e0::/48"`]
* `tls-cert-path`: Path to tls cert if using pre defined certificates (otherwise Headscale will request one from LetsEncrypt). [default: `""`]
* `tls-key-path`: Path to tls key if using pre defined certificates (otherwise Headscale will request one from LetsEncrypt). [default: `""`]
* `policy.path`: A HuJSON file of ACL policies (see https://tailscale.com/kb/1018/acls for more information). If set, the path must be in a standard directory accessible by the snap (eg. /var/snap/headscale/common/policy.json)  [default: `""`]
* `oidc.only-start-if-oidc-is-available`: Block startup until the OIDC provider is available, otherwise it will fall back to local auth. [default: `true`]
* `oidc.issuer`: (setting an issuer will also enable oidc auth) [default: `""`]
* `oidc.client-id`: Client ID from the OIDC provider [default: `""`]
* `oidc.client-secret`: Client secret from the OIDC provider [default: `""`]
* `oidc.expiry`: Amount of time the node will be authenticated with OIDC before requiring re-authentication. [default: `"180d"`]
* `oidc.strip-email-domain`: If true, the domain of username email address will be removed (eg. `user@example.com` will be transformed to `user`) [default: `true`]

These options must be valid json lists:

* `oidc.scope`: The scopes used in the OIDC flow. [default: `["openid", "profile", "email"]`]
* `oidc.allowed-domains`: List of allowed principal domains. If an authenticated user's domain is not in this list, the authentication request will be rejected. [default: `[]`]
* `oidc.allowed-groups`: Similar to allowed-domains, but for groups. [default: `[]`]
* `oidc.allowed-users`: Similar to allowed-domains, but for users. [default: `[]`]

See https://headscale.net/stable/ref/configuration/ for more information about configuration.
Note that the supported snap config options correspond to the similarly named config options in the config.yaml file.

An example of setting options:

```bash
sudo snap set headscale 'oidc.scope=["openid", "profile", "email"]' server-url=https://myheadscale.example.com:443
```

To view the available config options and their current values:

```
$ sudo snap get headscale
Key                  Value
grpc-listen-addr     127.0.0.1:50443
listen-addr          0.0.0.0:8080
metrics-listen-addr  127.0.0.1:9090
oidc                 {...}
policy               {...}
prefixes             {...}
server-url           http://127.0.0.1:8080
...
```

Headscale must be restarted manually for the changed config to take affect:

```
sudo snap restart headscale
```
