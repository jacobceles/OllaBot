#!/bin/bash

# Start Ollama in the background
ollama serve &
sleep 5  # Give it time to start

# Debugging: Verify models are actually available
ollama list

# Start application services
poetry run uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload &
poetry run streamlit run app.py &

# Keep the container running
wait