# Pull base image
FROM python:3.9.0-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY Pipfile Pipfile.lock /code/
RUN apt-get update \
    # Dependencies for building Python packages
    && apt-get install -y build-essential \
    # psycopg2 dependencies
    && apt-get install -y libpq-dev \
    # Project dependencies
    && pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install --system \
    # Final clean up to keep the image size down
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /code/