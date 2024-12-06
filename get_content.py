## colocar estratégia de extração generalizada para todo html

import asyncio
import json
from dataclasses import dataclass

import aiohttp
from lxml import html

from extractors.article import Article, GloboArticle, R7Article, UOLArticle
from scraping_scripts import get_urls


async def extract_elements(article_info):
    portal_info = []

    async with aiohttp.ClientSession() as session:
        for url in article_info:  ##iterar sobre url e xpath_description do article_info
            try:
                async with session.get(url) as response:
                    html_content = await response.text()
                    tree = html.fromstring(
                        html_content
                    )  # nao usar html como nome de variável senão dá confusão
                    ##
                    description = tree.xpath(xpath_description)

                    article = Article(
                        url=url,
                        description=description[0] if description else None,
                    )

                    portal_info.append(article)
                    print(portal_info)

            except Exception as e:
                print(f"Erro ao processar URL {url}: {e}")
    return portal_info


#  "https://www.r7.com/arc/outboundfeeds/sitemap-news/?outputType=xml",
async def main(feeds):
    html_urls = await get_urls(feeds)
    # html_urls = html_urls[:20]
    # portais = await extract_elements(html_urls)
    print(html_urls)


##usar ld-json para pegar o que puder da maneira mais generalizável possível


if __name__ == "__main__":
    feeds = [UOLArticle(), R7Article(), GloboArticle()]
    asyncio.run(main(feeds))
