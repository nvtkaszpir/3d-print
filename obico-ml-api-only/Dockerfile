# hadolint ignore=DL3008
ARG BASE_IMAGE=docker.io/library/python:3.12.6-slim-bookworm
ARG BASE_DIGEST=sha256:15bad989b293be1dd5eb26a87ecacadaee1559f98e29f02bf6d00c8d86129f39
FROM ${BASE_IMAGE}@${BASE_DIGEST}

ARG BASE_IMAGE
ARG BASE_DIGEST
ARG GIT_SOURCE
ARG GIT_COMMIT
ARG AUTHORS=kaszpir@gmail.com
ARG URL=https://nvtkaszpir.github.io/3d-print

WORKDIR /app
COPY requirements-render.txt /app
COPY README.md /app
COPY info.html /app
COPY draw_detections.py /app
COPY server.py /app

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        fonts-freefont-ttf \
    && pip3 install --upgrade --no-cache-dir pip==24.2 \
    && pip3 install --no-cache-dir -r requirements-render.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN useradd -ms /bin/bash app -u 1000 && \
    chown -R app /app
USER app
EXPOSE 3334

ENV PYTHONDONTWRITEBYTECODE=1

RUN gunicorn --bind 0.0.0.0:3334 --workers 1 server --check-config --preload
CMD ["gunicorn", "--bind", "0.0.0.0:3334", "--workers", "1", "server"]

HEALTHCHECK --interval=10s --timeout=5s \
  CMD  curl --fail http://0.0.0.0:3334/ready || exit 1

LABEL org.opencontainers.image.base.name="${BASE_IMAGE}"
LABEL org.opencontainers.image.base.digest="${BASE_DIGEST}"
LABEL org.opencontainers.image.description="Linux python app to fetch images from remote server and call Obico ML Api to render detections of the failed prints."
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
LABEL org.opencontainers.image.source="${GIT_SOURCE}"
LABEL org.opencontainers.image.url="${URL}"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.authors="${AUTHORS}"
