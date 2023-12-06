FROM python:3.11-slim-bullseye

WORKDIR /code

COPY ./pyproject.toml /code/pyproject.toml
COPY ./src /code/src
RUN pip install /code

EXPOSE 5052

ENV DATABASE_URL="sqlite:///./app.db"

COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5052"]