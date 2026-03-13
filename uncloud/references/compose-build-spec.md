# Compose Build Specification

Reference: https://github.com/compose-spec/compose-spec/blob/main/build.md

The `build:` section in a Compose file defines how to build a service image from source.

## Basic Syntax

Two forms are supported:

```yaml
# String: path to build context
services:
  web:
    build: .

# Object: full configuration
services:
  web:
    build:
      context: ./app
      dockerfile: Dockerfile.prod
```

## build + image Interaction

When both `build:` and `image:` are present, `pull_policy` governs behavior.
If `pull_policy` is unset, Compose tries to pull the image first, then falls back to building.

```yaml
services:
  web:
    build: .
    image: myregistry/myapp:latest   # Used for tagging/pushing
    pull_policy: build               # Always build from source
```

## Core Fields

### context
Path to the Dockerfile directory, or a Git repository URL. Defaults to project directory (`.`).

```yaml
build:
  context: ./backend
  # or a git URL:
  context: https://github.com/org/repo.git#branch:subdir
```

### dockerfile / dockerfile_inline
Point to an alternate Dockerfile, or embed one inline. Mutually exclusive.

```yaml
build:
  context: .
  dockerfile: docker/Dockerfile.prod

# or inline:
build:
  dockerfile_inline: |
    FROM python:3.11
    COPY . /app
    RUN pip install -r requirements.txt
```

### args
Build arguments passed to Dockerfile `ARG` instructions.

```yaml
build:
  context: .
  args:
    RAILS_ENV: production
    NODE_VERSION: "20"
    # Value from shell env:
    SECRET_KEY: ${SECRET_KEY}
```

### target
Select a specific stage in a multi-stage Dockerfile.

```yaml
build:
  context: .
  target: production
```

### tags
Additional image tags beyond the service's `image` property.

```yaml
build:
  context: .
  tags:
    - myapp:latest
    - myapp:v1.2.3
    - registry.example.com/myapp:stable
```

### labels
Metadata added to the resulting image.

```yaml
build:
  context: .
  labels:
    com.example.version: "1.0"
    com.example.commit: ${GIT_SHA}
```

## Advanced Fields

### additional_contexts
Named build contexts (Compose v2.17.0+). Supports paths, Git URLs, and references to other services via `service:` prefix.

```yaml
build:
  context: .
  additional_contexts:
    assets: ./frontend/dist
    base: docker-image://mybase:latest
    shared: service:shared-lib
```

### cache_from / cache_to
Optimize builds by importing/exporting layer cache.

```yaml
build:
  context: .
  cache_from:
    - type=registry,ref=myapp:cache
    - type=local,src=/tmp/build-cache
  cache_to:
    - type=registry,ref=myapp:cache,mode=max
    - type=local,dest=/tmp/build-cache
```

### platforms
Target architectures to build for. Service platform is automatically included unless explicitly omitted.

```yaml
build:
  context: .
  platforms:
    - linux/amd64
    - linux/arm64
```

### network
Network mode for `RUN` instructions during build.

```yaml
build:
  context: .
  network: host      # Use host network
  # network: none    # No network access
  # network: custom  # Named network
```

### pull / no_cache

```yaml
build:
  context: .
  pull: true       # Always re-pull base images (ignore local cache)
  no_cache: true   # Disable build cache entirely (v2.4.0+)
```

## Security

### secrets
Grant build-time access to sensitive data (not baked into image layers).

```yaml
secrets:
  db_password:
    environment: DB_PASSWORD

services:
  web:
    build:
      context: .
      secrets:
        - db_password                    # Short syntax

        # Long syntax:
        - source: db_password
          target: /run/secrets/db_pass
          uid: "1000"
          gid: "1000"
          mode: 0400
```

### ssh
Enable SSH agent forwarding during build.

```yaml
build:
  context: .
  ssh:
    - default          # Forward default SSH agent
    - mykey=~/.ssh/id_rsa  # Specific key
```

### privileged
Build with elevated privileges (v2.15.0+).

```yaml
build:
  context: .
  privileged: true
```

### entitlements
Grant extra privileged entitlements during build (v2.27.0+).

```yaml
build:
  context: .
  entitlements:
    - network.host
    - security.insecure
```

## Performance & Config

### shm_size
Shared memory size for build containers.

```yaml
build:
  context: .
  shm_size: 128m   # or in bytes: 134217728
```

### ulimits
Override ulimits during build (v2.23.1+).

```yaml
build:
  context: .
  ulimits:
    nofile:
      soft: 1024
      hard: 1024
```

### extra_hosts
Add hostname → IP mappings during build.

```yaml
build:
  context: .
  extra_hosts:
    - "myhost=192.168.1.10"
    - "otherhost:10.0.0.5"
```

### isolation
Platform-dependent container isolation technology.

```yaml
build:
  context: .
  isolation: hyperv   # Windows only
```

## Attestations (v2.39.0+)

### provenance
Add SLSA provenance attestations to published images.

```yaml
build:
  context: .
  provenance: true          # Enable with defaults
  provenance: mode=max      # Full provenance
```

### sbom
Generate a Software Bill of Materials attestation.

```yaml
build:
  context: .
  sbom: true
  sbom: generator=docker/scout-sbom-indexer:latest   # Custom generator
```

## Full Example

```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
      target: production
      args:
        RAILS_ENV: production
        GIT_SHA: ${GIT_SHA:-local}
      platforms:
        - linux/amd64
        - linux/arm64
      cache_from:
        - type=registry,ref=myapp:buildcache
      cache_to:
        - type=registry,ref=myapp:buildcache,mode=max
      secrets:
        - source: rails_master_key
          target: /run/secrets/rails_master_key
      labels:
        com.example.version: "1.0"
      tags:
        - myregistry/myapp:latest
    image: myregistry/myapp:latest

secrets:
  rails_master_key:
    environment: RAILS_MASTER_KEY
```
