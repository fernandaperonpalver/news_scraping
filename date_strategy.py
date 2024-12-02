import asyncio
import re
from datetime import datetime

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup


def parse_iso(data: str) -> datetime:
    try:
        data = re.sub(r"\.?\d*Z$", "", data)
        return datetime.strptime(data, "%Y-%m-%dT%H:%M:%S")
    except ValueError as e:
        raise ValueError(f"parse_iso: Could not parse date: {data}") from e


def parse_portuguese(data: str) -> datetime:
    try:
        return datetime.strptime(data, "%d/%m/%Y %H:%M:%S")
    except ValueError as e:
        raise ValueError(f"parse_portuguese: Could not parse date: {data}") from e


def parse_pub_date(data: str) -> datetime:
    try:
        data = re.sub(r"<\/?pubDate>", "", data).strip()
        return datetime.strptime(data, "%a, %d %b %Y %H:%M:%S %z")
    except ValueError as e:
        raise ValueError(f"parse_pub_date: Could not parse date: {data}") from e


def data_format(data: str):
    strategies = [parse_iso, parse_portuguese, parse_pub_date]
    for parser in strategies:
        try:
            return parser(data)
        except ValueError as e:
            # Debug detalhado para entender erros
            print(f"Erro ao tentar {parser.__name__} com data: {data}")
            continue
    return "erro"
