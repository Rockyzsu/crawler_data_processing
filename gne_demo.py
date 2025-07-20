import requests
from gne import GeneralNewsExtractor

url = "https://www.chinadaily.com.cn/a/202505/24/WS68317c10a310a04af22c1529.html"


def crawl(url):

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
        'Referer': 'https://www.chinadaily.com.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

    response = requests.request("GET", url, headers=headers)
    return response.text


extractor = GeneralNewsExtractor()

html = crawl(url)
result = extractor.extract(html)
print('Title --> ', result['title'], '\n')
print('Content -->', result['content'], '\n')
print('PublishTime -->', result['publish_time'])
