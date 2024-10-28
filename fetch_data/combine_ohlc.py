import pandas as pd
from typing import Optional, List
from datetime import datetime
from utils.file_utils import load_data, save_data
from fetch_data.api_config_v3 import API_CONFIG


def get_last_timestamp(filepath: str) -> Optional[datetime]:
    """
    If a current combined file exists, the last timestamp is retrieved and 
    used as a marker to perform further combining on only new data, if there 
    is no current file None is returned as a flag to create a new combined file.

    Parameters:
    - filepath (str): Path to the file containing OHLC data.

    Returns:
    - datetime or None: The maximum timestamp from the 'Open time' column if
      the file exists; otherwise, None if the file is not found.
    """
    try:
        df = load_data(filepath)
        return df['Open time'].max()
    except FileNotFoundError:
        return None


def load_new_data(filepath: str, last_timestamp: Optional[datetime]) -> pd.DataFrame:
    """
    Loads OHLC data from exchange source pickle files into a pandas dataframe,
    if there is a last_timestamp then the data from the dataframe will be filtered
    for only new data past this point.

    Parameters:
    - filepath (str): Path to the file containing OHLC data.
    - last_timestamp (datetime): Timestamp to filter data from; only data newer
      than this timestamp will be loaded.

    Returns:
    - pd.DataFrame: DataFrame containing new data starting from after last_timestamp.
    """
    df = load_data(filepath)
    if last_timestamp:
        df = df[df['Open time'] > last_timestamp]
    return df


def process_and_impute_ohlc_data_with_ma(df: pd.DataFrame, ma_window: int = 3) -> pd.DataFrame:
    """
    Generates centered moving averages of window size ma_window for each OHLC column,
    the time index for each df is expanded to generate all time indices between the
    maximum and minimum values in the dataframe and fill in the missing spaces. Where
    there are gaps, these are filled in with the moving average value and any remaining 
    NaN rows (where a moving average could not be generated) are dropped, alongside the 
    temporary moving average columns.    

    Parameters:
    - df (pd.DataFrame): OHLC data to process.
    - ma_window (int): The window size for moving average (default=3). A smaller value is
      recommended as we don't want to fill in large gaps since this would require estimating
      the values too much and make our imputed data too artificial.

    Returns:
    - pd.DataFrame: Processed and imputed DataFrame with aligned OHLC data.
    """

    # Reindex DataFrame to cover any missing time intervals
    full_time_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='min')
    df = df.reindex(full_time_index)

    # Calculate moving averages for each specified column
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        ma_col_name = f'MA_{col}'
        df[ma_col_name] = df[col].rolling(center=True, window=ma_window, min_periods=1).mean()

    # Impute missing values using moving averages
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        ma_col = f'MA_{col}'
        df[col] = df[col].fillna(df[ma_col])

    # Drop temporary moving average columns, any remaining NaNs and round the OHLC to 2 d.p.
    df.drop(columns=[f'MA_{col}' for col in ['Open', 'High', 'Low', 'Close', 'Volume']], inplace=True)
    df.dropna(inplace=True)
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].round(2)

    return df


