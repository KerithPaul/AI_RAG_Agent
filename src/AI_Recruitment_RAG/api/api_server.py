from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from ..config.config_loader import load_configs
import logging
from datetime import datetime, timedelta

from ..agent.llm_interface import query_llm
from fastapi import WebSocket, WebSocketDisconnect

# Load configurations
config, _, _ = load_configs()
logger = logging.getLogger('RAG_Agent')

# Create FastAPI app
app = FastAPI(title="Federal Register RAG Agent")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create templates directory if it doesn't exist
templates_path = Path(__file__).parent.parent.parent.parent / 'templates'
if not templates_path.exists():
    templates_path.mkdir(parents=True)
    logger.info(f"Created templates directory at {templates_path}")

templates = Jinja2Templates(directory=str(templates_path))

# Create and mount static directory
static_path = templates_path / 'static'
if not static_path.exists():
    static_path.mkdir(parents=True)
    logger.info(f"Created static directory at {static_path}")

app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        while True:
            try:
                # Receive message
                user_query = await websocket.receive_text()
                logger.info(f"Received query: {user_query}")
                
                # Process through LLM
                response = await query_llm(user_query)
                
                # Send response
                await websocket.send_text(response)
                logger.info("Response sent successfully")
                
            except WebSocketDisconnect:
                logger.info("WebSocket connection closed by client")
                break
            except Exception as e:
                error_message = f"Error processing query: {str(e)}"
                logger.error(error_message)
                await websocket.send_text(error_message)
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        try:
            await websocket.close()
        except:
            pass
        

@app.get("/")
async def home(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/config")
async def get_config():
    """Get public configuration"""
    return {
        "api_version": "1.0",
        "max_query_length": 1000,
        "supported_date_format": "YYYY-MM-DD"
    }