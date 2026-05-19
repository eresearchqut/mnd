# Builder stage
FROM python:3.13 AS builder

ENV PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
  # Base
  gettext \
  libpq5 \
  media-types \
  nodejs \
  unixodbc \
  # Builder
  build-essential \
  git \
  gzip \
  libpq-dev \
  libssl-dev \
  libyaml-dev \
  unixodbc-dev \
  zlib1g-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# Copy rdrf (trrf) dependency files first for layer caching
COPY rdrf/pyproject.toml rdrf/uv.lock ./rdrf/
COPY rdrf/clients ./rdrf/clients

# Sync production dependencies only
ENV UV_LINK_MODE=copy
WORKDIR /app/rdrf
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Runtime stage
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONPATH="/app/rdrf/rdrf/:/app/mnd/"
ENV DJANGO_SETTINGS_MODULE=mnd.settings

ENV PROJECT_NAME=mnd
ENV PROJECT_SOURCE=https://github.com/eresearchqut/mnd.git
ENV DEPLOYMENT=prod
ENV PRODUCTION=1
ENV DEBUG=0
ENV STATIC_ROOT=/data/static
ENV WRITABLE_DIRECTORY=/data/scratch
ENV MEDIA_ROOT=/data/static/media
ENV LOG_DIRECTORY=/data/log
ENV LOCALE_PATHS=/data/translations/locale

RUN mkdir /app

RUN addgroup --gid 1000 django \
  && adduser --disabled-password --home /data --no-create-home --system -q --uid 1000 --ingroup django django \
  && mkdir /data \
  && chown django:django /data \
  && chown django:django /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  # Base
  git \
  gettext \
  libpq5 \
  media-types \
  nodejs \
  unixodbc \
  ssl-cert \
  libmagic1 \
  pdftk \
  curl \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# Copy venv from builder
COPY --from=builder /app/rdrf/.venv /app/rdrf/.venv

# Copy rdrf dependency files
COPY rdrf/pyproject.toml rdrf/uv.lock ./rdrf/
COPY rdrf/clients ./rdrf/clients

# Finalize dependency install (production only)
ENV UV_LINK_MODE=copy
WORKDIR /app/rdrf
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Add venv to PATH
ENV PATH="/app/rdrf/.venv/bin:$PATH"

# The generated snakeoil cert is valid for 10 years, but if you need to
# re-generate it you can use:
# RUN make-ssl-cert generate-default-snakeoil --force-overwrite

RUN chgrp -R django /etc/ssl/private/ \
  && chmod g+r /etc/ssl/private/ssl-cert-snakeoil.key

COPY docker/dev/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

VOLUME ["/data"]
ENV HOME=/data

EXPOSE 9000

COPY --chown=django:django . /app

USER django
WORKDIR /data

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uwsgi"]
