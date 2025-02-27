FROM python:3.13.2-slim-bookworm
RUN pip install poetry
WORKDIR /ollabot
COPY . .
RUN poetry config virtualenvs.in-project true
RUN poetry install
EXPOSE 8000 8051
CMD poetry run uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload && poetry run streamlit run app.py