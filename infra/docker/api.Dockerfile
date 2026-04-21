FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY apps ./apps
COPY packages ./packages
COPY workers ./workers
COPY scripts ./scripts

RUN pip install --no-cache-dir fastapi pydantic uvicorn pg8000 httpx

CMD ["python", "scripts/run_api.py"]
