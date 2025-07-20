import pandas as pd
from influxdb import InfluxDBClient
import yfinance as yf
# from influxdb_client import InfluxDBClient, Point, WritePrecision
# from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta
import pytz
import akshare as ak

# ========================
# 配置区域（按需修改）
# ========================

INFLUX_CONFIG = {
    "url": "http://localhost:8086",         # InfluxDB地址
    "token": "your_admin_token",            # InfluxDB访问令牌
    "org": "your_org",                      # 组织名称
    "bucket": "stock_data"                  # 存储桶名称
}

STOCKS = ["AAPL", "MSFT", "GOOGL", "TSLA"]  # 要监控的股票代码
TIMEZONE = pytz.timezone("America/New_York")  # 股票市场时区


# ========================
# 获取股票数据
# ========================
def fetch_stock_data(ticker):

    df = ak.stock_us_daily(symbol=ticker)  # 苹果历史数据
    print(df.tail())
    return df.tail(200)


# connect to InfluxDB
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('db_stock')


def write_data_to_influx_db(df):

    date_column = 'date'
    # make sure date column is datetime type
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])
    df['symbol'] = 'NVDA'
    # set date column as index
    points = []
    for _, row in df.iterrows():
        point = {
            "measurement": "stock_data",  # measurement is like a table in SQL
            "time": row["date"],
            "tags": {
                "ticker": row["symbol"]  # ticker is like a column in SQL
            },
            "fields": {
                "open": row["open"],
                "close": row["close"],
                "high": row["high"],
                "low": row["low"],
                "volume": row["volume"]
                
            }
        }
        points.append(point)

    try:
        client.write_points(
            points=points,
            time_precision='s'
        )
    except Exception as e:
        print(f"Error writing data: {e}")
    finally:
        client.close()

def query_data_from_influx_db():
    query = 'SELECT * FROM stock_data WHERE ticker = \'NVDA\' ORDER BY time DESC'
    result = client.query(query)
    df = pd.DataFrame(list(result.get_points()))
    print(df.head())

if __name__ == '__main__':
    # df = fetch_stock_data("NVDA")
    # write_data_to_influx_db(df)
    query_data_from_influx_db()