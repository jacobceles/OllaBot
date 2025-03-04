FROM python:3.13.2-slim-bookworm
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    bash \
    git \
    build-essential \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install poetry
RUN curl -fsSL https://ollama.com/install.sh | sh
WORKDIR /ollabot
COPY . .
RUN mkdir -p /root/.ollama
COPY .ollama /root/.ollama
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x entrypoint.sh
RUN chmod +x /usr/local/bin/ollama
RUN poetry config virtualenvs.in-project true
RUN poetry install
EXPOSE 8000 8501 11434
ENTRYPOINT ["/entrypoint.sh"]