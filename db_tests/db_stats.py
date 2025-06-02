#!/usr/bin/env python3
"""
Enhanced database statistics visualization script
Shows detailed statistics for each ticker in the database
"""

import sys
import os
import sqlite3
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta

# Add the project root to sys.path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_acquisition.create_database import DB_PATH
from src.utils.file_io import get_db_connection

def get_database_statistics():
    """
    Get comprehensive statistics about the database
    """
    try:
        conn = get_db_connection(DB_PATH)
        cursor = conn.cursor()
        
        # Get total record count and ticker count
        cursor.execute("SELECT COUNT(*) as count FROM ohlcv")
        total_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT ticker) as count FROM ohlcv")
        ticker_count = cursor.fetchone()['count']
        
        # Get list of all tickers
        cursor.execute("SELECT DISTINCT ticker FROM ohlcv ORDER BY ticker")
        tickers = [row['ticker'] for row in cursor.fetchall()]
        
        # Get global date range
        cursor.execute("SELECT MIN(date) as min_date, MAX(date) as max_date FROM ohlcv")
        global_range = cursor.fetchone()
        
        # Print summary
        print("=" * 80)
        print(f"DATABASE SUMMARY")
        print("=" * 80)
        print(f"Total Records: {total_count:,}")
        print(f"Total Tickers: {ticker_count}")
        print(f"Date Range: {global_range['min_date']} to {global_range['max_date']}")
        print(f"Oldest data is from: {global_range['min_date']} ({(datetime.now() - datetime.strptime(global_range['min_date'], '%Y-%m-%d')).days} days ago)")
        print("=" * 80)
        
        # Get ticker statistics
        ticker_stats = []
        for ticker in tickers:
            # Get ticker data range
            cursor.execute("""
            SELECT 
                MIN(date) as first_date,
                MAX(date) as last_date,
                COUNT(*) as record_count,
                AVG(open) as avg_open,
                AVG(close) as avg_close,
                MAX(high) as max_high,
                MIN(low) as min_low,
                SUM(volume) as total_volume,
                AVG(volume) as avg_volume
            FROM ohlcv
            WHERE ticker = ?
            """, (ticker,))
            
            stats = cursor.fetchone()
            
            # Calculate date range
            first_date = datetime.strptime(stats['first_date'], '%Y-%m-%d')
            last_date = datetime.strptime(stats['last_date'], '%Y-%m-%d')
            date_range_days = (last_date - first_date).days
            
            # Calculate completeness
            # Assuming 252 trading days per year (standard in finance)
            years = date_range_days / 365.0
            expected_trading_days = int(years * 252)
            completeness = stats['record_count'] / expected_trading_days if expected_trading_days > 0 else 0
            
            # Get recent records (3 years)
            three_years_ago = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
            cursor.execute("""
            SELECT COUNT(*) as count 
            FROM ohlcv 
            WHERE ticker = ? AND date >= ?
            """, (ticker, three_years_ago))
            recent_count = cursor.fetchone()['count']
            
            # Get year-to-date records
            ytd = datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')
            cursor.execute("""
            SELECT COUNT(*) as count 
            FROM ohlcv 
            WHERE ticker = ? AND date >= ?
            """, (ticker, ytd))
            ytd_count = cursor.fetchone()['count']
            
            # Add to statistics list
            ticker_stats.append({
                'Ticker': ticker,
                'First Date': stats['first_date'],
                'Last Date': stats['last_date'],
                'Days of History': date_range_days,
                'Years of Data': f"{years:.1f}",
                'Total Records': stats['record_count'],
                'Completeness': f"{completeness:.1%}",
                '3yr Records': recent_count,
                'YTD Records': ytd_count,
                'Avg Close': f"${stats['avg_close']:.2f}",
                'High': f"${stats['max_high']:.2f}",
                'Low': f"${stats['min_low']:.2f}",
                'Avg Volume': f"{stats['avg_volume']:,.0f}"
            })
            
        # Create DataFrame
        df = pd.DataFrame(ticker_stats)
        
        # Split into batches of 7 tickers for readability
        batch_size = 7
        
        for i in range(0, len(tickers), batch_size):
            batch_tickers = tickers[i:i+batch_size]
            batch_df = df[df['Ticker'].isin(batch_tickers)]
            
            # First table - Basic ticker info
            print(f"\nTICKER DATA SUMMARY (BATCH {i//batch_size + 1}/{(len(tickers)-1)//batch_size + 1})")
            print("-" * 80)
            print(tabulate(
                batch_df[['Ticker', 'First Date', 'Last Date', 'Days of History', 'Years of Data', 'Total Records', 'Completeness']],
                headers='keys',
                tablefmt='pretty',
                showindex=False
            ))
            
            # Second table - Recent data and statistics
            print(f"\nTICKER RECENT DATA & PRICE STATISTICS (BATCH {i//batch_size + 1}/{(len(tickers)-1)//batch_size + 1})")
            print("-" * 80)
            print(tabulate(
                batch_df[['Ticker', '3yr Records', 'YTD Records', 'Avg Close', 'High', 'Low', 'Avg Volume']],
                headers='keys',
                tablefmt='pretty',
                showindex=False
            ))
            
            # Add separator between batches
            if i + batch_size < len(tickers):
                print("\n" + "=" * 80)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error getting database statistics: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Generating detailed database statistics...\n")
    get_database_statistics() 