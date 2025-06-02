import requests
import os
import sys
import json
from datetime import datetime

# Add the project root to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.file_io import load_yaml_config
from src.utils.logger import logger

class AlphaVantageAPI:
    """Alpha Vantage API client for fetching financial data"""
    
    def __init__(self, api_key=None, config_path=None):
        """
        Initialize the Alpha Vantage API client
        
        Args:
            api_key (str, optional): Alpha Vantage API key. If None, load from config.
            config_path (str, optional): Path to the config file.
        """
        if config_path is None:
            config_path = 'configs/data_sources.yaml'
        
        if api_key is None:
            try:
                config = load_yaml_config(config_path)
                self.api_key = config['api_keys']['alpha_vantage']
                self.base_url = config['alpha_vantage']['base_url']
                self.output_format = config['alpha_vantage']['output_format']
                self.rate_limit = config['alpha_vantage']['max_calls_per_minute']
            except Exception as e:
                logger.error(f"Failed to load Alpha Vantage configuration: {str(e)}")
                raise
        else:
            self.api_key = api_key
            self.base_url = 'https://www.alphavantage.co/query'
            self.output_format = 'json'
            self.rate_limit = 5
    
    def get_daily_time_series(self, symbol, outputsize='compact'):
        """
        Fetch daily time series data for a given stock symbol
        
        Args:
            symbol (str): Stock ticker symbol
            outputsize (str): 'compact' for last 100 data points, 'full' for all available data
            
        Returns:
            dict: Daily time series data
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize,
            'apikey': self.api_key,
            'datatype': self.output_format
        }
        
        logger.info(f"Fetching daily time series for {symbol}")
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            data = response.json()
            
            # Check for API error messages
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                return None
            
            logger.info(f"Successfully fetched daily time series for {symbol}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

def test_alpha_vantage_api(ticker='AAPL'):
    """
    Test the Alpha Vantage API with a single ticker
    
    Args:
        ticker (str): Ticker symbol to test
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Testing Alpha Vantage API with ticker {ticker}")
        
        # Create API client
        client = AlphaVantageAPI()
        
        # Make request
        data = client.get_daily_time_series(ticker)
        
        if data is None:
            logger.error("Test failed: No data returned")
            return False
        
        # Check for expected data structure
        if 'Time Series (Daily)' not in data:
            logger.error(f"Test failed: Unexpected response structure: {json.dumps(data, indent=2)}")
            return False
        
        # Get the latest trading day data
        time_series = data['Time Series (Daily)']
        latest_date = list(time_series.keys())[0]
        latest_data = time_series[latest_date]
        
        # Log the results
        logger.info(f"Test successful! Latest data for {ticker} on {latest_date}:")
        logger.info(f"Open: {latest_data['1. open']}")
        logger.info(f"High: {latest_data['2. high']}")
        logger.info(f"Low: {latest_data['3. low']}")
        logger.info(f"Close: {latest_data['4. close']}")
        logger.info(f"Volume: {latest_data['5. volume']}")
        
        # Save sample data to a file
        output_dir = 'data/raw'
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{ticker}_daily_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Sample data saved to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    # If run as a script, test the API
    import sys
    
    ticker = 'AAPL'
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    
    success = test_alpha_vantage_api(ticker)
    sys.exit(0 if success else 1)
