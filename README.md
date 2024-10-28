# Multi-Exchange Cryptocurrency OHLC Data Integration and Analysis

This repository provides a comprehensive pipeline for aggregating, cleaning, and analyzing OHLC (Open, High, Low, Close) cryptocurrency data from multiple exchanges. By using this solution, you can create a continuous, volume-weighted index dataset for BTC/USD (or any specified pairs) and automate the entire process, from data retrieval to data publishing on Kaggle.

The master bash script enables full automation, running each Python module in sequence to fetch, process, audit, and upload data. Configurable through `API_CONFIG`, this pipeline is exchange-agnostic—simply add a new API configuration to begin working with a new dataset.

## Key Features

1. **Automated Workflow**  
   The bash script automates the entire workflow, from data download to Kaggle upload, supporting a cron job setup for ongoing updates. It allows integration of multiple trading pairs and exchanges through a single configuration file.

2. **Comprehensive Data Integration**  
   OHLC data from multiple exchanges is integrated and volume-weighted, creating a robust, continuous index. The data cleaning process includes gap detection, imputation, and open-close (OC) alignment.

3. **Exchange-Agnostic Design**  
   With `API_CONFIG`, exchanges can be added dynamically, allowing scalability and integration of additional cryptocurrency pairs or data sources.

4. **Kaggle Metadata Generation**  
   Automatically generates and uploads Kaggle metadata files for each trading pair, streamlining dataset updates for research and machine learning applications.

5. **Jupyter Notebook Tutorial**  
   An included Jupyter notebook provides an in-depth walkthrough for integrating, processing, and visualizing the final combined dataset. This notebook demonstrates how to use the aggregated index, analyze data quality, and visualize OHLC data.

## Repository Structure

- **[fetch_data/download_klines.py](fetch_data/download_klines.py)**  
   Downloads raw OHLC data from configured APIs, handling rate limits and saving data in a standardized format.
   
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

- **[master_script.sh](master_script.sh)**  
   The master automation script that sequentially activates each component of the workflow, streamlining the data download, processing, auditing, and Kaggle upload steps.

- **Jupyter Notebook: Multi-Exchange BTC/USD Data Integration**  
   A tutorial-style notebook to guide you through the dataset integration process. Covers data import, gap analysis, OC alignment, volume-weighted averaging, and gap imputation. This resource illustrates how each component works and provides hands-on examples of data visualization.

## Installation and Setup

1. **Clone this Repository**
   ```bash
   git clone https://github.com/your-username/multi-exchange-crypto-ohlc.git
   cd multi-exchange-crypto-ohlc

2. **Configure the API**
Add API keys and configurations to API_CONFIG. Ensure exchange-specific values are correct (endpoint URLs, rate limits, etc.).

3. **Set Up Python Environment**
Install required packages in your Python environment. Recommended to use virtualenv:

### Data Processing and Quality Checks

The repository's workflow includes multiple steps to clean, process, and analyze OHLC data from various exchanges, creating a cohesive and continuous dataset that is automatically updated and uploaded to Kaggle.

#### Workflow Overview
The following scripts drive the data workflow, creating a combined, volume-weighted OHLC index from multiple exchanges:

1. **`download_klines.py`**: Fetches OHLC data from supported exchanges (as defined in `API_CONFIG`). Handles rate limiting, retries, and centralizes data download parameters for each exchange, enabling easy addition of new datasets.

2. **`combine_ohlc.py`**: Aggregates OHLC data across exchanges into a single, unified dataset for each trading pair. Features:
   - **Volume-weighted Averaging**: Calculates OHLC values with volume weighting to prioritize data from high-volume exchanges, creating a more market-representative index.
   - **Data Imputation**: Fills small gaps using a centered moving average to maintain data continuity and ensure consistent analysis.
   - **Open-Close (OC) Alignment**: Ensures the Open of each candle aligns with the Close of the previous candle, correcting inconsistencies in source data.
   - **Exchange Mappings**: Automatically maps each trading pair to the exchanges that provide data for it.

3. **`audit_and_metagen.py`**: Performs diagnostics and quality checks on the combined dataset, generating metadata for easy publication to Kaggle. Key features include:
   - **Data Diagnostics**: Checks for NaNs, duplicate rows, and time discontinuities.
   - **Image Generation**: Generates styled data tables and OHLC charts, uploaded to Imgur and linked in the metadata.
   - **Kaggle Metadata Generation**: Creates standardized `metadata.json` files for each dataset, using exchange schemas and currency mappings for consistency.

4. **`file_utils.py`**: Handles loading and saving data across formats (CSV, pickle, numpy) and manages directory paths. Ensures that data from each stage is securely saved and organized for seamless integration.

5. **`master_script.sh`**: Automates the entire process from start to finish, including:
   - Activating the environment
   - Running data download, combination, and quality check scripts
   - Uploading updated datasets to Kaggle with new metadata

#### Example Data Analysis in Jupyter Notebook
A comprehensive Jupyter notebook (`btc_usd_index_notebook.ipynb`) is provided, walking through the full process of creating a BTC/USD index from multi-exchange data. Key steps include:
   - **Data Inspection and Cleaning**: Loading and checking each exchange’s dataset for gaps, misalignments, and outliers.
   - **Gap Imputation**: Applying moving averages to impute missing values, preventing artificial volatility.
   - **Volume-weighted Index Construction**: Calculating the volume-weighted OHLC values to form a continuous, gap-free dataset.
   - **Data Visualization**: Plotting candlestick charts and line plots for quality checks and further insights.

### Continuous Kaggle Dataset Updates

This project is designed for seamless integration with Kaggle:
1. **Automated Metadata**: Each dataset is paired with a dynamic metadata file (`metadata.json`), including title, description, resource links, and data diagnostics images.
2. **Scheduled Updates**: With the `master_script.sh` as a cron job, all datasets can be kept up-to-date automatically.
3. **Quick Dataset Addition**: Add new exchange datasets by configuring them in `API_CONFIG`.

### Kaggle Repositories
Explore the finalized datasets here:
1. [BTC/USD on Multi-Exchange OHLC Index](#)
2. [ETH/USD on Multi-Exchange OHLC Index](#)
3. [ADA/USD on Multi-Exchange OHLC Index](#)
4. [XRP/USD on Multi-Exchange OHLC Index](#)
5. [BNB/USD on Multi-Exchange OHLC Index](#)

### Contributions & License
This project is open to contributions and licensed under the [MIT License](LICENSE). Feel free to open issues or pull requests for new exchanges, features, or bug fixes.
