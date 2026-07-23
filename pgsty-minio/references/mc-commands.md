# mc (MinIO Client) Command Reference

The `pgsty/minio` server image bundles `mcli` with an `mc` symlink from `pgsty/mc`.
A `local` alias pointing at `http://localhost:9000` is auto-configured.

## Alias Management

```bash
mc alias set <name> <endpoint> <access-key> <secret-key>
mc alias ls
mc alias rm <name>
mc alias export <name>     # export as JSON
mc alias import <file>     # import from JSON
```

## Bucket Operations

```bash
mc mb <alias>/<bucket>                 # create bucket
mc rb <alias>/<bucket>                 # remove empty bucket
mc rb --force <alias>/<bucket>         # remove bucket + all objects (destructive!)
mc ls <alias>/                         # list buckets
mc ls <alias>/<bucket>/                # list objects
mc ls --recursive <alias>/<bucket>/    # recursive listing
mc tree <alias>/<bucket>/              # tree view
mc du <alias>/<bucket>/                # disk usage
mc stat <alias>/<bucket>               # bucket metadata
```

## Object Operations

```bash
mc cp <source> <dest>                  # copy (local<->remote or remote<->remote)
mc mv <source> <dest>                  # move
mc rm <alias>/<bucket>/<object>        # remove object
mc rm --recursive <alias>/<bucket>/    # remove all objects (destructive!)
mc cat <alias>/<bucket>/<object>       # print object to stdout
mc head <alias>/<bucket>/<object>      # first N lines
mc get <alias>/<bucket>/<object> <local-path>  # download
mc put <local-path> <alias>/<bucket>/  # upload
mc pipe <alias>/<bucket>/<object>      # stream stdin to object
```

## Sync / Mirror

```bash
mc mirror <source> <dest>              # one-way sync (like rsync)
mc mirror --watch <source> <dest>      # continuous sync
mc mirror --remove <source> <dest>     # sync + delete orphans at dest
mc diff <alias1>/<bucket> <alias2>/<bucket>  # show differences
```

## Anonymous Access (Public Buckets)

```bash
mc anonymous set download <alias>/<bucket>   # public read-only
mc anonymous set upload <alias>/<bucket>     # public write-only
mc anonymous set public <alias>/<bucket>     # public read+write+list
mc anonymous set none <alias>/<bucket>       # remove public access
mc anonymous get <alias>/<bucket>            # check current policy
mc anonymous list <alias>/<bucket>           # list policy rules
```

## Presigned URLs

```bash
mc share download <alias>/<bucket>/<object>                  # 7-day default
mc share download --expire 24h <alias>/<bucket>/<object>     # custom expiry
mc share upload <alias>/<bucket>/<prefix>                    # presigned upload
mc share list download                                        # list active shares
mc share list upload
```

## Bucket Versioning

```bash
mc version enable <alias>/<bucket>
mc version info <alias>/<bucket>
mc version suspend <alias>/<bucket>
```

## Bucket Lifecycle (ILM)

```bash
mc ilm rule ls <alias>/<bucket>
mc ilm rule add <alias>/<bucket> --expire-days 90
mc ilm rule add <alias>/<bucket> --transition-days 30 --tier TIER-NAME
mc ilm rule rm <alias>/<bucket> --id <rule-id>
mc ilm tier ls <alias>
```

## Tags

```bash
mc tag set <alias>/<bucket>/<object> "key=value&key2=value2"
mc tag list <alias>/<bucket>/<object>
mc tag remove <alias>/<bucket>/<object>
```

## Find

```bash
mc find <alias>/<bucket>/ --name "*.zip"
mc find <alias>/<bucket>/ --larger 10MB
mc find <alias>/<bucket>/ --older-than 7d
mc find <alias>/<bucket>/ --name "*.tmp" --exec "mc rm {}"
```

## Events / Notifications

```bash
mc event add <alias>/<bucket> <arn> --event put,delete
mc event list <alias>/<bucket>
mc event remove <alias>/<bucket> <arn>
mc watch <alias>/<bucket>              # live event stream
```

## Admin Commands

```bash
mc admin info <alias>                  # server info (version, uptime, disks)
mc admin service restart <alias>       # restart server
mc admin service stop <alias>          # stop server
mc admin logs <alias>                  # stream server logs

# IAM
mc admin user add <alias> <user> <password>
mc admin user ls <alias>
mc admin user rm <alias> <user>
mc admin user enable <alias> <user>
mc admin user disable <alias> <user>
mc admin policy ls <alias>
mc admin policy attach <alias> <policy> --user <user>

# Health / diagnostics
mc ready <alias>                       # readiness probe (exit 0 = ready)
mc ping <alias>                        # liveness ping
mc admin config get <alias>            # dump server config
mc admin config set <alias> <key> <value>  # update server config
```

## Batch Jobs

```bash
mc batch generate <alias> replicate    # generate job template
mc batch start <alias> <job-file>      # submit batch job
mc batch list <alias>                  # list running jobs
mc batch status <alias> <job-id>       # check job status
mc batch cancel <alias> <job-id>       # cancel job
```
