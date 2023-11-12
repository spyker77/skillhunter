#####################
# 1 STAGE – BUILDER #
#####################

FROM python:3.12-slim as builder

ENV APP_HOME=/code

WORKDIR $APP_HOME

ARG GECKODRIVER_VERSION=0.33.0
ARG POETRY_VERSION=1.7.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev libpoppler-cpp-dev curl && \
    curl -sL https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz | tar -xz -C /usr/local/bin && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry config virtualenvs.create false && \
    poetry install --with dev

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
RUN chmod +x /usr/local/bin/geckodriver

COPY . .
