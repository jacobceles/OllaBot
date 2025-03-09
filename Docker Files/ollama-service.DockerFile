FROM ubuntu:latest
RUN apt-get update && apt-get install -y curl
RUN curl -L https://ollama.ai/install.sh | sh
EXPOSE 11434