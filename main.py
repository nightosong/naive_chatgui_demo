import aiohttp
import asyncio
import json
import logging
from tqdm import tqdm
from modules.loaders import SchemaLoader
from modules.models import LlamaChatModelManager, LLMType
from modules.readers import read_image_text, ExcelReader

schema = SchemaLoader("schema.yaml")
logging.getLogger("ppocr").setLevel(level=logging.WARNING)


async def fetch_image_text(image_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(image_url, timeout=10) as response:
                if response.status == 200:
                    image_content = await response.read()
                    return await asyncio.to_thread(read_image_text, image_content, True)
        except Exception as e:
            print(f"Error fetching image from {image_url}: {e}")
    return ""


async def process_row(data: list, llm: LLMType, row: int, save_file: str):
    try:
        image_url = json.loads(data[5])[0]
        image_text = await fetch_image_text(image_url)
        image_prompt = schema.prompts.image_text_summary.format(query_str=image_text)
        response = await llm.acomplete(image_prompt)

        asyncio.to_thread(ExcelReader.insert_cell, save_file, row, 7, response.text)

    except Exception as e:
        print(f"Error processing row {row} with data {data}: {e}")


async def load_excel_analysis(
    load_file: str, save_file: str, batch_size=100, max_concurrency=10
):
    llm_mgr = LlamaChatModelManager(schema.chat_models)
    llm = llm_mgr.load()

    generator = ExcelReader.load_data_by_row(load_file)
    semaphore = asyncio.Semaphore(max_concurrency)

    row = 2
    batch = []

    async def process_batch(batch_data, start_row):
        nonlocal row
        tasks = []
        async with semaphore:
            for data in batch_data:
                tasks.append(process_row(data, llm, start_row, save_file))
                start_row += 1
        await asyncio.gather(*tasks)

    for data in tqdm(generator, miniters=10):
        batch.append(data)
        if len(batch) >= batch_size:
            await process_batch(batch, row)
            batch = []
            row += batch_size

    if batch:
        await process_batch(batch, row)


if __name__ == "__main__":
    asyncio.run(load_excel_analysis("product.xlsx", "results.xlsx"))
