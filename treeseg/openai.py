''' OpenAI embeddings '''
import aiohttp
import asyncio

from .embeddings import Embeddings

async def openai_embeddings(config: Embeddings, chunks:list) -> list:
    """Retrieve embeddings using OpenAI."""
    task_params = json.dumps({"model": config.model, "input": chunks})
    async with aiohttp.ClientSession(headers=config.headers) as session:
        async with session.post(
            config.endpoint,
            data=task_params,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status != 200:
                logger.error(await response.json())
                raise Exception("EmbeddingRequestFailed", f"status={response.status}")
            obj = await response.json()
            return [entry["embedding"] for entry in obj["data"]]
