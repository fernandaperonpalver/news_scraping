import asyncio
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from typing import List

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree

from extractors.article import Article, GloboArticle, UOLArticle


async def get_news_sitemap(articles_feeds):
    start = 0
    articles_sitemap = []
    async with aiohttp.ClientSession() as session:
        for article_feed in articles_feeds:
            if "sitemap" in article_feed.feed:
                async with session.get(article_feed.feed) as response:
                    text = await response.text()
                    soup = BeautifulSoup(text, "html.parser")
                    for item in soup.find_all("url"):
                        # Find URL and datetime elements
                        link_elem = item.find(article_feed.xpath_url)  # Get URL
                        link = link_elem.get_text(strip=True) if link_elem else ""

                        datetime_elem = item.find(article_feed.xpath_date)
                        date = (
                            datetime_elem.get_text(strip=True) if datetime_elem else ""
                        )

                        articles_sitemap.append(
                            Article(
                                portal=article_feed.portal,
                                url=link,
                                title="",
                                datetime=date,
                                xpath_title=article_feed.xpath_title,
                                xpath_date=article_feed.xpath_date,
                                xpath_description=article_feed.xpath_description,
                            )
                        )
                        start += 1
                        print(f"Getting sitemap_{start}")
    return articles_sitemap


async def get_news_rss(articles_feeds):
    rss_articles = []
    async with aiohttp.ClientSession() as session:
        for article in articles_feeds:
            if "rss" in article.feed:
                async with session.get(article.feed) as response:
                    portal = article.portal
                    text = await response.text()
                    parser = etree.XMLParser(recover=True)
                    root = etree.fromstring(text.encode("utf-8"), parser=parser)

                    # Seleciona todos os <item>
                    items = root.xpath("//item")

                    for item_node in items:
                        # Usa os XPaths definidos no artigo
                        title_list = item_node.xpath(article.xpath_title)
                        url_list = item_node.xpath(article.xpath_url)
                        date_list = item_node.xpath(article.xpath_date)

                        title = title_list[0].strip() if title_list else ""
                        link = url_list[0].strip() if url_list else ""
                        pub_date = date_list[0].strip() if date_list else ""

                        rss_articles.append(
                            Article(
                                portal=portal,
                                url=link,
                                title=title,
                                datetime=pub_date,
                                xpath_title=article.xpath_title,
                                xpath_date=article.xpath_date,
                                xpath_description=article.xpath_description,
                            )
                        )

    return rss_articles


async def get_urls(urls: list) -> list:
    urls_rss = []
    urls_sitemap = []

    for article in urls:
        if "rss" in article.feed:
            urls_rss.append(article)
        else:
            urls_sitemap.append(article)

    article_rss = await get_news_rss(urls_rss)
    article_sitemap = await get_news_sitemap(urls_sitemap)

    articles = article_sitemap + article_rss
    return articles
