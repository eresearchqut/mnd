# FROM muccg/rdrf-builder
FROM python:3.8.0 as builder

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
  # TODO check if requirements are needed
  # Base
  gettext \
  libpcre3 \
  libpq5 \
  mime-support \
  nodejs \
  unixodbc \
  # Builder
  build-essential \
  gzip \
  libpcre3-dev \
  libpq-dev \
  libssl-dev \
  libyaml-dev \
  unixodbc-dev \
  zlib1g-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /requirements/rdrf
WORKDIR /requirements

# RUN env | sort

# Add our python deps in multiple docker layers
# hgvs was failing due to lack of nose, hence the order

COPY requirements/* ./
COPY rdrf/requirements/* ./rdrf/

RUN    pip install -r rdrf/requirements.txt \
    && pip install -r rdrf/dev-requirements.txt \
    && pip install -r rdrf/test-requirements.txt \
    && pip install -r requirements.txt \
    && pip install -r dev-requirements.txt \
    && pip install -r test-requirements.txt

VOLUME ["/data"]

FROM python:3.8.0-slim

ENV PYTHONPATH="/app/rdrf/rdrf/:/app/mnd/"
ENV DJANGO_SETTINGS_MODULE mnd.settings
ENV STATIC_ROOT="/data/static"
ENV WRITABLE_DIRECTORY="/data/scratch"
ENV LOCALE_PATHS="/data/translations/locale"
ENV LOG_DIRECTORY="/data/log"
ENV MEDIA_ROOT="/data/static/media"

# RUN apt-get update && apt-get install -y --no-install-recommends \
#    libxml2 \
#   && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# This is done in order to workaround problems installing openjdk as reported here:
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=863199
RUN mkdir -p /usr/share/man/man1

RUN apt-get update && apt-get install -y --no-install-recommends \
  # Base
  # TODO check if requirements are needed
  gettext \
  libpcre3 \
  libpq5 \
  mime-support \
  nodejs \
  unixodbc \
  libmagic1 \
  pdftk \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /requirements/rdrf/
WORKDIR /requirements

COPY --from=builder /root/.cache /root/.cache
COPY --from=builder /requirements/ .

RUN    pip install -r rdrf/requirements.txt \
    && pip install -r rdrf/dev-requirements.txt \
    && pip install -r rdrf/test-requirements.txt \
    && pip install -r requirements.txt \
    && pip install -r dev-requirements.txt \
    && pip install -r test-requirements.txt

RUN rm -Rf /root/.cache

COPY docker/dev/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

VOLUME ["/app", "/data"]

ENV HOME /data
WORKDIR /data

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["runserver_plus"]
