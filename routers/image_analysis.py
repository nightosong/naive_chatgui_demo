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
            async with session.get(image_url, timeout=30) as response:
                if response.status == 200:
                    image_content = await response.read()
                    return await asyncio.to_thread(read_image_text, image_content, True)
        except Exception as e:
            print(f"Error fetching image from {image_url}: {e}")
    return ""


async def process_row(data: list, llm: LLMType, row: int):
    try:
        image_url = json.loads(data[5])[0]
        image_text = await fetch_image_text(image_url)
        image_prompt = schema.prompts.image_text_summary.format(query_str=image_text)
        response = await llm.acomplete(image_prompt)
        return response.text
    except Exception as e:
        print(f"Error processing row {row} with data {data}: {e}")
    return ""


async def load_excel_analysis(
    load_file: str, save_file: str, batch_size=10, max_concurrency=5
):
    llm_mgr = LlamaChatModelManager(schema.chat_models)
    llm = llm_mgr.load()

    generator = ExcelReader.load_data_by_row(load_file)
    last_run_end = 100
    step_per_run = 1000
    start = 0
    while start < last_run_end:
        next(generator)
        start += 1

    semaphore = asyncio.Semaphore(max_concurrency)

    row = 2
    batch = []

    async def process_batch(batch_data, start_row):
        nonlocal row
        tasks = []
        start_row_lazy = start_row
        async with semaphore:
            for data in batch_data:
                tasks.append(process_row(data, llm, start_row))
                start_row += 1

        batch_responses = await asyncio.gather(*tasks)
        batch_rows = list(range(start_row_lazy, start_row_lazy + batch_size + 1))
        await asyncio.to_thread(
            ExcelReader.insert_cells, save_file, batch_rows, 7, batch_responses
        )

    for data in tqdm(generator):
        batch.append(data)
        if len(batch) >= batch_size:
            await process_batch(batch, row)
            batch = []
            row += batch_size
        if step_per_run < 0:
            break
        step_per_run -= 1

    if batch:
        await process_batch(batch, row)


if __name__ == "__main__":
    asyncio.run(load_excel_analysis("products.xlsx", "results.xlsx"))
