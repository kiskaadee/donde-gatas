FROM pgvector/pgvector:pg17

# Install official PostGIS 3 for PostgreSQL 17
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-17-postgis-3 \
        postgresql-17-postgis-3-scripts && \
    rm -rf /var/lib/apt/lists/*

COPY docker/postgres/init-extensions.sql /docker-entrypoint-initdb.d/01-init-extensions.sql
