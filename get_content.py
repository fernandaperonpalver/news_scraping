## colocar estratégia de extração generalizada para todo html

import asyncio
import json
from dataclasses import dataclass

import aiohttp
import pandas as pd
from lxml import html

from date_strategy import data_format
from extractors.article import Article, GloboArticle, R7Article, UOLArticle
from scraping_scripts import get_urls


async def extract_elements_from_html(articles):
    updated_articles = []
    start = 0
    async with aiohttp.ClientSession() as session:
        for article in articles:
            start += 1
            print(start)
            try:
                async with session.get(article.url) as response:
                    html_content = await response.text()
                    tree = html.fromstring(html_content)

                    title_matches = (
                        tree.xpath(article.xpath_title) if article.xpath_title else []
                    )
                    description_matches = (
                        tree.xpath(article.xpath_description)
                        if article.xpath_description
                        else []
                    )

                    updated_article = Article(
                        portal=article.portal,
                        url=article.url,
                        title=title_matches[0] if title_matches else article.title,
                        description=description_matches[0]
                        if description_matches
                        else article.description,
                        datetime=article.datetime,
                        xpath_title=article.xpath_title,
                        xpath_date=article.xpath_date,
                        xpath_description=article.xpath_description,
                    )

                    updated_articles.append(updated_article)

            except Exception as e:
                print(f"Erro ao processar URL {article.url}: {e}")
                # Mantém o artigo sem alterações caso haja exceção
                updated_articles.append(article)

    return updated_articles


async def main(feeds):
    html_urls = await get_urls(feeds)
    portais = await extract_elements_from_html(html_urls)
    df = pd.DataFrame(
        [
            {
                "portal": artigo.portal,
                "title": artigo.title,
                "description": artigo.description,
                "url": artigo.url,
                "datetime": artigo.datetime,
            }
            for artigo in portais  # Itera sobre cada objeto em 'portais'
        ]
    )
    df["datetime"] = df["datetime"].apply(data_format)
    df.to_csv("article_data.csv", index=False)
    return None


if __name__ == "__main__":
    feeds = [UOLArticle(), R7Article(), GloboArticle()]
    asyncio.run(main(feeds))
