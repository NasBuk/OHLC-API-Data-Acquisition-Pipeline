"""
API configuration file for cryptocurrency exchanges.

This file defines the settings and parameters for interacting with different
cryptocurrency exchange APIs to fetch market data (OHLC - Open, High, Low, 
Close data).

The purpose of keeping this as a separate file is to provide a single place 
where exchange-specific settings can be updated or new exchanges can be added 
without needing to modify the core code. Any changes related to exchange API 
specifics should ONLY be made here.

### How to Add a New Exchange:
To add a new exchange, consult the exchange's official API documentation to 
properly fill in the fields below. Each exchange has its own format for API 
requests and responses, so it's crucial to correctly map the exchange's 
response structure and parameters to the existing configuration structure.

### Key Explanations:

- **url**: The base URL for the API endpoint that retrieves historical 
  candlestick (OHLC) data.
  
- **columns**: A list of columns used for storing the API response data in a 
  pandas DataFrame. This should correspond to the structure of the data 
  returned by the exchange’s API.

- **symbol**: A mapping of standardized trading pairs to the exchange-specific 
  format. For example, 'BTCUSD' may correspond to 'BTCUSDT' on Binance.

- **interval**: A mapping of standardized time intervals to the exchange-specific 
  format (e.g., '1m' for 1-minute candles).

- **start_date**: The date from which to start fetching historical data. This 
  should be in 'YYYY-MM-DD' format and should be adjusted based on how far back 
  data needs to be fetched and the exchange's historical data availability.

- **sleep_time**: Time (in seconds) to wait between requests to prevent hitting 
  API rate limits. This varies by exchange depending on their rate-limit rules.

- **limit**: The maximum number of data points (candles) returned in a single 
  request. This value is exchange-specific and must comply with the exchange’s 
  API limits.

- **time_columns**: A list of the columns representing timestamps in the API 
  response (e.g., 'Open time', 'Close time'). These ensure correct interpretation 
  of time-based data.

- **time_unit**: Specifies the time unit for timestamps in the API response. 
  Common units are 'ms' (milliseconds) and 's' (seconds). This tells the code 
  how to convert timestamps correctly.

- **response_key**: The key or path used to extract OHLC data from the JSON 
  response. Some exchanges return data in nested structures. Use dot notation 
  (e.g., 'data.result') to navigate through nested JSON objects.

- **reverse_data**: A boolean flag indicating whether the returned data should be 
  reversed. Some exchanges return data in reverse chronological order, so this 
  flag ensures the data is ordered correctly from earliest to latest.

- **construct_params**: A lambda function that constructs the parameters required 
  for making API requests. The lambda takes the exchange configuration (`config`), 
  a `start_datetime`, and an `end_datetime`, and returns a dictionary of request 
  parameters. Each exchange has a unique lambda to handle its specific requirements 
  for building the API request.

### Important Notes:
- Always refer to the official API documentation of the exchange you're adding 
  to ensure proper parameter mapping and response interpretation.
- The codebase dynamically fills placeholders like `symbol`, `start_time`, and 
  `end_time` during data fetch operations.
- Ensure the number of candles fetched per request (as defined in 'limit') complies 
  with the exchange's API limitations.
"""

from datetime import timedelta

