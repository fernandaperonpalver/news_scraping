import pandas as pd
import requests



def check_link_status(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code, None
    except requests.RequestException as e:
        return 'error', str(e)

# Exemplo de DataFrame
# Substitua pelos seus dados reais
df = pd.read_csv('remaining_com_url.csv')

# Inicializar novas colunas para as respostas e erros
df['response'] = None
df['error'] = None

# Iterar sobre os links e verificar cada um
for index, row in df.iterrows():
    status, error = check_link_status(row['url'])
    print(status, error)
    df.at[index, 'response'] = status
    df.at[index, 'error'] = error

df.to_excel('remaining_with_response.xlsx')