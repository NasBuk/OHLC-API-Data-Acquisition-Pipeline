import os
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(file_path: str, file_type: str = 'pickle', set_index: str = None, 
              drop_columns: list = None, log_info: bool = True):
    """
    Load data from a file as a pickle dataframe, CSV, or numpy array, index columns can be set
    and columns can be dropped optionally.

    Parameters:
    file_path (str): The path to the file.
    file_type (str): The data structure to load ('pickle', 'csv', or 'numpy'). Defaults to 'pickle'.
    set_index (str, optional): The column to set as index. Defaults to None.
    drop_columns (list, optional): Columns to drop. Defaults to None.
    log_info (bool): Whether to log the process. Defaults to True.

    Returns:
    data: Loaded data (type depends on file_type).
    """
    try:
        full_path = create_path(file_path, log_info=log_info)

        if file_type == 'pickle':
            df = pd.read_pickle(full_path)
        elif file_type == 'csv':
            df = pd.read_csv(full_path)
        elif file_type == 'numpy':
            data = np.load(full_path)
            if log_info:
                logging.info(f"Numpy data loaded successfully from {file_path}")
            return data
        else:
            raise ValueError("Unsupported file type specified.")
        
        # Common DataFrame operations for 'pickle' and 'csv'
        if drop_columns:
            df.drop(columns=drop_columns, axis=1, inplace=True)
        if set_index:
            df.set_index(set_index, inplace=True)
        if log_info:
            logging.info(f"Data loaded successfully from {file_path} as {file_type}")
        return df

    except FileNotFoundError:
        if log_info:
            logging.error(f"File not found: {full_path}")
        raise
    except Exception as e:
        if log_info:
            logging.error(f"Error loading file: {e}")
        raise


def save_data(data, file_path: str, file_type: str = 'pickle', 
              drop_columns: list = None, reset_index: bool = False, 
              log_info: bool = True, create_missing_dirs: bool = True, 
              append_if_exists: bool = True):
    """
    Save a pickle dataframe, CSV, or numpy data to a file. Index can be reset, and
    columns can be optionally dropped before saving.

    Parameters:
    data: The data to save (type depends on file_type).
    file_path (str): The path to the file.
    file_type (str): The type of file to save ('pickle', 'csv', or 'numpy'). Defaults to 'pickle'.
    drop_columns (list, optional): Columns to drop if saving a DataFrame. Defaults to None.
    reset_index (bool, optional): Whether to reset the index if saving a DataFrame. Defaults to False.
    log_info (bool): Whether to log the process. Defaults to True.
    create_missing_dirs (bool): Whether to create missing directories in the path. Defaults to True.
    append_if_exists (bool): Whether to append to the file if it exists (only for CSV). Defaults to True.
    """
    try:
        full_path = create_path(file_path, create_missing_dirs=create_missing_dirs, log_info=log_info)

        if file_type == 'pickle':
            if drop_columns:
                data.drop(columns=drop_columns, inplace=True)
            if reset_index:
                data.reset_index(inplace=True)
            data.to_pickle(full_path)
            if log_info:
                logging.info(f"Pickle DataFrame saved successfully to {file_path}")
        
        elif file_type == 'csv':
            if drop_columns:
                data.drop(columns=drop_columns, inplace=True)
            if reset_index:
                data.reset_index(inplace=True)
            
            # Check if the file exists and whether to append or overwrite
            if os.path.exists(full_path) and append_if_exists:
                data.to_csv(full_path, mode='a', header=False, index=False)
                if log_info:
                    logging.info(f"Data appended to CSV file: {file_path}")
            else:
                data.to_csv(full_path, index=False)
                if log_info:
                    logging.info(f"CSV file saved successfully to {file_path}")
        
        elif file_type == 'numpy':
            np.save(full_path, data)
            if log_info:
                logging.info(f"Numpy array saved successfully to {file_path}")
        
        else:
            raise ValueError("Unsupported file type specified.")
    
    except KeyError as e:
        if log_info:
            logging.error(f"Error dropping columns: {e}")
        raise
    except Exception as e:
        if log_info:
            logging.error(f"Error saving file: {e}")
        raise


def create_path(input_string: str, create_missing_dirs: bool = False, log_info: bool = True) -> str:
    """
    Create the full path for the given input string. If create_missing_dirs is True,
    create any missing directories in the path.

    Parameters:
    input_string (str): The input file path (absolute or relative).
    create_missing_dirs (bool): Whether to create missing directories. Defaults to False.
    log_info (bool): Whether to log the process. Defaults to True.

    Returns:
    str: The full path.
    """
    # Check if the input path is already absolute
    if os.path.isabs(input_string):
        new_path = input_string
    else:
        # Otherwise create a relative reference to the project root folder
        new_path = os.path.join(os.path.dirname(__file__), '..', *input_string.split(os.sep))
    
    directory = os.path.dirname(new_path)
    
    # Check and create missing directories if required
    if create_missing_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            if log_info:
                logging.info(f"Created missing directories: {directory}")
    else:
        # If not creating dirs, just log missing directories
        if not os.path.exists(directory):
            if log_info:
                logging.error(f"Directory not found: {directory}")
        elif not os.path.isfile(new_path):
            if log_info:
                logging.error(f"File not found: {os.path.basename(new_path)}")
    
    return new_path
