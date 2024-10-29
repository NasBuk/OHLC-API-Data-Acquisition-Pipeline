import pandas as pd
import concurrent.futures
import dataframe_image as dfi
import requests
import json
import os
import copy
import matplotlib.pyplot as plt

from utils.file_utils import load_data, save_data
from data_analysis.diagnostics import dataframe_diagnostics
from fetch_data.api_config_v3 import API_CONFIG
from fetch_data.metadata_template import metadata_template, currency_name_map, exchange_schemas


def save_data_with_check(df_new: pd.DataFrame, log_filename: str) -> None:
    """
    Saves data to a log file, only new, unique rows are saved. This is to compare
    diagnostics across each data update to spot any issues that may occur.

    Parameters:
    - df_new (pd.DataFrame): New data to be saved.
    - log_filename (str): Name of the log file to save data in.

    Returns:
    - None
    """
    # Check for an existing log file and load, otherwise initialize a new dataframe for logs
    try:
        df_log = load_data(f'data/logs/{log_filename}.pkl')
    except FileNotFoundError:
        df_log = pd.DataFrame(columns=df_new.columns)

    # If a log file exists, generate unique row identifiers to determine whether new data is being assessed,
    # by comparing with existing row uids. If the unique id exists, no new diagnostic logs will be saved.
    if not df_log.empty:
        if 'uid' not in df_log.columns:
            df_log['uid'] = df_log.apply(lambda row: f"{row['Trading Pair']}_{row['Exchange']}_{row['Size']}", axis=1)
    else:
        df_log['uid'] = []

    # Generate unique identifiers for the new data to compare with existing uid's in previous logs
    if 'uid' not in df_new.columns:
        df_new['uid'] = df_new.apply(lambda row: f"{row['Trading Pair']}_{row['Exchange']}_{row['Size']}", axis=1)

    # Check for duplicates based on the unique identifier, if the uid for new data doesn't exist in the logs, save the row
    df_to_save = df_new[~df_new['uid'].isin(df_log['uid'])]

    # Append new records to logs if they are not duplicates
    if not df_to_save.empty:
        df_log = pd.concat([df_log, df_to_save], ignore_index=True)
        df_log = df_log.drop(columns=['uid'])  # Remove 'uid' column before saving
        save_data(df_log, f'data/logs/{log_filename}.pkl')
    else:
        print("No new records to save. All records already exist.")


def process_trading_pair(exchange: str, trading_pair: str, file_format: str) -> dict:
    """
    Processes OHLC data for a trading pair from a specific exchange, returning diagnostic metrics.

    Parameters:
    - exchange (str): Name of the exchange.
    - trading_pair (str): Trading pair identifier.
    - file_format (str): Format of the file to load ('pkl' or 'csv').

    Returns:
    - dict: Dictionary of diagnostics information for the processed trading pair.
    """
    try:
        # Pickle and csv formats are both used to storing data, both are diagnosed separately
        if file_format == 'pkl':
            df = load_data(f'data/ohlc/{trading_pair}/{trading_pair}_1m_{exchange}.pkl')
        elif file_format == 'csv':
            df = load_data(f'data/ohlc_csv/{trading_pair}/{trading_pair}_1m_{exchange}.csv', file_type='csv')

        df['Open time'] = pd.to_datetime(df['Open time'])

        # Perform diagnostics, refer to the module to see how these are performed
        diagnostics = dataframe_diagnostics(df, print_diagnostics=False, print_gaps=True, return_values=True, check_ohlc=True)

        # Return the result in dictionary form
        return {
            'File Format': file_format,
            'Trading Pair': trading_pair,
            'Exchange': exchange,
            'Data Range': f"{diagnostics['data_range'].split(' - ')[0].split()[0]} - {diagnostics['data_range'].split(' - ')[1].split()[0]}",
            'Size': diagnostics['size'],
            'Total NaNs': diagnostics['total_nans'],
            'Rows with NaNs': diagnostics['rows_with_nans'],
            'Discontinuities': diagnostics['num_discontinuities'],
            'Discontinuity Start': diagnostics['gap_start_time'],
            'Discontinuity End': diagnostics['gap_end_time'],
            'Duplicate Rows': diagnostics['duplicate_rows'],
            'Invalid Highs': diagnostics['invalid_highs'],
            'Invalid Lows': diagnostics['invalid_lows'],
        }
    except Exception as e:
        print(f"Error processing {trading_pair} on {exchange} with {file_format}: {e}")
        return None


