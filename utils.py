import aiohttp
import asyncio

async def get_dollar_price():
    url = "https://nationalbank.kz/ru/exchangerates/ezhednevnye-oficialnye-rynochnye-kursy-valyut/search"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            for item in data.get("records"):
                if item.get("code") == "USD":
                    return item.get("amount")
    return None
