###########
# BUILDER #
###########

# Pull base image
FROM python:3.10-slim-buster as builder

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpoppler-cpp-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY poetry.lock .
COPY pyproject.toml .
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry export -f requirements.txt --output requirements.txt --dev \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r requirements.txt


#########
# FINAL #
#########

# Pull base image
FROM python:3.10-slim-buster

# Set working directory
ENV APP_HOME=/code
WORKDIR $APP_HOME

# Create the app user
RUN addgroup --system app \
    && adduser --system --group app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpoppler-cpp-dev \
    pkg-config \
    firefox-esr \
    wget \
    tar \
    # Package required for converting uploaded resumes to pdf >>> resume_analyzer.analyzer.convert_to
    # libreoffice \
    && wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \
    && tar -x geckodriver -zf geckodriver-v0.30.0-linux64.tar.gz -O > /usr/bin/geckodriver \
    && chmod +x /usr/bin/geckodriver \
    && rm geckodriver-v0.30.0-linux64.tar.gz \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies from wheels
COPY --from=builder $APP_HOME/wheels /wheels
COPY --from=builder $APP_HOME/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache /wheels/*

# Copy the project
COPY . .

# Chown all the files to the app user
RUN chown -R app:app $APP_HOME

# Change to the app user
USER app