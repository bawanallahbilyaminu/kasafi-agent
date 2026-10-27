#!/usr/bin/env bash
# Read-only VPS discovery before deploying Kasafi. Installs, edits and restarts nothing.
# Run from your machine:  ssh <user>@<server> 'bash -s' < deploy/discover.sh
# Prints no passwords: from mailcow.conf it shows only port, bind and certificate settings.

section() { printf '\n== %s\n' "$1"; }

section "host"
hostname; . /etc/os-release 2>/dev/null && echo "$PRETTY_NAME"; uptime -p

section "resources"
df -h / | tail -1
free -h | sed -n 2p
nproc

section "docker"
docker --version 2>&1
docker compose version 2>&1
sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}' 2>&1

section "listening ports (80, 443, 8000-8099, 8443)"
sudo ss -tlnp 2>/dev/null | awk 'NR==1 || /:(80|443|80[0-9][0-9]|8443) /'

section "is 127.0.0.1:8010 free?"
if sudo ss -tln | grep -qE '[:.]8010 '; then echo "8010 IN USE"; else echo "8010 free"; fi

section "web servers"
for s in nginx apache2 caddy traefik; do printf '%-8s %s\n' "$s" "$(systemctl is-active "$s" 2>/dev/null)"; done

section "CloudPanel"
command -v clpctl >/dev/null && echo "clpctl present" || echo "clpctl not found"
sudo ls /etc/nginx/sites-enabled 2>/dev/null

section "mailcow (port and certificate settings only)"
M=$(sudo docker inspect -f '{{index .Config.Labels "com.docker.compose.project.working_dir"}}' \
      "$(sudo docker ps -qf name=nginx-mailcow | head -1)" 2>/dev/null)
echo "mailcow dir: ${M:-not found}"
[ -n "$M" ] && sudo grep -E '^(HTTP_PORT|HTTPS_PORT|HTTP_BIND|HTTPS_BIND|SKIP_LETS_ENCRYPT|ADDITIONAL_SAN|MAILCOW_HOSTNAME)=' "$M/mailcow.conf"

section "existing /opt/kasafi?"
ls -ld /opt/kasafi 2>/dev/null || echo "not present"

section "DNS for kasafi-api.halalnumeriq.com.ng"
getent hosts kasafi-api.halalnumeriq.com.ng || echo "not resolving yet"
echo "server's public IPv4: $(curl -s -4 --max-time 5 https://ifconfig.me || echo unknown)"
