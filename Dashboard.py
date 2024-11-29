import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries
import requests
from Config import *


class TechStocksPipeline:
    def __init__(self, api_key):
        self.api_key = api_key
        self.ts = TimeSeries (key=api_key)
        self.tech_symbols = STOCK_SYMBOLS

    def get_stock_data(self, symbol):
        try:
            data, meta_data = self.ts.get_intraday (symbol, interval='1min', outputsize='compact')
            df = pd.DataFrame.from_dict (data, orient='index')
            df.index = pd.to_datetime (df.index)
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            return df.sort_index ()
        except Exception as e:
            print (f"Error fetching stock data: {e}")
            return pd.DataFrame ()


class NewsStream:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"

    def get_news(self, symbol):
        params = {
            'q': symbol,
            'apiKey': self.api_key,
            'sortBy': 'publishedAt',
            'pageSize': 5
        }
        try:
            response = requests.get (self.base_url, params=params)
            return response.json ().get ('articles', [])
        except Exception as e:
            print (f"Error fetching news: {e}")
            return []


class Dashboard:
    def __init__(self):
        self.app = dash.Dash (__name__,
                              external_stylesheets=[
                                  'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'])
        self.pipeline = TechStocksPipeline (ALPHA_VANTAGE_API_KEY)
        self.news_stream = NewsStream (NEWS_API_KEY)
        self.setup_layout ()
        self.setup_callbacks ()

    def setup_layout(self):
        self.app.layout = html.Div ([
            html.Div ([
                html.H1 ('Nautilus Horizon', className='text-4xl font-bold mb-2'),
                html.P ('Market Intelligence Dashboard', className='text-xl text-gray-600')
            ], className='p-6 bg-white shadow-lg mb-6'),

            html.Div ([
                html.Div ([
                    html.Div ([
                        dcc.Dropdown (
                            id='stock-selector',
                            options=[{'label': s, 'value': s} for s in STOCK_SYMBOLS],
                            value=STOCK_SYMBOLS [0],
                            className='mb-4'
                        ),
                        dcc.Graph (id='price-chart', className='mb-4'),
                        dcc.Graph (id='volume-chart')
                    ], className='bg-white rounded-lg shadow-lg p-4')
                ], className='w-2/3 pr-4'),

                html.Div ([
                    html.Div ([
                        html.H3 ('Market Statistics', className='text-2xl font-bold mb-4'),
                        html.Div (id='market-stats', className='mb-6'),
                        html.H3 ('Latest News', className='text-2xl font-bold mb-4'),
                        html.Div (id='news-feed', className='h-96 overflow-y-auto')
                    ], className='bg-white rounded-lg shadow-lg p-4')
                ], className='w-1/3')
            ], className='container mx-auto px-4 flex'),

            dcc.Interval (
                id='update-interval',
                interval=60 * 1000,
                n_intervals=0
            )
        ], className='bg-gray-100 min-h-screen')

    def setup_callbacks(self):
        @self.app.callback (
            [Output ('price-chart', 'figure'),
             Output ('volume-chart', 'figure'),
             Output ('market-stats', 'children'),
             Output ('news-feed', 'children')],
            [Input ('update-interval', 'n_intervals'),
             Input ('stock-selector', 'value')]
        )
        def update_dashboard(n, symbol):
            try:
                df = self.pipeline.get_stock_data (symbol)
                news = self.news_stream.get_news (symbol)

                if df.empty:
                    return self.create_empty_charts (), self.create_empty_charts (), \
                        self.create_empty_stats (), self.create_empty_news ()

                price_chart = {
                    'data': [{
                        'x': df.index,
                        'y': df ['close'],
                        'type': 'scatter',
                        'mode': 'lines',
                        'name': symbol,
                        'line': {'color': '#2563eb', 'width': 2}
                    }],
                    'layout': self.create_chart_layout ('Price History', 'Price ($)')
                }

                volume_chart = {
                    'data': [{
                        'x': df.index,
                        'y': df ['volume'],
                        'type': 'bar',
                        'name': 'Volume',
                        'marker': {'color': '#93c5fd'}
                    }],
                    'layout': self.create_chart_layout ('Trading Volume', 'Volume')
                }

                return price_chart, volume_chart, self.create_market_stats (df), self.create_news_feed (news)

            except Exception as e:
                print (f"Error updating dashboard: {e}")
                return self.create_empty_charts (), self.create_empty_charts (), \
                    self.create_empty_stats (), self.create_empty_news ()

    def create_chart_layout(self, title, yaxis_title):
        return {
            'title': title,
            'height': 400,
            'template': 'plotly_white',
            'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40},
            'yaxis': {'title': yaxis_title},
            'xaxis': {'title': 'Time'}
        }

    def create_market_stats(self, df):
        try:
            current_price = float (df ['close'].iloc [-1])
            open_price = float (df ['open'].iloc [0])
            volume = int (df ['volume'].iloc [-1])
            high = float (df ['high'].max ())
            low = float (df ['low'].min ())

            daily_change = ((current_price - open_price) / open_price * 100)

            stats = [
                ('Current Price', "${:.2f}".format (current_price)),
                ('Daily Change', "{:.2f}%".format (daily_change)),
                ('Volume', "{:,d}".format (volume)),
                ('High', "${:.2f}".format (high)),
                ('Low', "${:.2f}".format (low))
            ]

            return html.Div ([
                html.Div ([
                    html.Span (label, className='font-bold'),
                    html.Span (value)
                ], className='flex justify-between py-2 border-b border-gray-200')
                for label, value in stats
            ])
        except Exception as e:
            print (f"Error creating market stats: {e}")
            return self.create_empty_stats ()

    def create_news_feed(self, news_data):
        return html.Div ([
            html.Div ([
                html.H4 (article ['title'], className='font-bold text-lg mb-2'),
                html.P (article ['description'], className='text-sm text-gray-600'),
                html.Div (
                    datetime.strptime (article ['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                    .strftime ('%Y-%m-%d %H:%M'),
                    className='text-xs text-gray-500 mt-2'
                ),
                html.Hr (className='my-4')
            ], className='mb-4')
            for article in news_data
        ])

    def create_empty_charts(self):
        return {'data': [], 'layout': self.create_chart_layout ('No Data Available', '')}

    def create_empty_stats(self):
        return html.Div ("No data available", className='text-gray-500')

    def create_empty_news(self):
        return html.Div ("No news available", className='text-gray-500')

    def run_server(self, debug=True, port=8050):
        self.app.run_server (debug=debug, port=port)


if __name__ == '__main__':
    dashboard = Dashboard ()
    dashboard.run_server ()
