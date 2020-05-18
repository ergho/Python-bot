import requests
import time

url: str = 'https://google.se'
number_reqs: int = 50

def sync_main(url: str, number_reqs: int):
    session = requests.Session()
    for x in range(number_reqs):
        print(f'request number: {x} to {url}')
        resp = session.get(url)
        if resp.status_code == 200:
            pass

start_time: float = time.perf_counter()
sync_main(url, number_reqs)
end_time: float = time.perf_counter() - start_time
print(f'Time taken: {end_time:0.2f}')

import time
import asyncio
import aiohttp

async def make_req(session, url: str, req_n: int):
    print(f'request number: {req_n} to {url}')
    async with session.get(url) as resp:
        if resp.status == 200:
            await resp.text()

async def async_main(url: str, number_reqs: int):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[make_req(session, url, x) for x in range(number_reqs)]
        )

start_time = time.perf_counter()
asyncio.run(async_main(url, number_reqs))
end_time = time.perf_counter() - start_time
print(f' Sync total time: {end_time:0.2f}')