import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s')

project_name = "AI_Recruitment_RAG"

list_of_files = [
    ".github/workflows/.gitkeep",

    # Data Pipeline Modules
    f"src/{project_name}/data_pipeline/__init__.py",
    f"src/{project_name}/data_pipeline/fetch_data.py",  # Handles API fetching
    f"src/{project_name}/data_pipeline/process_data.py",  # Cleans & transforms data
    f"src/{project_name}/data_pipeline/store_data.py",  # Stores in MySQL

    # Agent System
    f"src/{project_name}/agent/__init__.py",
    f"src/{project_name}/agent/tool_calls.py",  # Defines function schema for LLM
    f"src/{project_name}/agent/execute_tools.py",  # Parses & executes tool calls
    f"src/{project_name}/agent/llm_interface.py",  # Connects to Ollama/LLM engine

    # API Interface
    f"src/{project_name}/api/__init__.py",
    f"src/{project_name}/api/websocket_interface.py",  # Websocket-based API
    f"src/{project_name}/api/api_server.py",  # FastAPI-based endpoints

    # Utils & Configs
    f"src/{project_name}/utils/__init__.py",
    f"src/{project_name}/utils/common.py",  # Utility functions
    f"src/{project_name}/config/__init__.py",
    f"src/{project_name}/config/configuration.py",  # Load API keys & configs

    # Entity & Database Schema
    f"src/{project_name}/entity/__init__.py",
    f"src/{project_name}/entity/db_schema.py",  # Defines MySQL table structures

    # Constants
    f"src/{project_name}/constants/__init__.py",

    # Config Files
    "config/config.yaml",
    "params.yaml",
    "dvc.yaml",  # If using Data Version Control for pipeline tracking
    "schema.yaml",  # Defines expected data format

    # Main System Entrypoints
    "main.py",  # Runs the full system
    "app.py",  # API endpoint entry point

    # Deployment & Documentation
    "Dockerfile",
    "README.md",
    "requirements.txt",
    "setup.py",

    # Research & Testing
    "research/prototyping.ipynb",  # Jupyter notebook for dev experiments

    # UI Components
    "templates/index.html"  # Basic chat UI
]

# Creating directories and files
for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for file: {filename}")
    
    if not os.path.exists(filepath) or (os.path.getsize(filepath) == 0):
        with open(filepath, 'w') as f:
            pass
        logging.info(f"Creating file: {filename} at {filepath}")
    else:
        logging.info(f"File {filename} already exists at {filepath}.")