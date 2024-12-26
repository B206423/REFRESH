FROM python:3.11.11-slim-bookworm

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.4

# System deps (we don't use exact versions because it is hard to update them,
# pin when needed):
# hadolint ignore=DL3008
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    curl \
    vim \
# clean temp file to reduce docker size 
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# System deps:
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry install --no-interaction --no-ansi --no-root

# Creating folders, and files for a project:
COPY . /app

# RUN pip3 install -r requirements.txt
# TODO: use variable for port number
EXPOSE 8000
CMD ["gunicorn"  , "--workers=1", "--bind", "0.0.0.0:8000", "--timeout", "120", "--log-level=debug", "clientApp:app"]
