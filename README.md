### Federal Register RAG Agent ###

--A Retrieval-Augmented Generation (RAG) system for Federal Register  documents with daily updates and real-time querying capabilities.

### System Requirements ###

 -> Python 3.8+
 -> MySQL Server 8.0+
 -> Windows 10/11
 -> Git


### Installation ###

 1. Clone the repository:

    git clone https://github.com/yourusername/RAG_Agent.git
    cd RAG_Agent

 2. Create and activate virtual environment:

    python -m venv env
    .\env\Scripts\activate

 3. Install required packages:

    pip install -r requirements.txt


### Configuration ###

 1. Create MySQL database:

    CREATE DATABASE federal_register;

 2. Configure the application:

    database:
        host: "localhost"
        user: "your_username"
        password: "your_password"
        database: "federal_register"
        charset: "utf8mb4"
        port: 3306

    data_pipeline:
        fetch:
            start_date: "2025-01-01"
            batch_size: 1000
        pagination:
            enabled: true
            per_page: 100


### Project Structure ###

RAG_Agent/
├── src/
│   └── AI_Recruitment_RAG/
│       ├── agent/         # LLM interface
│       ├── api/          # FastAPI server
│       ├── config/       # Configuration
│       ├── data_pipeline/ # ETL pipeline
│       └── static/       # Static files
├── templates/           # HTML templates
├── scripts/            # Update scripts
└── logs/              # Application logs


### Running the Application ###

 1. Start the application:

    python main.py

 2. Access the web interface:

    http://127.0.0.1:8000


### Setting Up Daily Updates ###

 1. Create scheduled task:

    cd scripts
    .\setup_task.ps1

 2. Verify task creation:

    Task Scheduler -> Federal Register Update


### Features ###

--Real-time document querying
--Daily data updates
--WebSocket communication
--Data pipeline monitoring
--Coverage verification


### API Endpoints ###

-- /: Main chat interface
-- /ws: WebSocket endpoint
-- /health: Health check
-- /api/config: Configuration info


### Data Pipeline ###

The system:

--Fetches Federal Register documents
--Processes and cleanses data
--Stores in MySQL database
--Verifies data coverage
--Updates daily at midnight


### Monitoring ###

Check application logs:

    logs/system.log
    logs/daily_update.log


### Testing ###

Run tests:

    pytest tests/


### Error Handling ###

The system includes:

--Retry mechanisms
--Error logging
--Transaction management
--Data validation


### Contributing ###

--Fork the repository
--Create feature branch
--Commit changes
--Push to branch
--Create Pull Request

### Contact ###
Your Name - kerithpaul188@gmail.com

This README provides a comprehensive guide for:

Installation
Configuration
Running the application
Monitoring
Contributing

Make sure to replace placeholder values with your actual:

Database credentials
Contact information
Repository URL