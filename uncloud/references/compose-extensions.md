# Uncloud Compose File Extensions

Uncloud supports Docker Compose spec with custom `x-*` extensions and some limitations.

## x-ports (Port Publishing)

Replaces the standard `ports:` field. Defines how service ports are exposed externally via Caddy.

### Syntax

```
[bind_address:]host_port:container_port/protocol[@routing]
```

### Protocols

| Protocol | Description |
|----------|-------------|
| `https` | HTTPS via Caddy + automatic Let's Encrypt. `bind_address` is the domain. |
| `http` | HTTP only via Caddy. `bind_address` is the domain. |
| `tcp` | Raw TCP passthrough |
| `udp` | Raw UDP passthrough |

### Examples

```yaml
x-ports:
  # HTTPS with automatic cert (domain:container_port/https)
  - app.example.com:3000/https

  # HTTP only
  - app.example.com:3000/http

  # TCP on all interfaces
  - 5432:5432/tcp

  # TCP on loopback only (host networking)
  - 127.0.0.1:9000:9000/tcp@host

  # TCP on specific IP (e.g. Tailscale address)
  - 100.84.88.5:9000:9000/tcp@host

  # UDP
  - 53:53/udp
```

### Uncloud DNS subdomain (no custom domain)

```yaml
x-ports:
  - 80/https    # Gets assigned <service>.<cluster-id>.uncld.dev
```

## x-machines (Machine Placement)

Restricts which cluster machines a service runs on.

```yaml
services:
  web:
    image: myapp:latest
    x-machines:
      - machine-1
      - machine-2

  db:
    image: postgres:16
    x-machines: machine-db   # Single machine as string
```

- Use `uc machine ls` to see available machine names.
- When `x-machines` is set, `uc build --push` and `uc deploy` automatically target only those machines.

## deploy.mode

Controls replication strategy.

```yaml
deploy:
  mode: global        # One container per machine (stateful services)
  mode: replicated    # Specified replica count (default)

deploy:
  mode: replicated
  replicas: 3
```

**Use `global` for**: databases, caches, file storage — anything with local persistent volumes.
**Use `replicated` for**: stateless web/worker services that should scale horizontally.

**Note**: Global services do NOT auto-scale when new machines join. Re-run `uc deploy` after adding a machine.

## configs (Non-sensitive config files)

Mount configuration files into containers at runtime.

```yaml
configs:
  nginx_conf:
    file: ./nginx.conf    # Relative to compose file
  app_config:
    content: |            # Inline content (env var interpolation supported)
      key=${MY_ENV_VAR}

services:
  web:
    configs:
      - source: nginx_conf
        target: /etc/nginx/nginx.conf
        mode: 0644
        uid: "0"
        gid: "0"
```

Limitations:
- Only long syntax supported (explicit `source` + `target`)
- Short syntax not supported
- External configs not supported — all configs must be defined in the compose file
- Content is transmitted via gRPC at deploy time; files exist only during container lifetime

## Supported Standard Fields

Uncloud supports a subset of Docker Compose spec. Key supported fields:

```yaml
services:
  myservice:
    image: myimage:tag
    build:
      context: .
      dockerfile: Dockerfile
      args:
        KEY: value
      platforms:
        - linux/amd64
        - linux/arm64
    command: [override command]
    entrypoint: [override entrypoint]
    environment:
      KEY: value
      SECRET: ${FROM_ENV_FILE}
    env_file: .env
    volumes:
      - named_volume:/path/in/container
      - /host/path:/container/path
    depends_on:
      other_service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/up"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
    deploy:
      mode: global | replicated
      replicas: N
    pull_policy: always | missing | never
    user: "1000:1000"
    privileged: false
    networks:
      - mynetwork

networks:
  mynetwork:
    external: true
    name: actual-network-name

volumes:
  named_volume:   # Created on deploy
```

## Image Tag Templates

Dynamic image tags using Go template syntax:

```yaml
services:
  web:
    build: .
    image: myapp:{{gitdate "20060102"}}.{{gitsha 7}}.${GITHUB_RUN_ID:-local}{{if .Git.IsDirty}}.dirty{{end}}
```

Available template functions:
- `gitdate "format"` — current date in Go time format
- `gitsha N` — first N characters of git SHA
- `.Git.IsDirty` — whether working tree has uncommitted changes

## Environment Variable Interpolation

```yaml
environment:
  DATABASE_URL: postgres://user:${DB_PASSWORD}@db:5432/mydb
  RAILS_ENV: production
  SECRET_KEY_BASE: ${SECRET_KEY_BASE}  # From shell env or .env file
```

Use `.env` file in same directory as compose file for local overrides.

## Internal DNS (Service Discovery)

Containers can reach each other by service name:

- `<service-name>.internal` → all instances of service (round-robin)
- `<machine-id>.m.<service-name>.internal` → instances on specific machine
- `<machine>.machine.internal` → machine's WireGuard IP

Injected env vars per container:
- `UNCLOUD_MACHINE_ID` — ID of machine container is running on
- `HOSTNAME` — service name with unique suffix (e.g. `worker-c1zd`)
