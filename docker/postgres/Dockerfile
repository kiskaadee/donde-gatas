FROM postgis/postgis:17-3.5

# Install build dependencies and pgvector
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-17-pgvector || \
        (apt-get install -y --no-install-recommends git build-essential postgresql-server-dev-17 && \
         cd /tmp && \
         git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git && \
         cd pgvector && \
         make && \
         make install && \
         apt-get remove -y git build-essential postgresql-server-dev-17 && \
         apt-get autoremove -y && \
         rm -rf /tmp/pgvector) && \
    rm -rf /var/lib/apt/lists/*

COPY docker/postgres/init-extensions.sql /docker-entrypoint-initdb.d/01-init-extensions.sql
