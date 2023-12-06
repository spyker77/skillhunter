####################
# 1 STAGE – PYTHON #
####################

FROM python:3.12-slim as python-builder

WORKDIR /code

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - --version 1.7.1 && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry config virtualenvs.create false && \
    poetry install --with dev && \
    playwright install firefox

##################
# 2 STAGE – NODE #
##################

FROM node:21.2-slim as node-builder

WORKDIR /code

COPY package*.json postcss.config.js tailwind.config.js ./
COPY static/css/ static/css/
COPY templates/ templates/

RUN npm install && npm run build

###################
# 3 STAGE – FINAL #
###################

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/code

WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 firefox-esr && \
    rm -rf /var/lib/apt/lists/*

COPY --from=python-builder /usr/local/ /usr/local/
COPY --from=python-builder /root/.cache/ms-playwright /root/.cache/ms-playwright
COPY --from=node-builder $APP_HOME/static/css/ $APP_HOME/static/css/

COPY . .
