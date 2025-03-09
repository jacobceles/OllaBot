FROM python:3.13.2-slim-bookworm
WORKDIR /streamlit
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
COPY . .
EXPOSE 8501
CMD ["poetry", "run", "streamlit", "run", "app.py"]