API_CONFIG = {
    'Binance': {
        'url': 'https://api.binance.com/api/v3/klines',
        'columns': ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'],
        'sleep_time': 0.025,
        'time_columns': ['Open time', 'Close time'],
        'time_unit': 'ms',
        'response_key': None,
        'reverse_data': False,
        'limit': '1000',
        'pairs': {
            'BTCUSD': {
                'symbol': 'BTCUSDT',
                'start_date': '2017-08-17'
            },
            'ETHUSD': {
                'symbol': 'ETHUSDT',
                'start_date': '2017-08-17'
            },
            'BNBUSD': {
                'symbol': 'BNBUSDT',
                'start_date': '2017-11-06'
            },
            'ADAUSD': {
                'symbol': 'ADAUSDT',
                'start_date': '2018-04-17'
            },
            'XRPUSD': {
                'symbol': 'XRPUSDT',
                'start_date': '2018-05-04'
            }
        },
        'interval': {
            '1m': '1m'
        },
        'construct_params': lambda config, start_datetime, end_datetime: {
            'symbol': config.symbol,
            'interval': config.interval,
            'startTime': str(int(start_datetime.timestamp() * 1000)),
            'endTime': str(int(end_datetime.timestamp() * 1000)),
            'limit': '1000'
        }
    },
    'OKX': {
        'url': 'https://www.okx.com/api/v5/market/history-candles',
        'columns': ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Volume (Currency)', 'Volume (Quote)', 'Confirm'],
        'sleep_time': 0.12,
        'time_columns': ['Open time'],
        'time_unit': 'ms',
        'response_key': 'data',
        'reverse_data': True,
        'limit': '100',
        'pairs': {
            'BTCUSD': {
                'symbol': 'BTC-USDT',
                'start_date': '2018-01-11'
            },
            'ETHUSD': {
                'symbol': 'ETH-USDT',
                'start_date': '2018-01-11'
            },
            'BNBUSD': {
                'symbol': 'BNB-USDT',
                'start_date': '2022-12-21'
            },
            'ADAUSD': {
                'symbol': 'ADA-USDT',
                'start_date': '2018-07-23'
            },
            'XRPUSD': {
                'symbol': 'XRP-USDT',
                'start_date': '2018-01-11'
            }
        },
        'interval': {
            '1m': '1m'
        },
        'construct_params': lambda config, start_datetime, end_datetime: {
            'instId': config.symbol,
            'bar': config.interval,
            'before': str(int((start_datetime - timedelta(minutes=1)).timestamp() * 1000)),
            'after': str(int(min(start_datetime + timedelta(minutes=99), end_datetime).timestamp() * 1000)),
            'limit': '100'
        }
    },
    'Coinbase': {
        'url': 'https://api.exchange.coinbase.com/products/{product_id}/candles',
        'columns': ['Open time', 'Low', 'High', 'Open', 'Close', 'Volume'],
        'sleep_time': 0.2,
        'time_columns': ['Open time'],
        'time_unit': 's',
        'response_key': None,
        'reverse_data': True,
        'limit': '300',
        'pairs': {
            'BTCUSD': {
                'symbol': 'BTC-USD',
                'start_date': '2015-07-20'
            },
            'ETHUSD': {
                'symbol': 'ETH-USD',
                'start_date': '2016-09-29'
            },
            'ADAUSD': {
                'symbol': 'ADA-USD',
                'start_date': '2021-03-18'
            },
            'XRPUSD': {
                'symbol': 'XRP-USD',
                'start_date': '2019-02-28'
            }
        },
        'interval': {
            '1m': 60
        },
        'construct_params': lambda config, start_datetime, end_datetime: {
            'granularity': config.interval,
            'start': start_datetime.isoformat(),
            'end': (min(start_datetime + timedelta(minutes=int(config.limit)), end_datetime)).isoformat()
        }
    },
    'Bitfinex': {
        'url': 'https://api-pub.bitfinex.com/v2/candles/trade:{timeframe}:{product_id}/hist',
        'columns': ['Open time', 'Open', 'Close', 'High', 'Low', 'Volume'],
        'sleep_time': 6,
        'time_columns': ['Open time'],
        'time_unit': 'ms',
        'response_key': None,
        'reverse_data': True,
        'limit': '10000',
        'pairs': {
            'BTCUSD': {
                'symbol': 'tBTCUSD',
                'start_date': '2013-07-19'
            },
            'ETHUSD': {
                'symbol': 'tETHUSD',
                'start_date': '2017-03-11'
            },
            'ADAUSD': {
                'symbol': 'tADAUSD',
                'start_date': '2021-04-06'
            },
            'XRPUSD': {
                'symbol': 'tXRPUSD',
                'start_date': '2017-09-25'
            }
        },
        'interval': {
            '1m': '1m', '5m': '5m', '15m': '15m', '1h': '1h', '6h': '6h', '1d': '1D'
        },
        'construct_params': lambda config, start_datetime, end_datetime: {
            'start': int(start_datetime.timestamp() * 1000),
            'end': int(min((start_datetime + timedelta(minutes=int(config.limit)), end_datetime)).timestamp() * 1000),
            'limit': config.limit
        }
    },
    'KuCoin': {
        'url': 'https://api.kucoin.com/api/v1/market/candles',
        'columns': ['Open time', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount'],
        'sleep_time': 0.5, 
        'time_columns': ['Open time'],
        'time_unit': 's',
        'response_key': 'data',
        'reverse_data': True,
        'limit': '1500',
        'pairs': {
            'BTCUSD': {
                'symbol': 'BTC-USDT',
                'start_date': '2017-12-21'
            },
            'ETHUSD': {
                'symbol': 'ETH-USDT',
                'start_date': '2018-01-01'
            },
            'BNBUSD': {
                'symbol': 'BNB-USDT',
                'start_date': '2019-06-19'
            },
            'ADAUSD': {
                'symbol': 'ADA-USDT',
                'start_date': '2019-07-04'
            },
            'XRPUSD': {
                'symbol': 'XRP-USDT',
                'start_date': '2019-02-17'
            }
        },
        'interval': {
            '1m': '1min', '5m': '5min', '15m': '15min', '1h': '1hour', '1d': '1day'
        },
        'construct_params': lambda config, start_datetime, end_datetime: {
            'type': config.interval,
            'symbol': config.symbol,
            'startAt': int(start_datetime.timestamp()),
            'endAt': int(min((start_datetime + timedelta(minutes=int(config.limit)), end_datetime)).timestamp())
        }
    },
    'BitMEX': {
        'url': 'https://www.bitmex.com/api/v1/trade/bucketed',
        'columns': ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume'],
        'sleep_time': 2.1,
        'time_columns': ['Open time'],
        'time_unit': 's',
        'response_key': None,
        'reverse_data': False,
        'limit': '10000',
        'pairs': {
            'BTCUSD': {
                'symbol': 'XBTUSD',
                'start_date': '2015-09-25'
            },
            'ETHUSD': {
                'symbol': 'ETHUSD',
                'start_date': '2018-08-02'
            },
            'BNBUSD': {
                'symbol': 'BNBUSD',
                'start_date': '2021-09-29'
            },
            'ADAUSD': {
                'symbol': 'ADAUSD',
                'start_date': '2021-09-29'
            },
            'XRPUSD': {
                'symbol': 'XRPUSD',
                'start_date': '2020-02-05'
            }
        },
        'interval': {
            '1m': '1m', '5m': '5m', '1h': '1h', '1d': '1d'
        },
        'construct_params': lambda config, start_datetime, end_datetime: {
            'symbol': config.symbol,
            'binSize': config.interval,
            'startTime': start_datetime.isoformat(),
            'endTime': (min(start_datetime + timedelta(minutes=int(config.limit)), end_datetime)).isoformat(),
            'count': config.limit,
            'partial': False
        }
    },
    'Bitstamp': {
        'url': 'https://www.bitstamp.net/api/v2/ohlc/{product_id}/',
        'columns': ['Open time', 'Open', 'Close', 'High', 'Low', 'Volume'],
        'sleep_time': 0.2,
        'time_columns': ['Open time'],
        'time_unit': 's',
        'response_key': 'data.ohlc',
        'reverse_data': False,
        'limit': '1000',
        'pairs': {
            'BTCUSD': {
                'symbol': 'btcusd',
                'start_date': '2011-08-18'
            },
            'ETHUSD': {
                'symbol': 'ethusd',
                'start_date': '2017-08-16'
            },
            'ADAUSD': {
                'symbol': 'adausd',
                'start_date': '2021-11-17'
            },
            'XRPUSD': {
                'symbol': 'xrpusd',
                'start_date': '2016-12-16'
            }
        },
        'interval': {
            '1m': '60',
            '5m': '300',
            '15m': '900',
            '30m': '1800',
            '1h': '3600',
            '6h': '21600',
            '1d': '86400'
        },
        'construct_params': lambda config, start_datetime, end_datetime: {
            'start': int((start_datetime ).timestamp()),
            'end': int(min((start_datetime + timedelta(minutes=int(config.limit)) - timedelta(minutes=1)), end_datetime).timestamp()),
            'step': config.interval,
            'limit': config.limit
        }
    },
    # 'HitBTC': {
    #     'url': 'https://api.hitbtc.com/api/3/public/candles/{product_id}/',
    #     'columns': ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume'],
    #     'sleep_time': 2.1,
    #     'time_columns': ['Open time'],
    #     'time_unit': 'ms',
    #     'response_key': None,
    #     'reverse_data': False,
    #     'limit': '100',
    #     'pairs': {
    #         'BTCUSD': {
    #             'symbol': 'BTCUSDT',
    #             'start_date': '2013-01-01'
    #         },
    #         'ETHUSD': {
    #             'symbol': 'ETHUSDT',
    #             'start_date': '2015-08-07'
    #         }
    #     },
    #     'interval': {
    #         '1m': 'M1', '5m': 'M5', '1h': 'H1', '1d': 'D1'
    #     },
    #     'construct_params': lambda config, start_datetime, end_datetime: {
    #         'symbol': config.symbol,
    #         'period': config.interval,
    #         'from': int(start_datetime.timestamp() * 1000),
    #         'till': int(end_datetime.timestamp() * 1000),
    #         'limit': config.limit
    #     }
    # },
    # 'Poloniex': {
    #     'url': 'https://api.poloniex.com/markets/{product_id}/candles/',
    #     'columns': ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume'],
    #     'sleep_time': 2.0,
    #     'time_columns': ['Open time'],
    #     'time_unit': 'ms',
    #     'response_key': None,
    #     'reverse_data': False,
    #     'limit': '100',
    #     'pairs': {
    #         'BTCUSD': {
    #             'symbol': 'BTC_USDT',
    #             'start_date': '2014-01-01'
    #         },
    #         'ETHUSD': {
    #             'symbol': 'ETH_USDT',
    #             'start_date': '2015-08-07'
    #         }
    #     },
    #     'interval': {
    #         '1m': 'MINUTE_1', '5m': 'MINUTE_5', '1h': 'HOUR_1', '1d': 'DAY_1'
    #     },
    #     'construct_params': lambda config, start_datetime, end_datetime: {
    #         'symbol': config.symbol,
    #         'interval': config.interval,
    #         'startTime': int(start_datetime.timestamp() * 1000),
    #         #'endTime': int(min((start_datetime + timedelta(minutes=int(config.limit))), end_datetime).timestamp() * 1000),
    #         'limit': config.limit
    #     }
    # },
    # 'CEX.IO': {
    #     'url': 'https://cex.io/api/ohlcv/hd/{date}/{symbol}',
    #     'columns': ['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'],
    #     'sleep_time': 6,
    #     'time_columns': ['timestamp'],
    #     'time_unit': 's',
    #     'response_key': None,
    #     'reverse_data': False,
    #     'limit': '100',
    #     'pairs': {
    #         'BTCUSD': {
    #             'symbol': 'BTC/USD',
    #             'start_date': '2013-01-01'
    #         },
    #         'ETHUSD': {
    #             'symbol': 'ETH/USD',
    #             'start_date': '2015-08-07'
    #         }
    #     },
    #     'interval': {
    #         '1m': '1m', '1h': '1h', '1d': '1d'
    #     },
    #     'construct_params': lambda config, start_datetime, end_datetime: {
    #         'symbol': config.symbol,
    #         'date': start_datetime.strftime('%Y%m%d'),
    #     }
    # }
}