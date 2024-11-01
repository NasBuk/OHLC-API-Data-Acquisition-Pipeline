"""
Main script for fetching OHLC (Open, High, Low, Close) data from various cryptocurrency exchanges as defined in the API_CONFIG configuration file.

### Code Flow

1. **Setup and Configuration**:
    - Define necessary imports, logging, constants for rate-limiting and retries, and load exchange-specific configurations from `API_CONFIG`.
    - Set up a `DataFetchConfig` class that standardizes API parameters for each exchange based on configurations, facilitating easier, consistent access to API details.

2. **Initialize Data**:
    - The `initialize_data` function loads existing data for a trading pair (if available) or creates a new DataFrame.
    - This function also determines the correct start and end times for data fetching, which ensures we avoid redundant downloads.

3. **Fetch Data in Batches**:
    - Using `fetch_klines`, the script retrieves data in batches based on exchange limits.
    - The function handles rate-limiting, retries, and error handling for each request, making adjustments if an API responds with a 429 status (rate-limit hit).
    - After each successful fetch, the `advance_start_datetime` function updates the start time to prevent re-fetching old data.

4. **Data Integrity Checks**:
    - After fetching each batch, `check_data_integrity` verifies data consistency (batch size, time gaps, and `High/Low` hierarchy).
    - If any issues are detected, the user is prompted to retry, skip, or continue the batch.

5. **Saving Data**:
    - The `save_new_data` function periodically saves fetched data to prevent data loss during long-running jobs.
    - Data is saved as a pickle (.pkl) file at regular intervals and finally as both .pkl and .csv when downloading completes.

6. **Concurrency and Execution**:
    - Using `process_exchange` for each exchange, the script concurrently fetches data for multiple trading pairs.
    - In the `main` function, `ThreadPoolExecutor` allows concurrent fetching from all configured exchanges, ensuring maximum efficiency.

This script is designed to:
- Fetch historical data from multiple exchanges and save as a pickle file in
  a sibling directory '/data/ohlc/' which will be created if it doesn't exist.
- Handle rate-limiting and retries when making API requests.
- Save the data in batches, ensuring progress is not lost during long-running jobs.
- Use a configurable API_CONFIG file to support multiple exchanges.

### Key Features:
- Data fetching for each exchange is driven by the configuration in API_CONFIG.
- Each exchange is processed independently with respect to its API parameters.
- Handles data saving in intervals to prevent data loss in case of interruptions.

The data downloaded is saved as pandas DataFrames in .pkl files, and the 
script is designed to be extensible for other exchanges by modifying API_CONFIG.
"""

import logging
import random
import pandas as pd
import requests
import concurrent.futures

from tqdm import tqdm
from time import sleep, time
from typing import Tuple, List, Dict, Optional
from datetime import datetime, timezone, timedelta
from utils.file_utils import load_data, save_data
from fetch_data.api_config_v3 import API_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


TIME_BEFORE_SAVE = 300               # Time interval (in seconds) before saving
MAX_RETRIES = 5                      # Amount of times to retry a failed request
RETRY_DELAY = 5                      # The base amount of times in seconds before retry, exponenential with subsequent retries


class DataFetchConfig:
    def __init__(self, trading_pair: str, exchange: str, timeframe: str, api_config: Dict):
        """
        Initialize the DataFetchConfig with necessary details for fetching data, each
        exchange has it's own specifics for fetching data which are initialized here
        for ease of access when that exchange is being called. The specifics are stored
        externally in API_CONFIG.py
        """


def initialize_data(filename: str, start_date: str, exchange: str) -> Tuple[pd.DataFrame, datetime, datetime, pd.DataFrame]:
    """
    Initialize or load existing data from a file for the given exchange. If the 
    file doesn't exist, it sets up a new DataFrame and determines the starting 
    and ending dates for fetching data, defaulting to the start date in API_CONFIG.
    """


def calculate_total_requests(start_datetime: datetime, end_datetime: datetime, candles_per_request: int) -> int:
    # Calculates the total requests to be made by determining the total amount of minutes between
    # the start and the end datetime and dividing that by the candle request limit for the exchange.


def print_parameters(symbol: str, start_datetime: datetime, end_datetime: datetime, filename: str, timeframe: str) -> None:
    # Print the parameters used for data fetching, including the symbol, interval, start and end times, 
    # and output file location.


def handle_rate_limiting(response: requests.Response, retry_count: int, max_retries: int, retry_delay: int) -> int:
    """
    Handle rate-limiting by checking for a 'Retry-After' response header and sleeping for 
    the specified time. If the max retries are exceeded, raise an exception.
    """


def fetch_klines(config: DataFetchConfig, start_datetime: datetime, end_datetime: datetime, mock: bool = False) -> List:
    """
    Fetch historical OHLC data (klines) from the specified exchange's API. This function handles 
    formatting a request to the exchange, fetching the URL from API_CONFIG, formatting the header 
    parameters using 'construct_params' and dealing with retries in case of request errors. It also 
    parses the variable content from exchange returns and formats the kline data into a standardized 
    list to make the return exchange agnostic. "construct_params" is a lambda function in the API_CONFIG
    please consult the config to see exchange specific logic for constructing start/end_datetime.
    """


def save_new_data(df: pd.DataFrame, new_df: pd.DataFrame, filename: str, exchange: str, final_save: bool = False, initial_start_datetime: datetime = None) -> pd.DataFrame:
    """
    Inserts newly fetched DataFrame data into the existing DataFrame, concatenates with existing data, and saves to file.
    DataFrame is returned to maintain current state for next update.
    """


def convert_data_types(df: pd.DataFrame, exchange: str) -> pd.DataFrame: 
    """
    Convert timestamp columns to datetime and everything else to float.
    """


def check_data_integrity(new_df: pd.DataFrame, batch_df: pd.DataFrame, limit) -> Tuple[bool, List[str], pd.DataFrame]:
    """
    Function to check the integrity of the data after each batch fetch.
    It checks for:
    - Number of klines matching the exchange's limit
    - Gaps between batches
    - HL integrity (high/low values)
    - NaN values
    - Duplicate rows after concatenation
    """


def advance_start_datetime(klines: List, start_datetime: datetime, config: DataFetchConfig) -> Optional[datetime]:
    """
    Function to advance the start_datetime and check for "stuck" timestamp issues.
    """


def download_data(config: DataFetchConfig, start_time=None, end_time=None, use_progress_bar: bool = False, audit_data: bool = False) -> pd.DataFrame:
    """
    Main function for downloading historical data for a specific trading pair 
    from an exchange. Fetches data in batches, handles rate-limiting, and 
    saves progress periodically. Moves the start datetime forward 1m from the 
    last timestamp received in the last request and defaults the end datetime 
    to the current moment the script was started at. The exchanges currently 
    being used will return their candle limit from the start datetime being 
    requested, meaning only the start datetime must update each loop i.e. if
    the start datetime is 01/01/2024 00:00 and the limit is 60 candles, the 
    return will be 60 1m candles and the loop updates the start datetime to
    01/01/2024 01:00 repeating until we hit the end datetime i.e. current moment.
    """


def process_exchange(exchange: str, timeframe: str):
    """
    Process data for a specific exchange by iterating over trading pairs,
    filling gaps, and downloading the data.
    """


def main():
    """
    Initializes concurrent data fetching for all exchanges as defined in API_CONFIG.
    """