FROM python:3.13.2-slim-bookworm
WORKDIR /fastapi
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install
COPY . .
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]