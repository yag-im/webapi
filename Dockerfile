# syntax=docker/dockerfile:1
FROM python:3.11-bookworm

ARG DEBIAN_FRONTEND=noninteractive

ARG APP_HOME_DIR=/opt/yag/yagsvc

RUN apt update \
    && apt install -y --no-install-recommends \
        gettext-base \
    && rm -rf /var/lib/apt/lists/*

COPY dist/*.whl /tmp/

RUN pip install --upgrade pip \
    && pip install /tmp/*.whl \
    && opentelemetry-bootstrap -a install \
    && rm -rf /tmp/*.whl

# bin folder contains:
#     cmd.sh: runs gunicorn
#     start.sh: handles graceful shutdown (wraps cmd.sh)
COPY runtime/bin ${APP_HOME_DIR}/bin

# conf folder contains:
#     gunicorn.config.py: needed for OTEL post-fork tracing purposes
COPY runtime/conf ${APP_HOME_DIR}/conf

ENV APP_HOME_DIR=${APP_HOME_DIR}

CMD $APP_HOME_DIR/bin/start.sh
