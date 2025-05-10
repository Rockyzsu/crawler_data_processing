import requests
from parsel import Selector


url = "https://www.fortunechina.com/fortune500/c/2024-08/05/content_456697.htm"

payload = {}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',

}

response = requests.request("GET", url, headers=headers, data=payload)
response.encoding = 'utf8'
resp = Selector(text=response.text)
nodes = resp.xpath(
    '//div[@class="hf-right word-img2"]/div[@class="word-table"]/div[@class="wt-table-wrap"]/table/tbody/tr')

cn_count = 0
us_count = 0
for node in nodes:
    num = node.xpath('./td[1]/text()').extract_first()
    name = node.xpath('./td[2]/a/text()').extract_first()
    income = node.xpath('./td[3]/text()').extract_first()
    profit = node.xpath('./td[4]/text()').extract_first()
    country = node.xpath('./td[5]/text()').extract_first()
    if country == '中国':
        cn_count += 1
        print(num, name, income, profit, country)

    if country == '美国':
        us_count += 1

print('500强中国企业数量：', cn_count)
print('500强美国企业数量：', us_count)
