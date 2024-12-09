from dataclasses import dataclass


@dataclass
class Article:
    portal: str
    url: str = ""
    title: str = ""
    description: str = ""
    datetime: str = ""
    xpath_title: str = ""
    xpath_date: str = ""
    xpath_description: str = ""


@dataclass
class GloboArticle(Article):
    portal: str = "globo"
    feed: str = "https://g1.globo.com/rss/g1/educacao/"
    xpath_title: str = "//item/title/text()"
    xpath_url: str = "//item/link/text()"
    xpath_date: str = "//item/pubDate/text()"
    xpath_description: str = '//meta[@name="description"]/@content'


@dataclass
class UOLArticle(Article):
    portal: str = "uol"
    feed: str = "https://noticias.uol.com.br/sitemap/v2/today.xml"
    xpath_title: str = '//meta[@property="og:title"]/@content'
    xpath_url: str = "loc"
    xpath_date: str = "lastmod"
    xpath_description: str = '//meta[@property="og:description"]/@content'


@dataclass
class R7Article(Article):
    portal: str = "r7"
    feed: str = "https://www.r7.com/arc/outboundfeeds/sitemap-news/?outputType=xml"
    xpath_title: str = '//meta[@property="og:title"]/@content'
    xpath_url: str = "loc"
    xpath_date: str = "lastmod"
    xpath_description: str = '//meta[@property="og:description"]/@content'
