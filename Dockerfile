####################
# 1 STAGE – PYTHON #
####################

# Python dependencies builder
FROM python:3.12-alpine as python-builder

ENV APP_HOME=/code
WORKDIR $APP_HOME

# Install system dependencies for Python packages
RUN apk update && \
    apk add --no-cache --virtual .build-deps build-base libpq-dev poppler-dev curl

# Install project dependencies
ARG POETRY_VERSION=1.7.0
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry config virtualenvs.create false && \
    poetry install --with dev

# Remove build dependencies to reduce cached layer size
RUN apk del .build-deps

##################
# 2 STAGE – RUST #
##################

# Rust-based geckodriver builder
FROM rust:1.73-alpine as rust-builder

# Compile geckodriver
ARG GECKODRIVER_VERSION=0.33.0
RUN apk add --no-cache --virtual .build-deps musl-dev curl && \
    curl -o geckodriver.tar.gz -L https://github.com/mozilla/geckodriver/archive/refs/tags/v${GECKODRIVER_VERSION}.tar.gz && \
    tar -xzf geckodriver.tar.gz && \
    cd geckodriver-${GECKODRIVER_VERSION} && \
    cargo build --release && \
    mv target/release/geckodriver /usr/local/bin/geckodriver && \
    rm -rf /var/cache/apk/* /geckodriver-${GECKODRIVER_VERSION} geckodriver.tar.gz && \
    apk del .build-deps

###################
# 3 STAGE – FINAL #
###################

# Pull base image for final stage
FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/code

WORKDIR $APP_HOME

# Install runtime system dependencies
RUN apk update && \
    apk add --no-cache libpq poppler-utils firefox-esr && \
    rm -rf /var/cache/apk/*

# Copy Python project dependencies
COPY --from=python-builder /usr/local/ /usr/local/

# Copy geckodriver
COPY --from=rust-builder /usr/local/bin/geckodriver /usr/local/bin/geckodriver
RUN chmod +x /usr/local/bin/geckodriver

# Copy the project
COPY . .
