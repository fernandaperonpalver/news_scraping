import requests
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata
import pandas as pd


## descrição do código --> primeira faz algumas estratégias para pegar todos os links que estão no sitemap 
 
def clean_text(df): 
    df['titulos'] = df['titulos'].apply(
        lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("utf-8")
    )
    return df



#Parte 1 - Globo
noticias = requests.get('https://g1.globo.com/rss/g1/educacao/')
noticias_text = noticias.text 
 
soup = BeautifulSoup(noticias_text, 'html.parser')

titulos = soup.find_all("title")

dic_info = {"titulos": [], "datas": [], "portal":[]}


for item in soup.find_all("item"):  # Considerando que as informações estão em <item>
    titulo = item.find("title").get_text(strip=True)
    dic_info["titulos"].append(titulo)

    data = item.find("pubdate").get_text(strip=True)
    if data:
        pub_date_iso = datetime.strptime(data, "%a, %d %b %Y %H:%M:%S %z").isoformat()
    else:
        pub_date_iso = None
    dic_info["datas"].append(pub_date_iso)
    dic_info["portal"].append('https://g1.globo.com/rss/g1/educacao/')
    df_globo = pd.DataFrame(dic_info)

#Parte 2 - R7
noticias = requests.get('https://www.r7.com/arc/outboundfeeds/sitemap-news/?outputType=xml')
noticias_text = noticias.text 
 
soup = BeautifulSoup(noticias_text, 'html.parser')

titulos = soup.find_all("title")

dic_info = {"titulos": [], "datas": [], "portal":[]}


for item in soup.find_all("news:news"):  # Considerando que as informações estão em <item>
    titulo = item.find("news:title").get_text(strip=True)
    dic_info["titulos"].append(titulo)

    data = item.find("news:publication_date").get_text(strip=True)
    if data: 
        data = data.replace("Z", "+00:00")
        pub_date_iso = datetime.fromisoformat(data).isoformat()
    else:
        pub_date_iso = None
    dic_info["datas"].append(pub_date_iso)
    dic_info["portal"].append('https://www.r7.com/arc/outboundfeeds/sitemap-news/?outputType=xml')
    df_r7 = pd.DataFrame(dic_info)

#Parte 3 - UOL
noticias = requests.get('https://noticias.uol.com.br/sitemap/v2/today.xml')
noticias_text = noticias.text 
 
soup = BeautifulSoup(noticias_text, 'html.parser')

titulos = soup.find_all("title")

dic_info = {"titulos": [], "datas": [], "portal":[]}


for item in soup.find_all("url"):  # Considerando que as informações estão em <item>
    titulo = item.find("loc").get_text(strip=True)
    ultima_parte = titulo.split("/")[-1]
    sem_extensao = ultima_parte.split(".")[0]
    resultado = sem_extensao.replace("-", " ")
    dic_info["titulos"].append(resultado)

    data = item.find("lastmod").get_text(strip=True)
    if data: 
        data = data.replace("Z", "+00:00")
        pub_date_iso = datetime.fromisoformat(data).isoformat()
    else:
        pub_date_iso = None
    dic_info["datas"].append(pub_date_iso)
    dic_info["portal"].append('https://noticias.uol.com.br/sitemap/v2/today.xml')
    df_uol = pd.DataFrame(dic_info)

 
df_final  = pd.concat([df_r7, df_globo, df_uol], axis = 0)
df_final = clean_text(df_final)
df_final.to_csv('/Users/fernanda/Documents/Palver/news_retrieval/result.csv', index=False)
print(df_final)
##ok, agora preciso pegar o título das matérias

