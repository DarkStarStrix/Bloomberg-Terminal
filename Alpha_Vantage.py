from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from Config import ALPHA_VANTAGE_API_KEY


def get_stock_data(symbol="IBM"):
    ts = TimeSeries (key=ALPHA_VANTAGE_API_KEY)
    data, meta_data = ts.get_intraday (symbol, interval='1min', outputsize='compact')

    # Convert to DataFrame
    df = pd.DataFrame.from_dict (data, orient='index')
    df.index = pd.to_datetime (df.index)
    df.columns = ['open', 'high', 'low', 'close', 'volume']

    return df.sort_index ()


if __name__ == "__main__":
    df = get_stock_data ()
    print (df.head ())
