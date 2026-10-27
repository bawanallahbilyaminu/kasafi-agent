# Kasafi API: FastAPI webhook server.
FROM python:3.12-slim-bookworm

# ffmpeg converts WhatsApp OGG/Opus voice notes to WAV (app/providers/audio.py).
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app
# Migrations run on deploy (deploy/remote.sh) once DATABASE_URL is set on the server.
COPY alembic.ini ./
COPY migrations ./migrations

# Late in the file so a new commit doesn't invalidate the dependency layers.
ARG KASAFI_COMMIT=unknown
ENV KASAFI_COMMIT=$KASAFI_COMMIT
LABEL org.kasafi.app=kasafi-agent-api org.kasafi.commit=$KASAFI_COMMIT

RUN useradd --system --uid 10001 kasafi && mkdir -p /data && chown kasafi /data
USER kasafi

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"

# --proxy-headers so client IPs come from the reverse proxy's X-Forwarded-For.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
