import yfinance as yf
import pandas as pd
from prefect import flow,task
from prophet import Prophet


#Fetch data
@task(name = "Extracting data",
      retries = 2,
      retry_delay_seconds = 3)

def extract_price(tickers:str, period:str,interval:str) -> pd.DataFrame:
    data = yf.download(
    tickers = tickers,
    period = period,
    interval = interval )
    return data

#Transformation
@task
def tranformation(data: pd.DataFrame) -> pd.DataFrame:
    data['Datetime'] = pd.to_datetime(data.Datetime)
    data['Datetime'] = data['Datetime'].dt.tz_localize(None)
    data = pd.DataFrame({'y':data['Close'], 'ds': data['Datetime']})
    return data

# Store
@task(name = 'Saving data as csv ')
def loading(data: pd.DataFrame, path: str) -> None:
    data.to_csv(path_or_buf= path,index=True)



#Pedict
@task(name ='Prophet prediction')
def forecaste(path1: str, path2: str) ->None:
    df = pd.read_csv(path1)
    prophet_model = Prophet()
    prophet_model.fit(df)
    forecast_date = prophet_model.make_future_dataframe(periods=5,freq='5min')
    prophet_predict = prophet_model.predict(forecast_date)
    prophet_predict.to_csv(path2)



#prefect flow
@flow
def main_flow(tickers = 'BTC-USD',
              period = '3h',
              interval = '5m',
              data_path="./Data/bitcoin_price.csv",
              forecaste_path = "./Data/forecast_price.csv"):
    
    print('Extracting')
    df = extract_price(tickers = tickers,
                       period = period,
                       interval = interval)

    print('Transforming')
    df = tranformation(df)

    print('Storing')
    loading(data = df,path=data_path)

    print('Forecasting')
    forecaste(path1=data_path,path2=forecaste_path)


#main
if __name__== "__main__":
    main_flow(tickers = 'BTC-USD',
              period = '3h',
              interval = '5m',
              data_path="./Data/bitcoin_price.csv",
              forecaste_path = "./Data/forecast_price.csv")