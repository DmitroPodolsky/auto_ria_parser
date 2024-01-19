import asyncio
from app.db import Manager
from app.parser import WebUrls, get_data


if __name__ == "__main__":
    database = Manager()
    web_parser = WebUrls()
    urls = web_parser.get_urls()
    
    loop = asyncio.get_event_loop()
    values = loop.run_until_complete(get_data(urls))
    loop.close()
    
    database.insert_data(values)
    database.dump_data()