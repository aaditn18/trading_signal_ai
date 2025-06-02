#!/usr/bin/env python3
"""
Analyze database contents to show detailed information for each ticker
Shows earliest date, latest date, and number of records for each ticker
"""

import sqlite3
import sys
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta

from src.data_acquisition.create_database import DB_PATH
from src.utils.file_io import get_db_connection

def analyze_database():
    """Analyze the database contents and display statistics"""
    try:
        # Connect to the database
        conn = get_db_connection(DB_PATH)
        cursor = conn.cursor()
        
        # Get list of all tickers
        cursor.execute("SELECT DISTINCT ticker FROM ohlcv ORDER BY ticker")
        tickers = [row['ticker'] for row in cursor.fetchall()]
        
        # Count total records
        cursor.execute("SELECT COUNT(*) as count FROM ohlcv")
        total_count = cursor.fetchone()['count']
        
        print(f"Database contains {total_count} total records across {len(tickers)} tickers\n")
        
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
            
            # Calculate date range
            start_date = datetime.strptime(earliest_date, '%Y-%m-%d')
            end_date = datetime.strptime(latest_date, '%Y-%m-%d')
            date_range_days = (end_date - start_date).days
            
            # Calculate trading days per year (approx 252 trading days per year)
            years = date_range_days / 365.0
            expected_records = int(years * 252)
            completeness = record_count / expected_records if expected_records > 0 else 0
            
            # Get recent records (last 3 years)
            three_years_ago = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
            cursor.execute(
                "SELECT COUNT(*) as count FROM ohlcv WHERE ticker = ? AND date >= ?", 
                (ticker, three_years_ago)
            )
            recent_count = cursor.fetchone()['count']
            
            # Add to list
            ticker_data.append({
                'Ticker': ticker,
                'First Date': earliest_date,
                'Last Date': latest_date,
                'Total Records': record_count,
                'Date Range (days)': date_range_days,
                'Completeness': f"{completeness:.1%}",
                'Recent Records (3yr)': recent_count
            })
        
        # Create DataFrame for nice display
        df = pd.DataFrame(ticker_data)
        
        # Print table
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"Error analyzing database: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Analyzing database contents...\n")
    analyze_database() 