def upload_image_to_imgur(image_path: str, client_id: str) -> str:
    """
    Uploads an image to Imgur and returns the link.

    Parameters:
    - image_path (str): Path to the image file.

    Returns:
    - str: Link to the uploaded image on Imgur.
    """
    url = "https://api.imgur.com/3/image"
    headers = {'Authorization': f'Client-ID {client_id}'}
    with open(image_path, 'rb') as image_file:
        response = requests.post(url, headers=headers, files={'image': image_file})
    return response.json()['data']['link']


def generate_metadata(trading_pair: str, imgur_url_1: str, imgur_url_2: str, output_dir: str, asset_exchange_map: dict) -> None:
    """
    Generates metadata for a dataset and saves it to a a Kaggle metadata.json file, required for interacting
    with Kaggle's API for dataset updates.

    Parameters:
    - trading_pair (str): Trading pair identifier.
    - imgur_url_1 (str): Link to the first image on Imgur.
    - imgur_url_2 (str): Link to the second image on Imgur.
    - output_dir (str): Directory to save the metadata file.
    - asset_exchange_map (dict): Mapping of trading pairs to exchanges.

    Returns:
    - None
    """
    # Dynamically get the full currency name from the mapping i.e. BTCUSD evaluates to Bitcoin
    currency_name = currency_name_map.get(trading_pair, trading_pair)

    # Make a deep copy of the metadata template to reset for each trading pair and not include previous appends
    metadata = copy.deepcopy(metadata_template)
    metadata["title"] = metadata["title"].format(currency_name=currency_name, currency_abbr=trading_pair)
    metadata["subtitle"] = metadata["subtitle"].format(currency_abbr=trading_pair)
    metadata["id"] = metadata["id"].format(currency_abbr=trading_pair)
    metadata["description"] = metadata["description"].format(currency_abbr=trading_pair, imgur_url_1=imgur_url_1, imgur_url_2=imgur_url_2)

    # Add the relevant resources based on the exchanges that provide data for this trading pair
    for exchange in asset_exchange_map[trading_pair]:
        metadata["resources"].append({
            "path": f"{trading_pair}_1m_{exchange}.csv",
            "description": f"1-minute historical data for {trading_pair} from {exchange}",
            "schema": {
                "fields": exchange_schemas.get(exchange, [])
            }
        })

    # Write to file, dynamically setting the output directory, different currencies are separated by directory
    output_file = os.path.join(output_dir, "dataset-metadata.json")
    with open(output_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Metadata for {currency_name} ({trading_pair}) saved to {output_file}")


def create_dataframe_image(df_sorted: pd.DataFrame, trading_pair: str, image_path: str) -> str:
    """
    Creates an image of a styled DataFrame that summarizes the diagnostics of all the 
    currency data from each exchange to assess at a glance the health of the data. Converted
    to an image to allow it to be uploaded to the Kaggle repository for the currency.

    Parameters:
    - df_sorted (pd.DataFrame): DataFrame to be imaged.
    - trading_pair (str): Trading pair identifier for naming.
    - image_path (str): Path to save the image.

    Returns:
    - str: File path of the saved image.
    """
    # Filter the table of all currencies to a specific pair
    df_subset = df_sorted[df_sorted['Trading Pair'] == trading_pair]

    if not df_subset.empty:
        def color_rows(row):
            background = 'black' if row.name % 2 == 0 else '#333333'
            return [f'background-color: {background}; color: white'] * len(row)

        df_styled = df_subset.style.apply(color_rows, axis=1)
        dfi.export(df_styled, image_path)
        print(f"Image saved for {trading_pair}: {image_path}")
        return image_path
    else:
        print(f"No data available for {trading_pair}")
        return None
    

def create_plot_image(df: pd.DataFrame, trading_pair: str, plot_image_path: str) -> None:
    """
    Creates and saves a line plot of the closing prices to be uploaded to the
    Kaggle repository for an at a glance depiction of the combined dataset.

    Parameters:
    - df (pd.DataFrame): DataFrame containing 'Open time' and 'Close' columns.
    - trading_pair (str): Trading pair identifier.
    - plot_image_path (str): Path to save the plot.

    Returns:
    - None
    """
    plt.figure(figsize=(10, 6))
    plt.plot(df['Open time'], df['Close'], color='blue', label='Close Price')
    plt.title(f'{trading_pair} Close Prices Over Time')
    plt.xlabel('Open Time')
    plt.ylabel('Close Price')
    plt.legend()

    plt.savefig(plot_image_path)
    plt.close()
    print(f"Plot saved for {trading_pair} at {plot_image_path}")


def main() -> None:
    """
    Main function to process trading pairs from various exchanges, generate diagnostics, and save metadata.

    Returns:
    - None
    """
    client_id = client_id               # Replace with your API client id
    exchanges = list(API_CONFIG.keys())
    exchanges.append('Combined_Index')
    results_pkl = []
    results_csv = []

    # Use ThreadPoolExecutor for concurrency
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        # Submit tasks for each exchange and trading pair for both pkl and csv source files
        for exchange in exchanges:
            if exchange == 'Combined_Index':
                pair_keys = list(API_CONFIG['Binance']['pairs'].keys())
            else:
                pair_keys = list(API_CONFIG[exchange]['pairs'].keys())

            for trading_pair in pair_keys:
                futures.append(executor.submit(process_trading_pair, exchange, trading_pair, 'pkl'))
                futures.append(executor.submit(process_trading_pair, exchange, trading_pair, 'csv'))

        # Collect results as they are completed
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                if result['File Format'] == 'pkl':
                    results_pkl.append(result)
                elif result['File Format'] == 'csv':
                    results_csv.append(result)

    # Create DataFrames from the results
    df_pkl = pd.DataFrame(results_pkl)
    df_csv = pd.DataFrame(results_csv)

    # Sort by 'Exchange' and 'Trading Pair', then drop 'File Format' and reset index for presenting the summary tables
    df_pkl_sorted = df_pkl.sort_values(by=['Exchange', 'Trading Pair']).drop(columns=['File Format']).reset_index(drop=True)
    df_csv_sorted = df_csv.sort_values(by=['Exchange', 'Trading Pair']).drop(columns=['File Format']).reset_index(drop=True)

    # Generate a dictionary of which exchange provides data for which currencies
    asset_exchange_map = {}
    for exchange in API_CONFIG:
        pair_keys = list(API_CONFIG[exchange]['pairs'].keys())
        for trading_pair in pair_keys:
            if trading_pair not in asset_exchange_map:
                asset_exchange_map[trading_pair] = []
            asset_exchange_map[trading_pair].append(exchange)

    # Generate images for each trading pair by creating subsets from the aggregated dataframe
    # Binance is used to generate the pair_keys (i.e. BTCUSD) because it supports all pairs.
    # Metadata for each currency pair is generated here, including images, links and diagnostic summaries
    pair_keys = list(API_CONFIG['Binance']['pairs'].keys())
    for trading_pair in pair_keys:
        metadata_dir = f"/home/hooch/trading/data/ohlc_csv/{trading_pair}"
        dataframe_image_path = f"/home/hooch/trading/data/images/{trading_pair}_dataframe.png"
        plot_image_path = f"/home/hooch/trading/data/images/{trading_pair}_plot.png"

        df_subset = df_pkl_sorted[df_pkl_sorted['Trading Pair'] == trading_pair]
        df_subset = df_subset.reset_index(drop=True)
        df = load_data(f'data/ohlc/{trading_pair}/{trading_pair}_1m_Combined_Index.pkl')

        create_dataframe_image(df_subset, trading_pair, dataframe_image_path)
        create_plot_image(df, trading_pair, plot_image_path)

        dataframe_image_url = upload_image_to_imgur(dataframe_image_path, client_id)
        close_plot_url = upload_image_to_imgur(plot_image_path, client_id)

        generate_metadata(trading_pair, dataframe_image_url, close_plot_url, metadata_dir, asset_exchange_map)

    save_data_with_check(df_pkl_sorted, 'pkl_log')
    save_data_with_check(df_csv_sorted, 'csv_log')

if __name__ == "__main__":
    main()