FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install dependencies and create user in single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && pip install --no-cache-dir pipenv \
    && adduser --disabled-password --gecos '' --shell /bin/bash appuser \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY Pipfile Pipfile.lock* ./
RUN pipenv install --system --deploy --ignore-pipfile

# Copy app and set ownership
COPY --chown=appuser:appuser ./app /app

USER appuser

EXPOSE ${APP_PORT:-8001}

CMD ["sh", "-c", "fastapi run --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8001}"]
