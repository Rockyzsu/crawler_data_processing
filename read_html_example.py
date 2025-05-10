import requests
import pandas as pd
from io import StringIO

url = "https://www.fortunechina.com/fortune500/c/2024-08/05/content_456697.htm"

payload = {}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',

}

response = requests.request("GET", url, headers=headers, data=payload)
response.encoding = 'utf8'
df = pd.read_html(StringIO(response.text))[0]
print(df.head(10))
