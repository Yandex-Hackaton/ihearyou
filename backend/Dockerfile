FROM python:3.12.3

# Poetry config
ENV POETRY_VERSION=2.2.1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_HOME=/opt/poetry
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry globally
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

WORKDIR /app

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi

# Copy project (без .venv — её игнорирует .dockerignore)
COPY . .

CMD ["poetry", "run", "uvicorn", "admin.app:app", "--host", "0.0.0.0", "--port", "8000"]