def fix_open_close_alignment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aligns the 'Open' and 'Close' values in OHLC data to ensure the 'Open' value 
    of each candle matches the 'Close' value of the previous candle. This corrects 
    misalignment caused by exchange data errors or averaging.

    Parameters:
    - df (pd.DataFrame): OHLC data with potentially misaligned 'Open' and 'Close' values.

    Returns:
    - pd.DataFrame: DataFrame with aligned 'Open' and 'Close' values.
    """

    # Shift 'Close' values one time index ahead and set 'Open' to these values
    first_open_value = df.loc[df.index[0], 'Open']
    df_fixed = df.copy()
    df_fixed['Open'] = df_fixed['Close'].shift(1)
    df_fixed.loc[df_fixed.index[0], 'Open'] = first_open_value

    # Apply 'High/Low' fix if 'Open' has been moved outside one of them.
    df_fixed['High'] = df_fixed[['Open', 'Close', 'High', 'Low']].max(axis=1)
    df_fixed['Low'] = df_fixed[['Open', 'Close', 'High', 'Low']].min(axis=1)

    return df_fixed


def process_ohlc_data(trading_pair: str, exchange_list: List[str]) -> None:
    """
    Combine all exchange OHLC data into a single index using volume weighted averaging.
    To create a smooth index less affected by missing data volatility, small gaps are
    imputed using a moving average. All OHLC data are then volume weighted averaged per
    timestep and 'Open' values shifted to ensure they align the the previous candles 
    'Close'. In cases where the overall volume is zero across all exchanges, the volume
    weighted average is replaced with a simple mean average instead.

    Parameters:
    - trading_pair (str): The trading pair identifier (e.g., 'BTCUSD').
    - exchange_list (List[str]): List of exchanges to process for this trading pair.

    Returns:
    - None. Saves combined and processed OHLC data to a file.
    """
    combined_file = f'data/ohlc/{trading_pair}/{trading_pair}_1m_Combined_Index.pkl'
    last_timestamp = get_last_timestamp(combined_file)
    
    # Load new data for each exchange in the list
    filename_patterns = {exchange: f"data/ohlc/{trading_pair}/{trading_pair}_1m_{exchange}.pkl" for exchange in exchange_list}
    dfs = {exchange: load_new_data(filepath, last_timestamp) for exchange, filepath in filename_patterns.items()}

    # Apply 'fix_open_close_alignment' only for 'Bitstamp' exchange data
    for exchange in dfs:
        dfs[exchange].set_index('Open time', inplace=True)
        if exchange == 'Bitstamp':
            dfs[exchange] = fix_open_close_alignment(dfs[exchange])

    # Impute gaps with a moving average, ensure that High and Low remain the extrema values in these gaps
    for exchange in dfs:
        dfs[exchange] = process_and_impute_ohlc_data_with_ma(dfs[exchange], 3)
        dfs[exchange]['High'] = dfs[exchange][['Open', 'Close', 'High', 'Low']].max(axis=1)
        dfs[exchange]['Low'] = dfs[exchange][['Open', 'Close', 'High', 'Low']].min(axis=1)

    # Combine all DataFrames from different exchanges
    combined_df = pd.concat(dfs.values(), axis=1, keys=dfs.keys(), join='outer')

    # Aggregate 'Volume' and compute weighted averages for OHLC values
    final_df = pd.DataFrame(index=combined_df.index)
    final_df['Volume'] = combined_df.xs('Volume', axis=1, level=1).sum(axis=1)

    for col in ['Open', 'High', 'Low', 'Close']:
        ohlc_columns = combined_df.xs(col, axis=1, level=1)
        volume_columns = combined_df.xs('Volume', axis=1, level=1)
        weighted_avg = (ohlc_columns * volume_columns).sum(axis=1) / volume_columns.sum(axis=1)
        final_df[col] = weighted_avg

    # Impute any remaining NaN values using a simple mean across exchanges
    for col in ['Open', 'High', 'Low', 'Close']:
        nan_rows = final_df[col].isna()
        if nan_rows.any():
            simple_mean = combined_df.xs(col, axis=1, level=1).mean(axis=1)
            final_df.loc[nan_rows, col] = simple_mean[nan_rows]

    # Align 'Open' and 'Close' values and reset the index
    final_df = fix_open_close_alignment(final_df)
    final_df.reset_index(inplace=True, names='Open time')

    # Save final DataFrame to CSV and PKL formats
    csv_file = f'data/ohlc_csv/{trading_pair}/{trading_pair}_1m_Combined_Index.csv'
    save_data(final_df, csv_file, file_type='csv')

    if last_timestamp:
        existing_df = load_data(combined_file)
        final_df = pd.concat([existing_df, final_df], ignore_index=True)

    save_data(final_df, combined_file)


# Create a mapping of trading pairs to the exchanges providing data for each pair
# i.e. generate list of all exchanges that have data for a particular currency
asset_exchange_map = {}

for exchange in API_CONFIG:
    pair_keys = list(API_CONFIG[exchange]['pairs'].keys())
    for trading_pair in pair_keys:
        if trading_pair not in asset_exchange_map:
            asset_exchange_map[trading_pair] = []
        asset_exchange_map[trading_pair].append(exchange)

# Process data for each trading pair across associated exchanges
for trading_pair, exchange_list in asset_exchange_map.items():
    process_ohlc_data(trading_pair, exchange_list)
