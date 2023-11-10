#####################
# 1 STAGE – BUILDER #
#####################

# Python dependencies builder
FROM python:3.12-slim as builder

ENV APP_HOME=/code
WORKDIR $APP_HOME

# Install system dependencies for Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev libpoppler-cpp-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Install project dependencies
ARG POETRY_VERSION=1.7.0
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry config virtualenvs.create false && \
    poetry install --with dev

###################
# 2 STAGE – FINAL #
###################

# Pull base image for final stage
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/code

WORKDIR $APP_HOME

# Install runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 libpoppler-cpp0v5 firefox-esr && \
    rm -rf /var/lib/apt/lists/*

# Copy Python project dependencies
COPY --from=builder /usr/local/ /usr/local/

# Copy the project
COPY . .
