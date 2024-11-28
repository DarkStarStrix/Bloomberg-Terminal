import requests
from newsApi import NewsApiClient
import pandas as pd
from datetime import datetime
from Config import *


def fetch_stock_data(symbol, period='1d', interval='1m'):
    stock = yf.Ticker (symbol)
    hist = stock.history (period=period, interval=interval)
    hist ['symbol'] = symbol
    return hist


class DataPipeline:
    def __init__(self):
        self.newsapi = NewsApiClient (api_key=NEWS_API_KEY)
        self.stock_data = pd.DataFrame ()
        self.news_data = pd.DataFrame ()

    def fetch_news(self, query='stock market'):
        articles = self.newsapi.get_everything (q=query, language='en', sort_by='publishedAt', page_size=10)
        return pd.DataFrame (articles ['articles'])

    def process_stock_data(self):
        all_data = []
        for symbol in STOCK_SYMBOLS:
            df = fetch_stock_data (symbol)
            df = df.reset_index ()
            df ['timestamp'] = pd.to_datetime (df ['Datetime']).dt.strftime ('%Y-%m-%d %H:%M:%S')
            df = df [['timestamp', 'symbol', 'Close', 'Volume']]
            df.columns = ['timestamp', 'symbol', 'price', 'volume']
            all_data.append (df)

        self.stock_data = pd.concat (all_data)
        return self.stock_data

    def process_news(self):
        news_df = self.fetch_news ()
        news_df ['timestamp'] = datetime.now ().strftime ('%Y-%m-%d %H:%M:%S')
        news_df ['source_name'] = news_df ['source'].apply (lambda x: x ['name'])
        news_df = news_df.drop ('source', axis=1)

        self.news_data = news_df [['source_name', 'author', 'title', 'description',
                                   'url', 'urlToImage', 'publishedAt', 'content', 'timestamp']]
        return self.news_data

    def get_latest_stock_price(self, symbol):
        stock_data = self.stock_data [self.stock_data ['symbol'] == symbol]
        if not stock_data.empty:
            return stock_data.iloc [-1]
        return None

    def get_stock_history(self, symbol, limit=100):
        return self.stock_data [self.stock_data ['symbol'] == symbol].tail (limit)

    def get_latest_news(self, limit=5):
        return self.news_data.head (limit)

    def update(self):
        self.process_stock_data ()
        self.process_news ()


pipeline = DataPipeline ()
pipeline.update ()  # Fetches both stock and news data

# Get latest stock data
latest_tesla = pipeline.get_latest_stock_price ('TSLA')

# Get news
latest_news = pipeline.get_latest_news ()

# Get historical data
tesla_history = pipeline.get_stock_history ('TSLA')
