#!/usr/bin/env python3
"""
Script to clean the database by removing Apple data and verifying 
the remaining tickers have complete data with no NULL values
"""

import sys
import sqlite3
import pandas as pd
from tabulate import tabulate
from datetime import datetime

from src.data_acquisition.create_database import DB_PATH
from src.utils.file_io import get_db_connection
from src.utils.logger import logger

def delete_ticker_data(ticker):
    """
    Delete all data for a specific ticker from the database
    
    Args:
        ticker (str): Ticker symbol to delete
        
    Returns:
        int: Number of records deleted
    """
    try:
        conn = get_db_connection(DB_PATH)
        cursor = conn.cursor()
        
        # Get record count before deletion
        cursor.execute("SELECT COUNT(*) as count FROM ohlcv WHERE ticker = ?", (ticker,))
        count_before = cursor.fetchone()['count']
        
        # Delete records
        cursor.execute("DELETE FROM ohlcv WHERE ticker = ?", (ticker,))
        conn.commit()
        
        # Check if records were deleted
        cursor.execute("SELECT COUNT(*) as count FROM ohlcv WHERE ticker = ?", (ticker,))
        count_after = cursor.fetchone()['count']
        
        deleted_count = count_before - count_after
        print(f"Deleted {deleted_count} records for {ticker}")
        logger.info(f"Deleted {deleted_count} records for {ticker}")
        
        conn.close()
        return deleted_count
        
    except Exception as e:
        print(f"Error deleting data for {ticker}: {str(e)}")
        logger.error(f"Error deleting data for {ticker}: {str(e)}")
        return 0

def check_for_null_values():
    """
    Check for NULL values in the database
    
    Returns:
        bool: True if no NULL values found, False otherwise
    """
    try:
        conn = get_db_connection(DB_PATH)
        cursor = conn.cursor()
        
        # Check for NULL values in any column
        cursor.execute("""
        SELECT ticker, date, COUNT(*) as count
        FROM ohlcv
        WHERE ticker IS NULL OR date IS NULL OR open IS NULL 
           OR high IS NULL OR low IS NULL OR close IS NULL OR volume IS NULL
        GROUP BY ticker, date
        """)
        
        null_records = cursor.fetchall()
        
        if null_records:
            print("Found NULL values in the following records:")
            for record in null_records:
                print(f"Ticker: {record['ticker']}, Date: {record['date']}, Count: {record['count']}")
            
            conn.close()
            return False
        else:
            print("No NULL values found in the database.")
            conn.close()
            return True
        
    except Exception as e:
        print(f"Error checking for NULL values: {str(e)}")
        return False

def analyze_tickers():
    """
    Analyze all tickers in the database and display statistics
    
    Returns:
        int: Number of tickers found
    """
    try:
        conn = get_db_connection(DB_PATH)
        cursor = conn.cursor()
        
        # Get list of all tickers
        cursor.execute("SELECT DISTINCT ticker FROM ohlcv ORDER BY ticker")
        tickers = [row['ticker'] for row in cursor.fetchall()]
        
        # Count total records
        cursor.execute("SELECT COUNT(*) as count FROM ohlcv")
        total_count = cursor.fetchone()['count']
        
        print(f"Database contains {total_count} total records across {len(tickers)} tickers")
        
        # Check if AAPL is in the list
        if 'AAPL' in tickers:
            print("WARNING: AAPL is still in the database")
        else:
            print("AAPL has been successfully removed from the database")
        
        # Create a list to store ticker data
        ticker_data = []
        
        # Get stats for each ticker
        for ticker in tickers:
            # Get earliest date
            cursor.execute(
                "SELECT date FROM ohlcv WHERE ticker = ? ORDER BY date ASC LIMIT 1", 
                (ticker,)
            )
            earliest_date = cursor.fetchone()['date']
            
            # Get latest date
            cursor.execute(
                "SELECT date FROM ohlcv WHERE ticker = ? ORDER BY date DESC LIMIT 1", 
                (ticker,)
            )
            latest_date = cursor.fetchone()['date']
            
            # Get total records
            cursor.execute(
                "SELECT COUNT(*) as count FROM ohlcv WHERE ticker = ?", 
                (ticker,)
            )
            record_count = cursor.fetchone()['count']
            
            # Add to list
            ticker_data.append({
                'Ticker': ticker,
                'First Date': earliest_date,
                'Last Date': latest_date,
                'Total Records': record_count
            })
        
        # Create DataFrame for nice display
        df = pd.DataFrame(ticker_data)
        
        # Print table
        print("\nTicker Statistics:")
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        
        conn.close()
        return len(tickers)
        
    except Exception as e:
        print(f"Error analyzing tickers: {str(e)}")
        return 0

if __name__ == "__main__":
    print("Starting database cleanup...")
    
    # Delete Apple data
    print("\n1. Removing Apple (AAPL) data from the database")
    deleted_count = delete_ticker_data('AAPL')
    
    # Check for NULL values
    print("\n2. Checking for NULL values in the database")
    no_nulls = check_for_null_values()
    
    # Analyze remaining tickers
    print("\n3. Analyzing remaining tickers")
    ticker_count = analyze_tickers()
    
    # Print summary
    print("\nSummary:")
    print(f"- Deleted {deleted_count} Apple records")
    print(f"- Database has {ticker_count} tickers (should be 21)")
    print(f"- NULL values: {'None found' if no_nulls else 'Found - see above'}")
    
    if ticker_count == 21 and no_nulls:
        print("\nDatabase cleanup successful!")
    else:
        print("\nDatabase cleanup completed with issues. See details above.") 