FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /code

COPY ./pyproject.toml /code/pyproject.toml
COPY ./src /code/src
RUN uv pip install . --system

EXPOSE 3000

ENV DATABASE_URL="sqlite:///./app.db"

COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
