import asyncio
from src.AI_Recruitment_RAG.agent.llm_interface import query_llm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Test query
    query = "Find executive documents from the last 7 days"
    result = query_llm(query)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())