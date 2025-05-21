from fastapi import WebSocket, WebSocketDisconnect
import logging
from ..agent.llm_interface import query_llm
from ..config.config_loader import load_configs

logger = logging.getLogger('RAG_Agent')
config, _, _ = load_configs()

async def handle_websocket_connection(websocket: WebSocket):
    """Handle individual WebSocket connection"""
    try:
        await websocket.accept()
        logger.info("New WebSocket connection established")
        
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

def setup_websocket(app):
    """Setup WebSocket route"""
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await handle_websocket_connection(websocket)