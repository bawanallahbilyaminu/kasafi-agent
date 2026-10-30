# Postgres 17 + pgvector (the image Kasafi already runs) + PostGIS 3, for the geo foundation
# (docs/hazard-and-services.md section 2). Same major version and data directory: an existing volume is kept.
FROM pgvector/pgvector:pg17
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-17-postgis-3 \
 && rm -rf /var/lib/apt/lists/*
