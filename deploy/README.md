# Deploying Kasafi API to the VPS

Goal: a fixed webhook URL, `https://kasafi-api.halalnumeriq.com.ng/webhook`, on a VPS that also runs mailcow and other
Docker apps. **Do not touch other services.** Kasafi runs as its own compose project (`kasafi-agent`), on its own
network and in `/opt/kasafi-agent`; these unique names avoid clashing with existing containers. It listens only on
`127.0.0.1:${KASAFI_PORT}` (default 8010). Public HTTPS comes from the host's **existing** reverse
proxy, which gets one new site entry. No server IPs, secrets or phone numbers go in this repo.

## 0. DNS

Add an `A` record: `kasafi-api.halalnumeriq.com.ng` pointing to the VPS's public IP (plus `AAAA` if the VPS has IPv6).

The domain's DNS is hosted at Cloudoon, not Cloudflare. If it ever moves to Cloudflare, keep this record
**DNS only** (grey cloud) until the Let's Encrypt certificate has been issued.

## 1. Discovery (read-only)

```sh
ssh <user>@<server> 'bash -s' < deploy/discover.sh
```

This shows what owns ports 80/443 (CloudPanel's nginx), mailcow's port and certificate settings, and whether 8010 is free.

## 2. Install (only touches /opt/kasafi-agent)

On the server:

```sh
git clone https://github.com/bawanallahbilyaminu/kasafi-agent.git /opt/kasafi-agent
```

From your machine, in the repo folder, copy **only** the keys the API needs. Nothing is printed, and the file is
created with mode 600:

```sh
grep -E '^(META_API_KEY|BASETEN_API_KEY|WHATSAPP_[A-Z_]+)=' .env \
  | ssh root@<server> 'umask 077; cat > /opt/kasafi-agent/deploy/.env && echo KASAFI_PORT=8010 >> /opt/kasafi-agent/deploy/.env'
```

On the server:

```sh
cd /opt/kasafi-agent/deploy && docker compose up -d --build
docker compose ps                        # kasafi-agent-api ... (healthy)
curl -s http://127.0.0.1:8010/health     # {"status":"ok"}
```

## 3. HTTPS: a CloudPanel Reverse Proxy site

CloudPanel owns the nginx vhosts, so **don't hand-edit nginx config**. Add one site in the CloudPanel UI:

1. Open CloudPanel (`https://<server>:8443`) and log in.
2. **Sites → + Add Site → Create a Reverse Proxy**.
3. **Domain Name:** `kasafi-api.halalnumeriq.com.ng`.
   **Reverse Proxy Url:** `http://127.0.0.1:8010`.
   **Site User:** `kasafi-api`, with a strong generated password (CloudPanel requires one; it isn't used by the app).
4. Click **Create**.
5. Open the new site → **SSL/TLS → Actions → New Let's Encrypt Certificate → Create and Install**. This needs the `A`
   record to already point at the server, with port 80 reachable.
6. Optional: on the site's **Vhost** tab, check that the `location /` block proxies to `http://127.0.0.1:8010`.
   Leave the rest of CloudPanel's template alone.

This adds one vhost and leaves the other sites and mailcow untouched. To remove it later: **Sites →** the site's
**⋯ → Delete**.

## 4. Verify, then switch Meta

```sh
curl -s https://kasafi-api.halalnumeriq.com.ng/health
```

Then App Dashboard → WhatsApp → Configuration → Webhook → Edit: set the Callback URL to
`https://kasafi-api.halalnumeriq.com.ng/webhook`, keep the same verify token, and click **Verify and save**.

## One-command deploy (from your laptop)

### SSH alias (one-time)

Add this to `C:\Users\<you>\.ssh\config` (that's `~/.ssh/config`; Git Bash and Windows OpenSSH share it). The IP lives
only there, never in this repo:

```
Host vps
    HostName <server IP>
    User root
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
```

Test it with `ssh vps true`. To avoid typing the key passphrase on every deploy, run the Windows ssh-agent once
(PowerShell as admin: `Set-Service ssh-agent -StartupType Automatic; Start-Service ssh-agent`, then `ssh-add`).
`deploy.sh` uses Windows OpenSSH when it's available, so it picks up the agent. For a different alias, set
`KASAFI_SSH_HOST=myalias`.

### Commands

| Git Bash | PowerShell | What it does |
|---|---|---|
| `deploy/deploy.sh` | `.\deploy\deploy.ps1` | Deploy the pushed `main` |
| `deploy/deploy.sh --rollback` | `.\deploy\deploy.ps1 --rollback` | Go back one release |
| `deploy/deploy.sh --sync-env` | `.\deploy\deploy.ps1 --sync-env` | Update the server's `deploy/.env` from your local `.env` |

### What a deploy does

1. **On your laptop:** it refuses if you're not on `main`, the working tree has uncommitted changes, or local `main`
   differs from `origin/main` (not pushed or not pulled). Then it runs `uv run pytest`.
2. **On the server** (`deploy/remote.sh`, sent over ssh and run as root, with a lock so two deploys can't overlap):
   - records the current commit
   - runs `git pull --ff-only` on `main` and checks that the result equals the commit your laptop expects
   - builds the `kasafi-agent-api` image stamped with that commit (`/version` reports it)
   - runs `alembic upgrade head` **only** if `alembic.ini` exists and `DATABASE_URL` is set in `deploy/.env`.
     When migrations are added, the Dockerfile must also copy `alembic.ini` and `migrations/`.
   - runs `docker compose up -d` for the **kasafi-agent project only**
   - waits up to 90 s for `127.0.0.1:8010/health` to answer **and** `/version` to report the new commit
3. **If that fails:** it checks out the previous commit, rebuilds, waits for health, and exits with code 2 and a red
   "rolled back" message naming the failing commit. If the rollback also fails, it exits with code 1 and says so.
4. **If it succeeds:** it adds the commit to `/var/lib/kasafi-agent/releases`, appends a line to
   `/var/log/kasafi-agent/deploy.log`, and keeps only the newest 3 `kasafi-agent-api:<commit>` images. It removes
   only dangling images labelled `org.kasafi.app=kasafi-agent-api`, never anything else. Back on your laptop it
   checks `https://kasafi-api.halalnumeriq.com.ng/health` and `/version` and prints the live commit.

It never touches `deploy/.env` during a normal deploy, never uses `--remove-orphans`, and never prunes other
containers or images. The server runs mailcow and other apps.

### `--rollback`

Rolls back to the previous release in `/var/lib/kasafi-agent/releases` and checks its health. Each run goes back one
more release. The next normal deploy returns to the latest `main`.

### `--sync-env`

Uploads **only** the allowed keys from your local `.env` (see `ALLOWED_KEYS` in `deploy.sh`: Meta, Baseten, Serper
and WhatsApp), with `\r` stripped, using `umask 077`. Values are never printed. `KASAFI_PORT` is kept from the
server's file, the old file is saved as `deploy/.env.bak`, and the container is restarted. If it's unhealthy with
the new values, the old `.env` is restored automatically. `DATABASE_URL` is deliberately left out until the
production database exists, because the local one points at dev Postgres.

The first time, run a normal deploy **before** `--sync-env`. The health check needs a container built by
`deploy.sh` so that `/version` matches.

## Remove completely

```sh
cd /opt/kasafi-agent/deploy && docker compose down    # stops only the kasafi-agent project
# then delete the kasafi-api site in CloudPanel (Sites → ⋯ → Delete)
```
