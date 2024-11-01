# Multi-Exchange Cryptocurrency OHLC Data Integration and Analysis

This repository provides a comprehensive pipeline for aggregating, cleaning, and combining OHLC (Open, High, Low, Close) financial data from multiple exchanges. By using this solution, you can create a continuous, volume-weighted index dataset for any trading pair asset, as well as create raw OHLC datasets from any exchange for any asset and automate the entire process, from data retrieval to data publishing on Kaggle.

The master bash script enables full automation via cron job automation, running each Python module in sequence to fetch, process, audit, and upload data. Configurable through `API_CONFIG`, this pipeline is exchange-agnostic—simply add a new API configuration to begin working with a new dataset. This works for any API endpoint that offers OHLCV data, the fetch_data/download_klines.py script is provided as pseudocode for demo purposes as this is proprietary for my own use, if you'd like an asset/exchange added, you can contact me and I'll make the asset available as a dataset on Kaggle.

## Key Features

1. **Automated Workflow**  
   The bash script automates the entire workflow, from data download to Kaggle upload, supporting a cron job setup for ongoing updates. It allows integration of multiple trading pairs and exchanges through a single configuration file.

2. **Comprehensive Data Integration**  
   OHLC data from multiple exchanges is integrated and volume-weighted, creating a robust, continuous index. The data cleaning process includes gap detection, imputation, and open-close (OC) alignment. 

3. **Exchange-Agnostic Design**  
   With `API_CONFIG`, exchanges can be added dynamically, allowing scalability and integration of additional pairs or data sources. This will work for ANY OHLC data that is offered through an API endpoint.

4. **Kaggle Metadata Generation**  
   Automatically generates and uploads Kaggle metadata files for each trading pair, streamlining dataset updates for research and machine learning applications. Links to the sets I currently maintain are at the bottom for you to see the end product.

5. **Jupyter Notebook Tutorial**  
   An included Jupyter notebook provides an in-depth walkthrough for integrating, processing, and visualizing the final combined dataset. This notebook demonstrates how to use the aggregated index, analyze data quality, and visualize OHLC data.

## Repository Structure

- **[fetch_data/download_klines_pseudocode.py](fetch_data/download_klines_pseudocode.py)**  
   Downloads raw OHLC data from configured APIs, handling rate limits, robust error handling, data integrity checks and saving data in a standardized format.
   
- **[fetch_data/combine_ohlc.py](fetch_data/combine_ohlc.py)**  
   Aggregates data from multiple exchanges to create a volume-weighted averaged index. This module includes:
   - Centered moving average imputation for filling data gaps.
   - Open-close alignment across exchanges to ensure continuity.
   - Volume-weighted averaging for OHLC values.

- **[fetch_data/audit_and_metagen.py](fetch_data/audit_and_metagen.py)**  
   Performs diagnostic checks and generates metadata for each dataset. Features include:
   - Diagnostic functions for data quality, detecting NaNs, gaps, and misalignments.
   - Visualization of data diagnostics, uploaded to Imgur for integration with Kaggle metadata.
   - Metadata generation formatted for Kaggle API compatibility, enabling easy dataset updates.

- **[fetch_data/api_config_v3.py](fetch_data/api_config_v3.py)**  
   API configuration file that specifies exchange-specific values (e.g., endpoint URLs, rate limits, time intervals) for each cryptocurrency pair. Supports dynamic addition of new pairs or exchanges.

- **[fetch_data/metadata_template.py](fetch_data/metadata_template.py)**  
   Metadata template file for consistent Kaggle uploads. Includes customizable fields for:
   - Dataset descriptions, titles, and resources.
   - Exchange schemas for standardized field definitions across exchanges.

- **[utils/file_utils.py](utils/file_utils.py)**  
   Utilities for handling file operations, including loading and saving data, creating directories, and managing file paths.

- **[automate_datasets.sh](automate_datasets.sh)**  
   The master automation script that sequentially activates each component of the workflow, streamlining the data download, processing, auditing, and Kaggle upload steps.

- **[Jupyter Notebook: Multi-Exchange BTC/USD Data Integration](notebooks/combining-multiple-data-sources-into-an-index.ipynb)**
   A tutorial-style notebook to guide you through the dataset integration process. Covers data import, gap analysis, OC alignment, volume-weighted averaging, and gap imputation. This resource illustrates how each component works and provides hands-on examples of data visualization. A live version of the notebook is available in my Kaggle dataset repositories, links at the bottom.

## Installation and Setup

1. **Clone this Repository**
   ```bash
   git clone https://github.com/NasBuk/Automated-Download-Update-OHLC-Dataset-from-any-API-Endpoint.git
   cd automated-download-update-ohlc-dataset-from-any-api-endpoint

2. **Set Up Python Environment**
Install required packages in your Python environment. Recommended to use a virtualenv, ensure you specify the bin/activate in the bash script to automate:
    ```bash
    python -m venv myenv
    source myenv/bin/activate
    pip install -e .

3. **Run the Master Script** Ensure the script is executable and run it (you must configure this file with your venv directories and project directory before running):
    ```bash
    chmod +x master_script.sh
    ./master_script.sh
You can set this up as a cron job to automate daily updates.

#### Example Data Analysis in Jupyter Notebook
A comprehensive Jupyter notebook (`btc_usd_index_notebook.ipynb`) is provided, walking through the full process of creating a BTC/USD index from multi-exchange data. Key steps include:
   - **Data Inspection and Cleaning**: Loading and checking each exchange’s dataset for gaps, misalignments, and outliers.
   - **Gap Imputation**: Applying moving averages to impute missing values, preventing artificial volatility.
   - **Volume-weighted Index Construction**: Calculating the volume-weighted OHLC values to form a continuous, gap-free dataset.
   - **Data Visualization**: Plotting candlestick charts and line plots for quality checks and further insights.

### Continuous Kaggle Dataset Updates

This project is designed for seamless integration with Kaggle:
1. **Automated Metadata**: Each dataset is paired with a dynamic metadata file (`metadata.json`), including title, description, resource links, and data diagnostics images.
2. **Scheduled Updates**: With the `automate_datasets.sh` as a cron job, all datasets can be kept up-to-date automatically.
3. **Quick Dataset Addition**: Add new exchange datasets by configuring them in `API_CONFIG`.

### Kaggle Repositories
Explore the finalized datasets here:
1. [BTC/USD on Multi-Exchange OHLC Index](https://www.kaggle.com/datasets/imranbukhari/comprehensive-btcusd-1m-data)
2. [ETH/USD on Multi-Exchange OHLC Index](https://www.kaggle.com/datasets/imranbukhari/comprehensive-ethusd-1m-data)
3. [ADA/USD on Multi-Exchange OHLC Index](https://www.kaggle.com/datasets/imranbukhari/comprehensive-adausd-1m-data)
4. [XRP/USD on Multi-Exchange OHLC Index](https://www.kaggle.com/datasets/imranbukhari/comprehensive-xrpusd-1m-data)
5. [BNB/USD on Multi-Exchange OHLC Index](https://www.kaggle.com/datasets/imranbukhari/comprehensive-bnbusd-1m-data)

### License
This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) license.

You are free to:
- Share: Copy and redistribute the material in any medium or format.
- Adapt: Remix, transform, and build upon the material.

**Under the following terms:**
- **Attribution**: You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial**: You may not use the material for commercial purposes.

For full details, see the [LICENSE file](LICENSE) or visit the [Creative Commons License page](https://creativecommons.org/licenses/by-nc/4.0/legalcode).
