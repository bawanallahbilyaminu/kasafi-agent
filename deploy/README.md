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

## Update

```sh
cd /opt/kasafi-agent && git pull && cd deploy && docker compose up -d --build
```

## Rollback / remove

```sh
cd /opt/kasafi-agent/deploy && docker compose down    # stops only the kasafi-agent project
# then delete the kasafi-api site in CloudPanel (Sites → ⋯ → Delete)
```
