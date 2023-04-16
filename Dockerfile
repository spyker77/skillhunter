###########
# BUILDER #
###########

# Pull base image
FROM python:3.11-slim-buster as builder

# Set working directory
ENV APP_HOME=/code
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev libpoppler-cpp-dev pkg-config curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    export PATH="$HOME/.cargo/bin:$PATH" && \
    curl -o v0.33.0.tar.gz -L https://github.com/mozilla/geckodriver/archive/refs/tags/v0.33.0.tar.gz && \
    tar -xzf v0.33.0.tar.gz && \
    cd geckodriver-0.33.0 && \
    cargo build --release && \
    mv target/release/geckodriver $APP_HOME/geckodriver && \
    cd $APP_HOME && \
    rm -rf /var/lib/apt/lists/* geckodriver-0.33.0 v0.33.0.tar.gz

# Install project dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry export --format requirements.txt --output requirements.txt --dev --without-hashes && \
    pip wheel --no-cache-dir --no-deps --wheel-dir $APP_HOME/wheels -r requirements.txt


#########
# FINAL #
#########

# Pull base image
FROM python:3.11-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/code

# Set working directory
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev libpoppler-cpp-dev pkg-config firefox-esr && \
    rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY --from=builder $APP_HOME/wheels /wheels
COPY --from=builder $APP_HOME/geckodriver /usr/bin/geckodriver
RUN pip install --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    chmod +x /usr/bin/geckodriver && \
    rm -rf /wheels

# Copy the project
COPY . .
