from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

noticias = [
    "https://noticias.uol.com.br/sitemap/v2/today.xml",
    "https://g1.globo.com/rss/g1/educacao/",
    "https://www.r7.com/arc/outboundfeeds/sitemap-news/?outputType=xml",
]


def clean_text(df):
    df["titulos"] = df["titulos"].apply(
        lambda x: unicodedata.normalize("NFKD", x)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )
    return df


def check_dates(item, link, dic_info):
    if "globo" in link:
        data = item.find("pubDate")
        if data:
            pub_date_iso = datetime.strptime(
                data.get_text(strip=True), "%a, %d %b %Y %H:%M:%S %z"
            ).isoformat()
        else:
            pub_date_iso = None
        dic_info["datas"].append(pub_date_iso)

    elif "r7" in link:
        data = item.find("news:publication_date")
        if data:
            data = data.get_text(strip=True).replace("Z", "+00:00")
            pub_date_iso = datetime.fromisoformat(data).isoformat()
        else:
            pub_date_iso = None
        dic_info["datas"].append(pub_date_iso)

    elif "uol" in link:
        data = item.find("lastmod")
        if data:
            data = data.get_text(strip=True).replace("Z", "+00:00")
            pub_date_iso = datetime.fromisoformat(data).isoformat()
        else:
            pub_date_iso = None
        dic_info["datas"].append(pub_date_iso)


def get_news(urls: list) -> dict:
    start = 0
    dic_info = {"titulos": [], "description": [], "datas": [], "portal": []}

    for url in urls:
        if "sitemap" in url:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.find_all("url"):
                link = item.find("loc").get_text(strip=True)
                dic_info["portal"].append(link)
                check_dates(item, link, dic_info)

        elif "rss" in url:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "xml")
            for item in soup.find_all("item"):
                link = item.find("link").get_text(strip=True)
                dic_info["portal"].append(link)
                check_dates(item, link, dic_info)
        start += 1
        print(start)

    return dic_info


def get_report_data(urls: list) -> pd.DataFrame:
    dic_info = get_news(urls)
    for url in dic_info["portal"]:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Title
        title = soup.find("title").get_text(strip=True) if soup.find("title") else ""
        dic_info["titulos"].append(title)

        # Description

        descriptions = (
            soup.find("meta", {"name": "description"}).get("content", "")
            if soup.find("meta", {"name": "description"})
            else ""
        )
        if not descriptions:
            descriptions = (
                soup.find("meta", {"itemprop": "alternateName"}).get("content", "")
                if soup.find("meta", {"itemprop": "alternateName"})
                else None
            )

        dic_info["description"].append(descriptions)

    # Convert to DataFrame
    df = pd.DataFrame(dic_info)
    return df


df = get_report_data(noticias)
df = clean_text(df)
df.to_csv("result.csv")
