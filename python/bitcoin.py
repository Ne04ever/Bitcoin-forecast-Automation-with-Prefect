import yfinance as yf
import pandas as pd

data = yf.download(
    tickers = 'BTC-USD',
    period = '3h',
    interval = '5m',
)

pd.DataFrame(data).to_csv("./Data/bitcoin.csv")