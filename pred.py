import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
import datetime as dt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings("ignore")

def predict_1_hour():
    start_date = dt.datetime.now() - dt.timedelta(days=90)
    end_date = dt.datetime.now()
    # Fetch historical BTC price data using yfinance
    btc_data = yf.Ticker('BTC-USD').history(start=start_date, end=end_date, interval='1h')
    # Prepare the dataset for training
    btc_data.reset_index(inplace=True)
    btc_data['Date'] = btc_data['Datetime']
    btc_data.drop(['Datetime'], axis=1, inplace=True)
    btc_data.set_index('Date', inplace=True)
    check_price = btc_data[-2:-1]["Close"][0]
    # Feature Engineering
    btc_data['Hour'] = btc_data.index.hour
    btc_data['DayOfWeek'] = btc_data.index.dayofweek
    btc_data['DayOfYear'] = btc_data.index.dayofyear
    btc_data['Month'] = btc_data.index.month
    btc_data['ClosePriceNextHour'] = btc_data['Close'].shift(-1)
    # Calculate technical indicators using pandas_ta library
    btc_data.ta.sma(length=10, append=True) # Simple Moving Average (SMA) with a window of 10 periods
    btc_data.ta.macd(append=True)
    btc_data.ta.vwap(append=True)
    btc_data.ta.rsi(length=14, append=True) # Relative Strength Index (RSI) with a window of 14 periods
    btc_data.ta.bbands(length=20, append=True) # Bollinger Bands (BB) with a window of 20 periods

    # Drop rows with NaN (last row, as we shifted)
    btc_data.dropna(inplace=True)
    # Split data into features (X) and target (y)
    X = btc_data[['Hour', 'DayOfWeek', 'DayOfYear', 'Month', 'Close', 'SMA_10',
                'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9', 'VWAP_D',
                'RSI_14', 'BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0']]
    y = btc_data['ClosePriceNextHour']
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # Initialize and fit the Gradient Boosting Regressor
    gb_regressor = GradientBoostingRegressor()
    gb_regressor.fit(X_train, y_train)
    # Make predictions for the next hour
    last_data_point = btc_data.iloc[-1]
    next_hour_date = last_data_point.name + dt.timedelta(hours=1)
    next_hour_features = [[next_hour_date.hour, next_hour_date.dayofweek, next_hour_date.dayofyear, next_hour_date.month,
                        last_data_point['Close'], last_data_point['SMA_10'],
                        last_data_point['MACD_12_26_9'], last_data_point['MACDh_12_26_9'], last_data_point['MACDs_12_26_9'],
                        last_data_point['VWAP_D'], last_data_point['RSI_14'], last_data_point['BBL_20_2.0'],
                        last_data_point['BBM_20_2.0'], last_data_point['BBU_20_2.0']]]
    predicted_price = gb_regressor.predict(next_hour_features)
    # Evaluate the model
    y_pred = gb_regressor.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    if rmse <= 200:
        return f"Hourly close price prediction: {round(predicted_price[0], 2)}$\nLast closing price: {round(check_price, 2)}$\nPredicted ratio diff. from the last closing price: {round((predicted_price[0] / check_price ) - 1, 3)}" 
    else:
        return "RMSE"