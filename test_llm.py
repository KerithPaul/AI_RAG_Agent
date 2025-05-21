import asyncio
import logging
from src.AI_Recruitment_RAG.agent.llm_interface import query_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Test queries
    queries = [
        "Find executive documents from the last 7 days related to healthcare",
        "What are the recent executive orders about public health?",
        "Show me documents about medical research from this week"
    ]
    
    for query in queries:
        print(f"\nProcessing query: {query}")
        try:
            result = await query_llm(query)
            print("\nResult:")
            print("-" * 80)
            print(result)
            print("-" * 80)
        except Exception as e:
            print(f"Error: {str(e)}")
        await asyncio.sleep(1)  # Brief pause between queries

if __name__ == "__main__":
    asyncio.run(main())