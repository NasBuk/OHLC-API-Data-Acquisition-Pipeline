from pandas import to_datetime

from utils.file_utils import load_data, save_data
from fetch_data.api_config_v3 import API_CONFIG


def resample_data(df, period, exchange):
    """Resample the dataframe according to the given period."""
    # Define the aggregation rules based on the exchange
    aggregation_rules = {
        'Binance': {
            'Open time': 'first',
            'Close time': 'last',
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum',
            'Quote asset volume': 'sum',
            'Number of trades': 'sum',
            'Taker buy base asset volume': 'sum',
            'Taker buy quote asset volume': 'sum',
            'Ignore': 'sum'
        },
        'Coinbase': {
            'Open time': 'first',
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        },
        'OKX': {
            'Open time': 'first',
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum',
            'Volume (Currency)': 'sum',
            'Volume (Quote)': 'sum',
            'Confirm': 'sum'
        },
        'Combined_Index': {
            'Open time': 'first',
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        },
        'Bitfinex': {
            'Open time': 'first',
            'Open': 'first',
            'Close': 'last',
            'High': 'max',
            'Low': 'min',
            'Volume': 'sum'
        },
        'KuCoin': {
            'Open time': 'first',
            'Open': 'first',
            'Close': 'last',
            'High': 'max',
            'Low': 'min',
            'Volume': 'sum',
            'Amount': 'sum'
        },
        'BitMEX': {
            'Open time': 'first',
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        },
        'Bitstamp': {
            'Open time': 'first',
            'Open': 'first',
            'Close': 'last',
            'High': 'max',
            'Low': 'min',
            'Volume': 'sum'
        }
    }

    # Resample using the appropriate aggregation rules for the exchange
    df_resampled = df.resample(period).agg(aggregation_rules[exchange])

    # Remove rows with NaT or NaN values
    df_resampled.dropna(inplace=True)

    # Reset the index
    df_resampled.reset_index(drop=True, inplace=True)
    return df_resampled


# Main function to automate resampling
def main():
    asset_exchange_map = {}

    for exchange in API_CONFIG:
        pair_keys = list(API_CONFIG[exchange]['pairs'].keys())
        for ticker in pair_keys:
            if ticker not in asset_exchange_map:
                asset_exchange_map[ticker] = []
            asset_exchange_map[ticker].append(exchange)

    # Append 'Combined_Index' to every key in asset_exchange_map
    for ticker in asset_exchange_map:
        asset_exchange_map[ticker].append('Combined_Index')


    # Iterate over each trading pair and its exchanges
    for ticker, exchanges in asset_exchange_map.items():
        for exchange in exchanges:
            # Define the resample periods and corresponding file names
            resample_periods = {
                #'15min': f'{ticker}_15m_{exchange}',
                #'30min': f'{ticker}_30m_{exchange}',
                '1h': f'{ticker}_1h_{exchange}',
                #'4h': f'{ticker}_4h_{exchange}',
                #'12h': f'{ticker}_12h_{exchange}',
                '1d': f'{ticker}_1d_{exchange}'
                # '1W': f'{ticker}_1w_{exchange}',
                # '1ME': f'{ticker}_1Mo_{exchange}'
            }
            # Load the data for the specific ticker and exchange
            try:
                df = load_data(f'data/ohlc/{ticker}/1m/{ticker}_1m_{exchange}.pkl')
                df['resample_time'] = to_datetime(df['Open time'])
                df.set_index('resample_time', inplace=True)
                
                # Resample and save data for each period
                for period, file_template in resample_periods.items():
                    df_resampled = resample_data(df, period, exchange)
                    file_name = file_template.format(ticker=ticker, exchange=exchange)
                    save_data(df_resampled, f'data/ohlc/{ticker}/{period}/{file_name}.pkl')
                    save_data(df_resampled, f'data/ohlc_csv/{ticker}/{period}/{file_name}.csv', file_type='csv', append_if_exists=False)
                    print(f"Resampled data saved for {ticker} on {exchange} at {period} interval.")
            
            except FileNotFoundError:
                print(f"Data file for {ticker} on {exchange} not found. Skipping.")

if __name__ == "__main__":
    main()