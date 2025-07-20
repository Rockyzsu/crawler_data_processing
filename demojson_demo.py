import datetime
import requests
headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "Cache-Control": "no-cache",
            "Cookie": "AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; em_hq_fls=js; HAList=a-sh-603707-%u5065%u53CB%u80A1%u4EFD%2Ca-sz-300999-%u91D1%u9F99%u9C7C%2Ca-sh-605338-%u5DF4%u6BD4%u98DF%u54C1%2Ca-sh-600837-%u6D77%u901A%u8BC1%u5238%2Ca-sh-600030-%u4E2D%u4FE1%u8BC1%u5238%2Ca-sz-300059-%u4E1C%u65B9%u8D22%u5BCC%2Cd-hk-06185; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; qgqp_b_id=956b72f8de13e912a4fc731a7845a6f8; searchbar_code=163407_588080_501077_163406_001665_001664_007049_004433_005827_110011; EMFUND0=null; EMFUND5=02-24%2019%3A30%3A19@%23%24%u5357%u65B9%u6709%u8272%u91D1%u5C5EETF%u8054%u63A5C@%23%24004433; EMFUND6=02-24%2021%3A46%3A42@%23%24%u5357%u65B9%u4E2D%u8BC1%u7533%u4E07%u6709%u8272%u91D1%u5C5EETF@%23%24512400; EMFUND7=02-24%2021%3A58%3A27@%23%24%u6613%u65B9%u8FBE%u84DD%u7B79%u7CBE%u9009%u6DF7%u5408@%23%24005827; EMFUND8=03-05%2015%3A33%3A29@%23%24%u6613%u65B9%u8FBE%u4E2D%u5C0F%u76D8%u6DF7%u5408@%23%24110011; EMFUND9=03-05 23:47:41@#$%u5929%u5F18%u4F59%u989D%u5B9D%u8D27%u5E01@%23%24000198; ASP.NET_SessionId=ntwtbzdkb0vpkzvil2a3h1ip; st_si=44251094035925; st_asi=delete; st_pvi=77351447730109; st_sp=2020-08-16%2015%3A54%3A02; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=3; st_psi=20210309200219784-0-8081344721",
            "Host": "fund.eastmoney.com",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://fund.eastmoney.com/data/fundranking.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
        }


def demo1():
    url = "https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx"
    params = {
        "t": "8",
        "page": "1,50000",
        "js": "reData",
        "sort": "fcode,asc",
    }

    r = requests.get(url, params=params, headers=headers)
    data_text = r.text
    print(data_text)


def demo2():
    time_interval = 'jnzf'
    ft = 'hh'
    td_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    td_dt = datetime.datetime.strptime(td_str, '%Y-%m-%d')
    # 去年今日
    last_dt = td_dt - datetime.timedelta(days=365)
    last_str = datetime.datetime.strftime(last_dt, '%Y-%m-%d')
    # rank_url = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft={0}&rs=&gs=0&sc={1}zf&st=desc&sd={2}&ed={3}&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1'.format(
    #     ft, time_interval, last_str, td_str)
    rank_url = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft={0}&rs=&gs=0&sc={1}&st=desc&sd={2}&ed={3}&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1'.format(
        ft, time_interval, last_str, td_str)

    print(rank_url)
    # r = requests.get(rank_url, headers=headers)
    # print(r.text)

def demo3():
    url="https://swapi.dev/api/people/"
    r = requests.get(url,verify=False)
    data_text = r.json()
    print(data_text)


def dump_mongodb():
    import pymongo

    url="https://swapi.dev/api/people/"
    response = requests.get(url,verify=False)
    json_data = response.json()

    user='root'
    password='byb202007leave'
    host='134.175.130.90'
    port='17018'

    connect_uri = f'mongodb://{user}:{password}@{host}:{port}'
    client = pymongo.MongoClient(connect_uri)
    db = client['db_spider']
    collection = db['wars_star']
    collection.insert_many(json_data['results'])

# demo2()
# demo3()
dump_mongodb()
