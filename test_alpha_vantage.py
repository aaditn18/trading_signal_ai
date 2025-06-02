#!/usr/bin/env python3
"""
Test script for Alpha Vantage API
Usage: python test_alpha_vantage.py [ticker]
"""

import sys
from src.data_acquisition.fetch_data import test_alpha_vantage_api

if __name__ == "__main__":
    ticker = 'AAPL'
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    
    print(f"Testing Alpha Vantage API with ticker {ticker}...")
    print(f"Results will be logged to logs/pipeline.log")
    
    success = test_alpha_vantage_api(ticker)
    
    if success:
        print("Test successful! Check logs/pipeline.log for details.")
    else:
        print("Test failed. Check logs/pipeline.log for error details.")
    
    sys.exit(0 if success else 1) 