import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from scipy.stats import skew, kurtosis
import numpy as np
from typing import Dict, List, Optional, Union

def dataframe_diagnostics(
    df: pd.DataFrame,
    stage: str = "Initial",
    print_gaps: bool = False,
    print_diagnostics: bool = True,
    check_ohlc: bool = False,
    return_values: bool = True,
    timeframe: str = '1m'  # New parameter for expected time difference
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
    - timeframe (str): The timeframe for the data (e.g., '1m', '1h', '1d').

    Returns:
    - Optional[Dict[str, Union[int, List[str], Optional[str], List[Dict[str, Union[int, str, pd.Timedelta]]]]]]:
      Dictionary with diagnostic metrics if `return_values` is True, otherwise None.
    """
    size = len(df)
    total_nans = df.isna().values.sum()                          # Total NaN's overall
    nan_cols = df.columns[df.isna().any()].tolist()              # Columns with any NaN values
    rows_with_nans = df.isna().any(axis=1).sum()                 # Total rows with any NaN values

    # Define the expected time difference based on the timeframe
    if timeframe == '1m':
        expected_diff = pd.Timedelta(minutes=1)
    elif timeframe == '1h':
        expected_diff = pd.Timedelta(hours=1)
    elif timeframe == '1d':
        expected_diff = pd.Timedelta(days=1)
    else:
        raise ValueError("Unsupported timeframe. Please use '1m', '1h', or '1d'.")

    # Find all rows where the gaps between subsequent rows are greater than the expected difference
    discontinuities = []
    time_diffs = df['Open time'].diff().dropna()
    discontinuities = time_diffs[time_diffs != expected_diff].index.tolist()

    # Identify the start and end of each gap, the gap size, and indices of gaps
    gap_details = []
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
        print(f"Timeframe: {timeframe}")
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

    
def classify_nans(data: Union[pd.Series, pd.DataFrame]) -> Dict[str, Dict[str, Union[int, str]]]:
    """
    Classify NaNs in a series or DataFrame as leading, trailing, interspersed, or full-column.

    Parameters:
    - data (pd.Series or pd.DataFrame): The data containing NaNs to be classified.

    Returns:
    - dict: Summary of NaN classifications by column.
    """
    def classify_single_series(nan_series):
        """Classify NaNs in a single series."""
        nan_count = nan_series.sum()

        if nan_series.all():
            return nan_count, "Full-column NaNs"

        non_nan_idx = nan_series[nan_series == False].index  # Indexes of non-NaN values
        if len(non_nan_idx) == 0:
            return nan_count, "Full-column NaNs"

        leading_nans = non_nan_idx[0] > 0
        trailing_nans = non_nan_idx[-1] < len(nan_series) - 1
        interspersed_nans = nan_series[non_nan_idx[0]:non_nan_idx[-1]].any()

        nan_types = []
        if leading_nans:
            nan_types.append("Leading NaNs")
        if trailing_nans:
            nan_types.append("Trailing NaNs")
        if interspersed_nans:
            nan_types.append("Interspersed NaNs")

        return nan_count, ", ".join(nan_types) if nan_types else "No NaNs"

    if isinstance(data, pd.Series):
        nan_count, classification = classify_single_series(data.isna())
        return {data.name: {"nan_count": nan_count, "classification": classification}}

    elif isinstance(data, pd.DataFrame):
        nan_summary = {}
        for column in data.columns:
            nan_count, classification = classify_single_series(data[column].isna())
            nan_summary[column] = {"nan_count": nan_count, "classification": classification}
        return nan_summary

    else:
        raise ValueError("Input must be a pandas Series or DataFrame")


def dataframe_statistics(df):
    """
    Calculate and print various statistics for each column in the dataframe, excluding the datetime column.
    """
    # Temporarily drop the 'Open time' column
    if 'Open time' and 'Close time' in df.columns:
        df_numeric = df.drop(columns=['Open time', 'Close time'])
    elif 'Open time' in df.columns:
        df_numeric = df.drop(columns=['Open time'])
    else:
        df_numeric = df

    print("\n--- DataFrame Statistics ---")
    print("Summary Statistics:")
    print(df_numeric.describe())

    print("\nSkewness of Columns:")
    print(df_numeric.skew())

    print("\nKurtosis of Columns:")
    print(df_numeric.kurt())

    print("\nMissing Values per Column:")
    print(df_numeric.isna().sum())

    print("\nCorrelation Matrix:")
    print(df_numeric.corr())


def visualize_distribution_with_stats(df, columns=None, bins=30, log_scale=False):
    """
    Visualizes data distribution for specified columns in a DataFrame by plotting histogram, 
    box plot, violin plot, KDE plot, and QQ plot as subplots, and prints summary statistics.

    Args:
    df (pd.DataFrame): DataFrame containing the data to be visualized.
    columns (list): List of column names to visualize. If None, all columns are visualized.
    bins (int): Number of bins for histograms.
    log_scale (bool): Apply log scale to the plots.
    """
    if columns is None:
        columns = df.columns
    
    for col in columns:
        data = df[col].dropna()

        # Summary Statistics
        print(f"--- Summary Statistics for {col} ---")
        print(f"Mean: {np.mean(data)}")
        print(f"Standard Deviation: {np.std(data)}")
        print(f"Skewness: {skew(data)}")
        print(f"Kurtosis: {kurtosis(data)}")
        print("\n")

        # Creating the subplots
        fig, axes = plt.subplots(3, 2, figsize=(14, 10))  # 3 rows, 2 columns of subplots
        fig.suptitle(f'Data Distribution for {col}', fontsize=16)

        # Plot 1: Histogram
        ax1 = axes[0, 0]
        ax1.hist(data, bins=bins, edgecolor='black')
        ax1.set_title('Histogram')
        ax1.set_xlabel(col)
        ax1.set_ylabel('Frequency')
        if log_scale:
            ax1.set_yscale('log')

        # Plot 2: Box Plot
        ax2 = axes[0, 1]
        ax2.boxplot(data, vert=False)
        ax2.set_title('Box Plot')
        ax2.set_xlabel(col)

        # Plot 3: Violin Plot
        ax3 = axes[1, 0]
        sns.violinplot(x=data, ax=ax3)
        ax3.set_title('Violin Plot')
        ax3.set_xlabel(col)

        # Plot 4: KDE Plot
        ax4 = axes[1, 1]
        sns.kdeplot(data, fill=True, ax=ax4)
        ax4.set_title('KDE Plot')
        ax4.set_xlabel(col)
        ax4.set_ylabel('Density')

        # Plot 5: QQ Plot
        ax5 = axes[2, 0]
        stats.probplot(data, dist="norm", plot=ax5)
        ax5.set_title('QQ Plot')

        # Remove unused subplot (axes[2, 1])
        fig.delaxes(axes[2, 1])

        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to fit title
        plt.show()