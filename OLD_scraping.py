import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup

from date_strategy import data_format

urls_rss = ["https://g1.globo.com/rss/g1/educacao/"]

urls_sitemap = ["https://noticias.uol.com.br/sitemap/v2/today.xml"]

#  "https://www.r7.com/arc/outboundfeeds/sitemap-news/?outputType=xml",


# adicionar funcoes assync dentro de funcoes assync e rodar elas
async def check_dates(item, link, dic_info):
    date_rules = {
        "globo": lambda item: item.find("pubDate"),
        "r7": lambda item: item.find("news:publication_date"),
        "uol": lambda item: item.find("lastmod"),
    }

    for site, rule in date_rules.items():
        if site in link:
            data = rule(item)
            if data:
                raw_date = data.get_text(strip=True)
                parsed_date = data_format(raw_date)
                dic_info["datas"].append(parsed_date)
                return

    dic_info["datas"].append(None)


async def get_news_sitemap(urls: list) -> dict:
    start = 0
    dic_info_sitemap = {"titulos": [], "description": [], "datas": [], "portal": []}
    async with aiohttp.ClientSession() as session:
        for url in urls:
            if "sitemap" in url:
                async with session.get(url) as response:
                    text = await response.text()
                    soup = BeautifulSoup(text, "html.parser")
                    for item in soup.find_all("url"):
                        link = item.find("loc").get_text(strip=True)
                        dic_info_sitemap["portal"].append(link)

                        await check_dates(item, link, dic_info_sitemap)
                        start += 1
                        print(start)
    return dic_info_sitemap


async def get_news_rss(urls: list) -> dict:
    dic_info_rss = {"titulos": [], "description": [], "datas": [], "portal": []}
    start = 1

    async with aiohttp.ClientSession() as session:
        for url in urls:
            if "rss" in url:
                async with session.get(url) as response:
                    text = await response.text()

                    try:
                        root = ET.fromstring(text)

                        for item in root.findall(".//item"):
                            print(ET.tostring(item, encoding="unicode"))
                            link_elem = item.find("link")
                            if link_elem is not None and link_elem.text:
                                link = link_elem.text.strip()
                                dic_info_rss["portal"].append(link)

                                await check_dates(item, link, dic_info_rss)

                            start += 1
                            print(f"Processados: {start}")

                    except ET.ParseError as e:
                        print(f"Error parsing XML from {url}: {e}")
                        continue

    return dic_info_rss


async def get_report_data(urls_rss: list, urls_sitemap: list) -> pd.DataFrame:
    dict1, dict2 = await asyncio.gather(
        get_news_rss(urls_rss), get_news_sitemap(urls_sitemap)
    )
    dic_info = {**dict1, **dict2}

    teste = 1
    async with aiohttp.ClientSession() as session:
        for url in dic_info["portal"]:
            try:
                # Fazer a requisição assíncrona
                async with session.get(url) as response:
                    text = await response.text()
                    soup = BeautifulSoup(text, "html.parser")

                    # Título
                    title = (
                        soup.find("title")
                        .get_text(strip=True)
                        .encode("utf-8")
                        .decode("utf-8")
                        if soup.find("title")
                        else ""
                    )
                    dic_info["titulos"].append(title)

                    # Descrição
                    descriptions = (
                        soup.find("meta", {"name": "description"})
                        .get("content", "")
                        .encode("utf-8")
                        .decode("utf-8")
                        if soup.find("meta", {"name": "description"})
                        else ""
                    )

                    if not descriptions:
                        descriptions = (
                            soup.find("meta", {"itemprop": "alternateName"}).get(
                                "content", ""
                            )
                            if soup.find("meta", {"itemprop": "alternateName"})
                            else None
                        )

                    dic_info["description"].append(descriptions)

                teste += 1
                print(f"teste_{teste}")

            except Exception as e:
                print(f"Erro ao processar URL {url}: {e}")
                dic_info["titulos"].append(None)
                dic_info["description"].append(None)

    # Convert to DataFrame
    df = pd.DataFrame(dic_info)
    df.to_csv("result.csv")
    return df


async def main():
    await get_report_data(urls_rss, urls_sitemap)


if __name__ == "__main__":
    asyncio.run(main())
