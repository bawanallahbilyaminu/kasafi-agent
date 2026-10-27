# Deploying Kasafi API to the VPS

Goal: a fixed webhook URL, `https://kasafi-api.halalnumeriq.com.ng/webhook`, on a VPS that also runs mailcow and other
Docker apps. **Do not touch other services.** Kasafi runs as its own compose project (`kasafi`), on its own network,
and listens only on `127.0.0.1:${KASAFI_PORT}` (default 8010). Public HTTPS comes from the host's **existing** reverse
proxy, which gets one new site entry. No server IPs, secrets or phone numbers go in this repo.

## 0. DNS

Add an `A` record: `kasafi-api.halalnumeriq.com.ng` pointing to the VPS's public IP (plus `AAAA` if the VPS has IPv6).

## 1. Discovery (read-only)

Find what already owns ports 80/443, and pick a free local port for Kasafi. See the command list in the session
notes, or run:

```sh
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
sudo ss -tlnp | grep -E ':(80|443|80[0-9]{2})\b'
systemctl is-active nginx caddy apache2 traefik 2>/dev/null
```

## 2. Install (only touches /opt/kasafi)

```sh
sudo git clone https://github.com/bawanallahbilyaminu/kasafi-agent.git /opt/kasafi
cd /opt/kasafi/deploy
sudo cp ../.env.example .env && sudo chmod 600 .env   # then fill in the values
echo "KASAFI_PORT=8010" | sudo tee -a .env            # a port confirmed free in step 1
sudo docker compose up -d --build
curl -s http://127.0.0.1:8010/health                  # {"status":"ok"}
```

## 3. HTTPS reverse proxy

Add **one** new site for `kasafi-api.halalnumeriq.com.ng` that proxies to `http://127.0.0.1:8010`, using whichever
proxy step 1 found. The exact config is decided after discovery. Don't edit mailcow's own config; if mailcow's
nginx is the thing listening on 80/443, decide together before changing anything.

## 4. Verify, then switch Meta

```sh
curl -s https://kasafi-api.halalnumeriq.com.ng/health
```

Then App Dashboard → WhatsApp → Configuration → Webhook → Edit: set the Callback URL to
`https://kasafi-api.halalnumeriq.com.ng/webhook`, keep the same verify token, and click **Verify and save**.

## Update

```sh
cd /opt/kasafi && sudo git pull && cd deploy && sudo docker compose up -d --build
```

## Rollback / remove

```sh
cd /opt/kasafi/deploy && sudo docker compose down    # stops only the kasafi project
# then remove the one reverse-proxy site added in step 3 and reload that proxy
```
