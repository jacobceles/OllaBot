# OllaBot

## Overview

OllaBot is a Streamlit-based application that allows users to interact with PostgreSQL database using natural language queries. It generates SQL queries, executes them, and provides summarized responses using LLMs powered by Ollama. The project is built using Poetry for dependency management and leverages LlamaIndex for SQL-based retrieval and summarization.

## Features

- Connects to PostgreSQL.
- Converts natural language queries into SQL statements.
- Executes the SQL queries and retrieves data.
- Summarizes the query results using an LLM-based response synthesizer.
- Performs log analysis to extract errors and suggest fixes.
- Simple Streamlit UI for interactive use.

## Project Structure
[text](api/models/.py) [text](api/models/.py)
```
📦 OllaBot
├── app.py                          # Streamlit UI for the bot
├── server.py                       # FastAPI backend for handling queries and log analysis
├── api/
│   ├── models/
│   │   ├── request_models.py       # Pydantic models for API requests
│   ├── services/
│   │   ├── llama_3.2_tokenizer     # Embedding model used to collect token metrics
│   │   ├── database_llm.py         # Database query execution and LLM integration
│   │   ├── log_analysis_llm.py     # Log analysis and summarization
│   ├── configs/
│   │   ├── config.yaml             # Configuration for models and embeddings
│   │   ├── table_config.yaml       # Table metadata for SQL generation
├── .env                            # Environment variables (DB credentials)
├── poetry.lock                     # Poetry lockfile
├── pyproject.toml                  # Poetry dependencies
├── screenshots/                    # Screenshots of the Streamlit application
└── README.md                       # Project documentation
```

## Prerequisites

### 1. Install Dependencies  

Ensure you have Poetry installed. If not, install it via:

```
pip install poetry
```

### 2. Install the Required Packages  

Clone the repository and navigate to the project directory:

```
git clone <repository-url>
cd OllaBot
```

Then, install dependencies with:

```sh
poetry config virtualenvs.in-project true
poetry install
```

### 3. Install and Set Up Ollama  

Ollama is required for generating SQL queries and summarizing responses.

#### Install Ollama  
Download and install from [Ollama's official website](https://ollama.com/download).  

#### Verify Installation  
After installation, check if Ollama is running by executing:  

```sh
ollama list
```

#### Download Models  

After verifying, download and serve the required models by executing:

```sh
ollama pull nomic-embed-text
```
```sh
ollama run qwen2.5-coder
```
```sh
ollama run llama3.2
```

### 4. Set Up the Environment Variables  

Create a `.env` file in the root directory and add the necessary database credentials:

```YAML
# PostgreSQL Credentials
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_HOST=<your_postgres_host>
POSTGRES_PORT=<your_postgres_port>
POSTGRES_DB=<your_postgres_db>
POSTGRES_SCHEMA=<your_postgres_schema>
```

## How to Run the Application

### Automated Running with VS Code Tasks

You can use VS Code's built-in task system to start the FastAPI server and the Streamlit app with a single command. To start the application using VS Code tasks:

1. Open **VS Code** and make sure your project folder is selected.
2. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS) to open the Command Palette.
3. Search for **"Tasks: Run Task"** and select it.
4. Choose one of the following:
   - **"Run Both Apps"** to start both services simultaneously.
   - **"Start FastAPI Server"** to run the backend API.
   - **"Start Streamlit App"** to run the frontend.
5. The terminals for both processes will open inside VS Code.

This approach ensures both the FastAPI server and the Streamlit app start together in an automated way when using VS Code. 

### Alternative: Running from Terminal

You can also run the tasks using the terminal:

```
# Activate Environment
source $(poetry env info --path)/bin/activate

# Start FastAPI Server
python -m server --local

# Start Streamlit App
source $(poetry env info --path)/bin/activate
streamlit run app.py -- --local

```
### Alternative: Running from Kubernetes

To run the app through K8's, first build the Docker images using the Make file 
```
# Docker Build Command
make build-ollabot

Next deploy the images to K8's using the Kustomize yamls

# K8's Deployment
kubectl apply -k [Path to folder containing the specific kustomize yaml]

```

Once the app is running, open [http://localhost:8501](http://localhost:8501) in your browser.

## How It Works

1. **Select a Feature**  
   - "Ask me!" for natural language SQL queries  
   - "Analyze Logs" for log analysis and summarization  

2. **Ask a Question (SQL Query Mode)**  
   - Select the database type (PostgreSQL) from the sidebar  
   - Enter a natural language query in the text box  
   - Click "Ask me!"  

3. **Execution Process**  
   - The app will generate an SQL query using the LLM  
   - Execute it on the selected database  
   - Retrieve and display the SQL query & summary  

4. **Log Analysis Mode**  
   - Paste the log data into the provided text area  
   - Click "Analyze Logs"  
   - The app extracts errors, summarizes them, and provides potential fixes  

## Configuration

### Modify Database Configuration  
Edit the `.env` file to change database credentials.

### Update Table Metadata  
Modify `table_config.yaml` to update table schema and metadata.

### Change LLM Models  
You can update the LLM models used for query generation and summarization by modifying `config.yaml`:

```YAML
models:
  summarize_errors:
    summary_model: "llama3.2:latest"
    embedding_model: "nomic-embed-text:latest"
  database_query:
    query_model: "qwen2.5-coder:latest"
    summary_model: "llama3.2:latest"
    embedding_model: "nomic-embed-text:latest"
```

## Troubleshooting

### Failed to connect to the database
- Check your `.env` file and verify that credentials are correct.

### Ollama model not found
- Ensure Ollama is installed and running:
  
```sh
ollama list
```

### ModuleNotFoundError
- Ensure dependencies are installed using:

```sh
poetry install
```
