FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --create-home --uid 10001 rhinoguard
WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY scenarios ./scenarios
COPY fixtures ./fixtures
COPY policies ./policies

RUN python -m pip install .

USER rhinoguard
EXPOSE 8080
CMD ["uvicorn", "rhinoguard.api.app:app", "--host", "0.0.0.0", "--port", "8080"]

# Clarify implementation notes for dockerfile
