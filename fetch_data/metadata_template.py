"""
Kaggle Metadata Template Generator

This module generates JSON metadata files for uploading and updating OHLC (Open, High, Low, Close) 
trading data across multiple exchanges on Kaggle. It includes templates and mappings for consistent
and standardized metadata creation, facilitating ease of access for machine learning engineers, 
analysts, and researchers working with 1-minute historical cryptocurrency data.

Modify this template to make changes to the data that is pushed to Kaggle dataset repositories.

The metadata generated is highly customizable and includes comprehensive features:
    - A dataset description template (metadata_template) for all included trading pairs.
    - A currency name mapping (currency_name_map) for converting symbols to full names.
    - Exchange schemas (exchange_schemas) that specify the fields and types for each supported 
      exchange, ensuring all data meets expected structure requirements.

This module is intended to be used in conjunction with audit_and_metagen.py that performs data auditing,
logging and Kaggle metadata generation.

Structures:
----------
- metadata_template : dict
    Template for the metadata with placeholders for currency name, exchange data, and URLs.
- currency_name_map : dict
    Maps trading pair symbols (e.g., "BTCUSD") to full names (e.g., "Bitcoin").
- exchange_schemas : dict
    Contains field definitions for each exchange, specifying field names, descriptions, 
    and data types for consistent, structured data storage across exchanges.

"""

metadata_template = {
    "title": "{currency_name}, 7 Exchanges, 1m Full Historical Data",
    "subtitle": "The Most Complete, Continuous and Clean {currency_abbr} Dataset for ML Engineers/Analysts",
    "id": "imranbukhari/comprehensive-{currency_abbr}-1m-data",
    "description": """I am a new developer and I would greatly appreciate your support. If you find this dataset helpful, please consider giving it an upvote!
    
# Key Features:

**Complete 1-Minute Data:** Raw 1-minute historical data from multiple exchanges, covering the entire trading history of {currency_abbr} available through their API endpoints. This dataset is updated daily to ensure up-to-date coverage.

**Combined Index Dataset:** A unique feature of this dataset is the combined index, which is derived by averaging all other datasets into one, please see attached notebook. This creates the longest continuous, unbroken {currency_abbr} dataset available on Kaggle, with no gaps and no erroneous values. It gives a much more comprehensive view of the market i.e. total volume across multiple exchanges.

**Superior Performance:** The combined index dataset has demonstrated superior 'mean average error' (MAE) metric performance when training machine learning models, compared to single-source datasets by a whole order of MAE magnitude.

**Unbroken History:** The combined dataset's continuous history is a valuable asset for researchers and traders who require accurate and uninterrupted time series data for modeling or back-testing.

![{currency_abbr} Dataset Summary]({imgur_url_1})

![Combined Dataset Close Plot]({imgur_url_2}) *This plot illustrates the continuity of the dataset over time, with no gaps in data, making it ideal for time series analysis.*

# Included Resources:

### Two Notebooks:

**Dataset Usage and Diagnostics:** This notebook demonstrates how to use the dataset and includes a powerful data diagnostics function, which is useful for all time series analyses.

**Aggregating Multiple Data Sources:** This notebook walks you through the process of combining multiple exchange datasets into a single, clean dataset. (Currently unavailable, will be added shortly)""",
     "resources": [],
     "licenses": [
        {
            "name": "CC-BY-SA-4.0"
        }
    ]
}

currency_name_map = {
    "BTCUSD": "Bitcoin",
    "ETHUSD": "Ethereum",
    "ADAUSD": "Cardano",
    "BNB": "BNBCoin",
    "XRP": "Ripple"
}

exchange_schemas = {
    "Binance": [
        {"name": "Open time", "description": "Candle start time", "type": "datetime"},
        {"name": "Open", "description": "Open price", "type": "number"},
        {"name": "High", "description": "Highest price", "type": "number"},
        {"name": "Low", "description": "Lowest price", "type": "number"},
        {"name": "Close", "description": "Close price", "type": "number"},
        {"name": "Volume", "description": "Traded volume", "type": "number"},
        {"name": "Close time", "description": "Candle close time", "type": "datetime"},
        {"name": "Quote asset volume", "description": "Total quote asset volume", "type": "number"},
        {"name": "Number of trades", "description": "Number of trades", "type": "integer"},
        {"name": "Taker buy base asset volume", "description": "Volume of base asset bought by takers", "type": "number"},
        {"name": "Taker buy quote asset volume", "description": "Volume of quote asset bought by takers", "type": "number"},
        {"name": "Ignore", "description": "Reserved field (ignored)", "type": "string"}
    ],
    "OKX": [
        {"name": "Open time", "description": "Candle start time", "type": "datetime"},
        {"name": "Open", "description": "Open price", "type": "number"},
        {"name": "High", "description": "Highest price", "type": "number"},
        {"name": "Low", "description": "Lowest price", "type": "number"},
        {"name": "Close", "description": "Close price", "type": "number"},
        {"name": "Volume", "description": "Traded volume", "type": "number"},
        {"name": "Volume (Currency)", "description": "Volume in currency", "type": "number"},
        {"name": "Volume (Quote)", "description": "Volume in quote asset", "type": "number"},
        {"name": "Confirm", "description": "Confirmation status", "type": "string"}
    ],
    "Coinbase": [
        {"name": "Open time", "description": "Candle start time", "type": "datetime"},
        {"name": "Low", "description": "Lowest price", "type": "number"},
        {"name": "High", "description": "Highest price", "type": "number"},
        {"name": "Open", "description": "Open price", "type": "number"},
        {"name": "Close", "description": "Close price", "type": "number"},
        {"name": "Volume", "description": "Traded volume", "type": "number"}
    ],
    "Bitfinex": [
        {"name": "Open time", "description": "Candle start time", "type": "datetime"},
        {"name": "Open", "description": "Open price", "type": "number"},
        {"name": "Close", "description": "Close price", "type": "number"},
        {"name": "High", "description": "Highest price", "type": "number"},
        {"name": "Low", "description": "Lowest price", "type": "number"},
        {"name": "Volume", "description": "Traded volume", "type": "number"}
    ],
    "KuCoin": [
        {"name": "Open time", "description": "Candle start time", "type": "datetime"},
        {"name": "Open", "description": "Open price", "type": "number"},
        {"name": "Close", "description": "Close price", "type": "number"},
        {"name": "High", "description": "Highest price", "type": "number"},
        {"name": "Low", "description": "Lowest price", "type": "number"},
        {"name": "Volume", "description": "Traded volume", "type": "number"},
        {"name": "Amount", "description": "Amount of asset traded", "type": "number"}
    ],
    "BitMEX": [
        {"name": "Open time", "description": "Candle start time", "type": "datetime"},
        {"name": "Open", "description": "Open price", "type": "number"},
        {"name": "High", "description": "Highest price", "type": "number"},
        {"name": "Low", "description": "Lowest price", "type": "number"},
        {"name": "Close", "description": "Close price", "type": "number"},
        {"name": "Volume", "description": "Traded volume", "type": "number"}
    ],
    "Bitstamp": [
        {"name": "Open time", "description": "Candle start time", "type": "datetime"},
        {"name": "Open", "description": "Open price", "type": "number"},
        {"name": "Close", "description": "Close price", "type": "number"},
        {"name": "High", "description": "Highest price", "type": "number"},
        {"name": "Low", "description": "Lowest price", "type": "number"},
        {"name": "Volume", "description": "Traded volume", "type": "number"}
    ]
}
