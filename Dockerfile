###########
# BUILDER #
###########

# Pull base image
FROM python:3.8-slim-buster as builder

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    # Dependencies for building Python packages and psycopg2
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    # Final clean up to keep the image size down
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY Pipfile .
COPY Pipfile.lock .
RUN pip install --upgrade pip \
    && pip install pipenv \
    && pipenv lock -r > requirements.txt \
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
FROM python:3.8-slim-buster

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    # Dependencies for building Python packages and psycopg2
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    # Final clean up to keep the image size down
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache /wheels/*

# Copy the project
COPY . .