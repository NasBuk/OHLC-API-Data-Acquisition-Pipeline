#!/bin/bash

: '
Master script for downloading, processing, auditing, and uploading cryptocurrency OHLC datasets.

This script:
1. Activates a Python virtual environment.
2. Downloads OHLC data.
3. Combines and cleans data.
4. Audits data and generates metadata for Kaggle.
5. Uploads datasets to Kaggle.
6. Deactivates the virtual environment once complete.

Setup:
- Place this script in the "trading" directory.
- Configure the path to the Python virtual environment by setting the VENV_PATH variable below.
'

# Set the virtual environment path (edit this variable as needed)
VENV_PATH="$HOME/myenv/bin"

# Ensure the script is running from the "trading" directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$BASE_DIR/data/ohlc_csv"

# Activate the Python virtual environment
source "$VENV_PATH/activate"

# Step 1: Download and update all datasets
"$VENV_PATH/python3.12" "$BASE_DIR/fetch_data/download_klines.py"

# Step 2: Combine and clean the datasets
"$VENV_PATH/python3.12" "$BASE_DIR/fetch_data/combine_ohlc.py"

# Step 3: Audit the data and generate metadata for Kaggle
"$VENV_PATH/python3.12" "$BASE_DIR/fetch_data/audit_and_metagen.py"

# Step 4: Loop through each trading pair dataset directory and upload it to Kaggle
for trading_pair_dir in "$DATA_DIR"/*; do
    if [ -d "$trading_pair_dir" ]; then
        "$VENV_PATH/kaggle" datasets version -p "$trading_pair_dir" -m "updated" -d
    fi
done

# Deactivate the Python virtual environment
deactivate
