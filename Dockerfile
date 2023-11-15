#####################
# 1 STAGE – BUILDER #
#####################

FROM python:3.12-slim as builder

ENV APP_HOME=/code

WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev libpoppler-cpp-dev curl && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - --version 1.7.0 && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry config virtualenvs.create false && \
    poetry install --with dev && \
    playwright install firefox

###################
# 2 STAGE – FINAL #
###################

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/code

WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 libpoppler-cpp0v5 firefox-esr && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/ /usr/local/
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

COPY . .
