###########
# BUILDER #
###########

# Pull base image
FROM python:3.9-slim-buster as builder

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev libpoppler-cpp-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY pyproject.toml .
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry add flashtext pdftotext \
    && poetry export -f requirements.txt --output requirements.txt \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r requirements.txt

# Copy the project and lint
COPY . .
RUN pip install flake9 black isort \
    && flake8 . \
    && black . \
    && isort .


#########
# FINAL #
#########

# Pull base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev libpoppler-cpp-dev pkg-config \
    # Package required for converting uploaded resumes to pdf >>> resume_analyzer.analyzer.convert_to
    # libreoffice \
    firefox-esr wget tar \
    && wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz \
    && tar -x geckodriver -zf geckodriver-v0.29.0-linux64.tar.gz -O > /usr/bin/geckodriver \
    && chmod +x /usr/bin/geckodriver \
    && rm geckodriver-v0.29.0-linux64.tar.gz \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies from wheels
COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache /wheels/*

# Copy the project
COPY . .