import pandas as pd
from typing import Dict, List, Optional, Union

def dataframe_diagnostics(
    df: pd.DataFrame,
    stage: str = "Initial",
    print_gaps: bool = False,
    print_diagnostics: bool = True,
    check_ohlc: bool = False,
    return_values: bool = True
) -> Optional[Dict[str, Union[int, List[str], Optional[str], List[Dict[str, Union[int, str, pd.Timedelta]]]]]]:
    """
    Perform diagnostics on a DataFrame to check for data issues, gaps, and NaN values. Multi-purpose function
    that can be used to print results output, check for OHLC integrity, return diagnostic results for further
    processing, displaying or logging.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing OHLC data to be diagnosed.
    - stage (str): Label for the diagnostics stage (e.g., 'Initial' or 'Post-Imputation').
    - print_gaps (bool): Whether to print information about detected time gaps.
    - print_diagnostics (bool): Whether to print detailed diagnostics information.
    - check_ohlc (bool): Whether to run an integrity check on OHLC values.
    - return_values (bool): Whether to return diagnostic results as a dictionary.

    Returns:
    - Optional[Dict[str, Union[int, List[str], Optional[str], List[Dict[str, Union[int, str, pd.Timedelta]]]]]]:
      Dictionary with diagnostic metrics if `return_values` is True, otherwise None.
    """
    size = len(df)
    total_nans = df.isna().values.sum()                          # Total NaN's overall
    nan_cols = df.columns[df.isna().any()].tolist()              # Columns with any NaN values
    rows_with_nans = df.isna().any(axis=1).sum()                 # Total rows with any NaN values

    # Find all rows in which the gaps between subsequent rows is greater than the expected difference
    discontinuities = []
    expected_diff = pd.Timedelta(minutes=1) # Currently for 1m data
    time_diffs = df['Open time'].diff().dropna()
    discontinuities = time_diffs[time_diffs != expected_diff].index.tolist()

    # Identify the start and end of each gap, the gap size and indices of gaps
    if print_gaps:
        gap_details = [
            {
                'Start Index': idx - 1,
                'End Index': idx,
                'Start Time': df['Open time'].iloc[idx - 1],
                'End Time': df['Open time'].iloc[idx],
                'Gap Size': df['Open time'].iloc[idx] - df['Open time'].iloc[idx - 1]
            }
            for idx in discontinuities
        ]

    # Filter the dataframe for duplicated rows and count the number of duplicates
    duplicate_rows = df[df.duplicated(keep=False)]
    num_duplicate_rows = len(duplicate_rows)

    # Gaps locations can be returned for various processes: plotting, making selective calls to fill the gaps etc.
    gap_start = f"{gap_details[0]['Start Index']}, {gap_details[0]['Start Time']}" if gap_details else None
    gap_end = f"{gap_details[-1]['End Index']}, {gap_details[-1]['End Time']}" if gap_details else None
    data_range = f"{df['Open time'].iloc[0]} - {df['Open time'].iloc[-1]}"

    # All results will be printed to terminal in formatted output if print_diagnostics is True
    if print_diagnostics:
        print(f"\n--- {stage} Diagnostics ---")
        print(f"Start 'Open time': {df['Open time'].iloc[0]}, End 'Open time': {df['Open time'].iloc[-1]}")
        print(f"Size: {size} rows")
        print(f"Total NaNs: {total_nans}")
        print(f"Columns with NaNs: {nan_cols if nan_cols else 'None'}")
        print(f"Rows with NaNs: {rows_with_nans}")
        if rows_with_nans > 0:
            last_nan_row = df[df.isna().any(axis=1)].iloc[-1]
            last_nan_index = df[df.isna().any(axis=1)].index[-1]
            print(f"Final NaN row index: {last_nan_index}, 'Open time': {last_nan_row['Open time']}")
        print(f"Number of duplicate rows: {num_duplicate_rows}")
        print(f"Number of discontinuities in 'Open time': {len(discontinuities)}")
        if print_gaps:
            first_gap_start = gap_details[0]['Start Time']
            first_gap_index = gap_details[0]['Start Index']
            last_gap_end = gap_details[-1]['End Time']
            last_gap_index = gap_details[-1]['End Index']
            print(f"Discontinuities range from index {first_gap_index} ('Open time': {first_gap_start}) to "
                  f"index {last_gap_index} ('Open time': {last_gap_end}).")

    # Selectively print information about the gaps, sometimes there are a lot so this output can be redacted
    if print_gaps and print_diagnostics:
        print(f"\nDetected {len(gap_details)} data gaps:")
        for i, gap in enumerate(gap_details):
            print(f"Gap {i+1}: Start Index {gap['Start Index']}, End Index {gap['End Index']}, "
                  f"Start Time {gap['Start Time']}, End Time {gap['End Time']}, Gap Size: {gap['Gap Size']}")

    if num_duplicate_rows > 0 and print_diagnostics:
        print("\nDetected duplicate rows:")
        print(duplicate_rows)

    # Perform OHLC integrity check if required
    ohlc_results = None
    if check_ohlc:
        ohlc_results = ohlc_integrity_check(df)
        if print_diagnostics:
            print("\n--- OHLC Integrity Check ---")
            print(f"Invalid 'High' values: {ohlc_results['invalid_high_count']} rows")
            print(f"Invalid 'Low' values: {ohlc_results['invalid_low_count']} rows")
   
    if return_values:
        return {
            'size': size,
            'total_nans': total_nans,
            'nan_cols': nan_cols,
            'rows_with_nans': rows_with_nans,
            'num_discontinuities': len(discontinuities),
            'first_discontinuity_index': discontinuities[0] if discontinuities else None,
            'last_discontinuity_index': discontinuities[-1] if discontinuities else None,
            'gap_start_time': gap_start,
            'gap_end_time': gap_end,
            'gaps': gap_details if gap_details else None,
            'data_range': data_range,
            'duplicate_rows': num_duplicate_rows,
            'invalid_highs': ohlc_results['invalid_high_count'] if ohlc_results else None,
            'invalid_lows': ohlc_results['invalid_low_count'] if ohlc_results else None
        }


def ohlc_integrity_check(df: pd.DataFrame) -> Dict[str, Union[int, pd.DataFrame]]:
    """
    Verify the integrity of OHLC data, ensuring that 'High' >= 'Open', 'Close', 'Low' 
    and 'Low' <= 'Open', 'Close', 'High'.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing OHLC data.

    Returns:
    - dict: Dictionary with counts and rows of invalid 'High' and 'Low' values.
    """
    invalid_high = df[df['High'] < df[['Open', 'Close', 'Low']].max(axis=1)]
    
    # Check if Low <= Open, Close, High
    invalid_low = df[df['Low'] > df[['Open', 'Close', 'High']].min(axis=1)]
    
    return {
        'invalid_high_count': len(invalid_high),
        'invalid_low_count': len(invalid_low),
        'invalid_high_rows': invalid_high,
        'invalid_low_rows': invalid_low
    }