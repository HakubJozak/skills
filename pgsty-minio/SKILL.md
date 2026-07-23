---
name: pgsty-minio
description: Deploy and manage MinIO object storage using the pgsty/minio FOSS fork (community-maintained, AGPLv3). Use when deploying MinIO containers, configuring S3-compatible storage, creating buckets and policies, setting up public file serving, or integrating MinIO with Docker Compose / uncloud. Triggers on "minio", "pgsty/minio", "object storage", "S3 bucket", "mc alias", "public file serving via minio".
---

# pgsty/minio — FOSS MinIO Fork

Community-maintained fork by Pigsty. Minimal changes from upstream: restored embedded
management console, updated module paths. Licensed AGPLv3.

- Server image: `pgsty/minio` ([Docker Hub](https://hub.docker.com/r/pgsty/minio))
- Client image: `pgsty/mc` ([Docker Hub](https://hub.docker.com/r/pgsty/mc))
- The server image bundles `mcli` (and `mc` symlink) from `pgsty/mc`
- Console: `georgmangold/console` (restored community fork)
- Docs site: https://silo.pigsty.io
- Source: https://github.com/pgsty/minio / https://github.com/pgsty/mc

For detailed environment variables and mc command reference, see:
- `references/environment-variables.md`
- `references/mc-commands.md`

## Container Deployment

### Ports

| Port | Purpose |
|------|---------|
| 9000 | S3 API |
| 9001 | Web Console |

### Required Environment Variables

```
MINIO_ROOT_USER       # Admin username (min 3 chars)
MINIO_ROOT_PASSWORD   # Admin password (min 8 chars)
```

### Docker Compose Service

```yaml
minio:
  image: pgsty/minio:RELEASE.2026-04-17T00-00-00Z
  command: server /data --console-address ":9001"
  environment:
    MINIO_ROOT_USER: ${MINIO_ROOT_USER}
    MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
  volumes:
    - minio_data:/data
  ports:
    - "9000:9000"
    - "9001:9001"
  healthcheck:
    test: ["CMD", "mc", "ready", "local"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Uncloud Compose (pinned, global mode)

For deploying on a specific machine via uncloud with `mode: global`:

```yaml
minio:
  image: pgsty/minio:RELEASE.2026-04-17T00-00-00Z
  command: server /data --console-address ":9001"
  environment:
    MINIO_ROOT_USER: ${MINIO_ROOT_USER}
    MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
  volumes:
    - /srv/harbor/storage:/data    # or named volume
  x-ports:
    - 127.0.0.1:9000:9000/tcp@host
    - 127.0.0.1:9001:9001/tcp@host
  x-machines: ckdm-hub             # pin to specific machine
  deploy:
    mode: global
  healthcheck:
    test: ["CMD", "mc", "ready", "local"]
    interval: 10s
    timeout: 5s
    retries: 5
```

Expose publicly via uncloud Caddy or Cloudflare tunnel — do NOT bind ports to `0.0.0.0`.

## Client (mc) Setup

The `mc` CLI is bundled inside `pgsty/minio`. Run it via exec or use a sidecar `pgsty/mc` container.

```bash
# From inside the running container (uc exec or docker exec):
mc alias set local http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD

# Create a bucket
mc mb local/my-bucket

# Set bucket policy to public (download-only)
mc anonymous set download local/my-bucket

# Upload files
mc cp /path/to/files/* local/my-bucket/

# Mirror a directory (sync)
mc mirror /source/dir local/my-bucket/prefix/

# List objects
mc ls local/my-bucket/
mc ls --recursive local/my-bucket/

# Get bucket/object info
mc stat local/my-bucket
mc du local/my-bucket
```

## Public File Serving

MinIO natively serves objects over HTTP on port 9000. To serve files publicly:

1. Create bucket: `mc mb local/public-files`
2. Set anonymous download: `mc anonymous set download local/public-files`
3. Upload files: `mc mirror /srv/data/ local/public-files/`
4. Files accessible at: `http://<host>:9000/public-files/<path>`

For production, place behind Caddy/Cloudflare for HTTPS and caching.

### Bucket Policies

```bash
# Public read-only (anonymous download)
mc anonymous set download local/my-bucket

# Public read+list
mc anonymous set public local/my-bucket

# Remove public access
mc anonymous set none local/my-bucket

# Check current policy
mc anonymous get local/my-bucket
```

## Useful Admin Commands

```bash
# Server info
mc admin info local

# Service restart
mc admin service restart local

# Check health / readiness
mc ready local

# Disk usage
mc du local/

# Server logs
mc admin logs local
```

## Healthcheck

The bundled `mc` makes healthchecks simple — `mc ready local` returns 0 when the server
is ready. The container auto-configures the `local` alias pointing at `http://localhost:9000`.

## Data Volume

MinIO stores all data (objects, config, IAM) under the volume path passed to `minio server`.
A single `/data` volume is fine for single-node deployment. For erasure coding, mount
multiple drives as `/data1`, `/data2`, etc. and pass them all to `minio server`.

## TLS

Place `public.crt` and `private.key` in `${HOME}/.minio/certs` inside the container
(or use `--certs-dir`). MinIO auto-enables HTTPS when certs are present. In uncloud/harbor
setups, TLS termination is typically handled by Caddy or Cloudflare — MinIO runs plain HTTP.
