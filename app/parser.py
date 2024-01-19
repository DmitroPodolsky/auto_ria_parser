import asyncio
import re

import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from loguru import logger

from app.config import settings

PATTERN_PAGE = re.compile(r"page=(\d+)")
PATTERN_SIZE = re.compile(r"size=(\d+)")


class WebUrls:
    """Class for parsing urls from website"""

    def __init__(self):
        """Initialize url from settings"""
        self.page = 0
        self.url = self.customize_url(settings.URL)

        logger.info(f"WebUrls initialized with url: {self.url}")

    def get_urls(self) -> list[str]:
        """Get urls from website
        :return: list of urls"""
        urls = []
        while True:
            self.url = self.customize_url(self.url, self.page)
            soup = self.get_soup()
            row_urls = soup.find_all(
                "div", class_="item ticket-title"
            )

            if len(row_urls) == 0:
                logger.info(f"Found {len(urls)} urls")
                return urls

            for url in row_urls:
                try:
                    urls.append(url.select_one("a")["href"])
                except Exception as e:
                    logger.error(f"Error for {url}: {e}")
            self.page += 1

    def customize_url(self, url: str, size: int = 100) -> str:
        """Customize url for parsing
        :param url: url for parsing
        :param size: size of page

        :return: customized url"""
        if PATTERN_PAGE.search(url):
            url = re.sub(re.compile(r"page=(\d+)"), f"page={self.page}", url)
        else:
            url += f"&page={self.page}"

        if PATTERN_SIZE.search(url):
            url = re.sub(PATTERN_SIZE, f"size={size}", url)
        else:
            url += f"&size={size}"

        return url

    def get_soup(self) -> BeautifulSoup:
        """Get soup from url
        :return: soup object"""
        response = requests.get(self.url)
        html = response.text
        return BeautifulSoup(html, "html.parser")


async def fetch_data(session: ClientSession, url: str) -> tuple:
    """Fetch data from url
    :param session: aiohttp session
    :param url: url for parsing
    :return: tuple with data"""
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            price = int(
                soup.find("div", class_="price_value")
                .text.replace("$", "")
                .replace(" ", "")
            )
            title = soup.find("h1", class_="head").text.strip()
            distance = (
                int(
                    soup.find("div", class_="base-information bold")
                    .text.strip()
                    .replace(" тис. км пробіг", "")
                )
                * 1000
            )
            photos = soup.find("div", class_="preview-gallery mhide").find_all("a")
            car_number = soup.find("span", class_="state-num ua").contents[0]
            car_vin = soup.find("span", class_="label-vin").text.strip()
            username = soup.find("div", class_="seller_info_name").text.strip()
            return (
                url,
                title,
                price,
                distance,
                username,
                photos[0].select_one("img")["src"],
                len(photos),
                car_number,
                car_vin,
            )
    except Exception as e:
        logger.error(f"Error for {url}: {e}")
        return None


async def get_data(urls: list[str]) -> list[tuple]:
    """Get data from urls
    :param urls: list of urls
    :return: list of tuples with data"""
    async with ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

        results = [result for result in results if result is not None]
        return results
