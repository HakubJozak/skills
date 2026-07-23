# MinIO Server Environment Variables

## Root Credentials

| Variable | Description |
|----------|-------------|
| `MINIO_ROOT_USER` | Admin username (min 3 chars) |
| `MINIO_ROOT_PASSWORD` | Admin password (min 8 chars) |
| `MINIO_ROOT_USER_FILE` | Path to file containing root user (Docker secrets) |
| `MINIO_ROOT_PASSWORD_FILE` | Path to file containing root password (Docker secrets) |

## Storage & Volumes

| Variable | Description |
|----------|-------------|
| `MINIO_VOLUMES` | Storage paths, equivalent to `minio server DIRECTORIES` |

## Site / Region

| Variable | Description |
|----------|-------------|
| `MINIO_SITE_NAME` | Site name, e.g. `"sfo-rack-1"` |
| `MINIO_SITE_REGION` | Region, e.g. `"us-west-1"` |
| `MINIO_SITE_COMMENT` | Optional comment |

## Networking & Domain

| Variable | Description |
|----------|-------------|
| `MINIO_DOMAIN` | FQDN for virtual-host-style requests (e.g. `minio.example.net` enables `bucket.minio.example.net`) |
| `MINIO_OPTS` | CLI parameters appended to `minio server` (for systemd setups) |
| `MINIO_CONFIG_ENV_FILE` | Path to environment file for `mc admin service restart` reloads |

## Console

| Variable | Description |
|----------|-------------|
| `MINIO_BROWSER` | Set to `off` to disable web console |
| `MINIO_BROWSER_REDIRECT_URL` | Public URL for console redirect (when behind proxy) |

## Scanner & Performance

| Variable | Description |
|----------|-------------|
| `MINIO_SCANNER_SPEED` | Scanner throttle: `fastest`, `fast`, `default`, `slow`, `slowest` |
| `MINIO_ILM_EXPIRY_WORKERS` | Workers for ILM expiration (default: half of CPU cores) |

## Storage Class (Erasure Coding)

| Variable | Description |
|----------|-------------|
| `MINIO_STORAGE_CLASS_STANDARD` | Parity for standard class, e.g. `"EC:4"` |
| `MINIO_STORAGE_CLASS_RRS` | Parity for reduced redundancy, e.g. `"EC:2"` |

## Container-Specific

| Variable | Description |
|----------|-------------|
| `MINIO_USERNAME` | Run as this user inside container |
| `MINIO_GROUPNAME` | Run as this group inside container |
| `MINIO_UID` | Numeric UID for container user |
| `MINIO_GID` | Numeric GID for container user |
