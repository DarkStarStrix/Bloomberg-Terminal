from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
from datetime import datetime
import time
from Config import ALPHA_VANTAGE_API_KEY


class TechStocksPipeline:
    def __init__(self, api_key):
        self.ts = TimeSeries (key=api_key)
        self.tech_symbols = [
            "AAPL",  # Apple
            "MSFT",  # Microsoft
            "GOOGL",  # Google
            "AMZN",  # Amazon
            "META",  # Meta
            "NVDA",  # NVIDIA
            "TSLA"  # Tesla
        ]
        self.data_cache = {}

    async def get_stock_data(self, symbol):
        try:
            data, meta_data = self.ts.get_intraday (symbol, interval='1min', outputsize='compact')
            df = pd.DataFrame.from_dict (data, orient='index')
            df.index = pd.to_datetime (df.index)
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df ['symbol'] = symbol
            self.data_cache [symbol] = df.sort_index ()
            # Rate limiting
            time.sleep (12)  # Alpha Vantage free tier limit
            return df
        except Exception as e:
            print (f"Error fetching data for {symbol}: {str (e)}")
            return None

    async def update_all_stocks(self):
        tasks = []
        for symbol in self.tech_symbols:
            task = asyncio.create_task (self.get_stock_data (symbol))
            tasks.append (task)
        await asyncio.gather (*tasks)

    def plot_tech_stocks(self):
        fig = make_subplots (
            rows=2, cols=1,
            subplot_titles=('Stock Prices', 'Trading Volume'),
            vertical_spacing=0.2,
            row_heights=[0.7, 0.3]
        )

        for symbol in self.tech_symbols:
            if symbol in self.data_cache:
                df = self.data_cache [symbol]
                # Price plot
                fig.add_trace (
                    go.Scatter (
                        x=df.index,
                        y=df ['close'],
                        name=f"{symbol} Price",
                        mode='lines'
                    ),
                    row=1, col=1
                )
                # Volume plot
                fig.add_trace (
                    go.Bar (
                        x=df.index,
                        y=df ['volume'],
                        name=f"{symbol} Volume",
                        opacity=0.7
                    ),
                    row=2, col=1
                )

        fig.update_layout (
            title='Tech Stocks Real-Time Data',
            height=900,
            xaxis2_title='Time',
            yaxis_title='Price ($)',
            yaxis2_title='Volume'
        )

        return fig

    def get_market_summary(self):
        summary = {}
        for symbol in self.tech_symbols:
            if symbol in self.data_cache:
                df = self.data_cache [symbol]
                latest = df.iloc [-1]
                earliest = df.iloc [0]
                price_change = ((latest ['close'] - earliest ['close']) / earliest ['close']) * 100

                summary [symbol] = {
                    'current_price': latest ['close'],
                    'price_change_pct': price_change,
                    'volume': latest ['volume'],
                    'high': df ['high'].max (),
                    'low': df ['low'].min ()
                }
        return summary


async def main():
    pipeline = TechStocksPipeline (ALPHA_VANTAGE_API_KEY)
    await pipeline.update_all_stocks ()

    # Plot stocks
    fig = pipeline.plot_tech_stocks ()
    fig.show ()

    # Print market summary
    summary = pipeline.get_market_summary ()
    for symbol, data in summary.items ():
        print (f"\n{symbol} Summary:")
        for metric, value in data.items ():
            print (f"{metric}: {value:.2f}")


if __name__ == "__main__":
    asyncio.run (main ())
