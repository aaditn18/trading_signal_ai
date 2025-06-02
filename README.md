# Trading Signal AI

A machine learning-based system for generating trading signals based on market data, technical indicators, and sentiment analysis.

## Project Structure

```
trading_signal_ai/
│
├── data/                     # All raw and processed data
│   ├── raw/                 # Raw OHLCV and news data
│   ├── processed/           # Cleaned and feature-engineered datasets
│   └── news/                # News articles and sentiment data
│
├── configs/                 # Configuration files
│   ├── tickers.yaml         # List of stock tickers
│   └── data_sources.yaml    # API keys and data source settings
│
├── models/                  # Saved machine learning models
│
├── signals/                 # Output signals (buy/sell/hold)
│
├── logs/                    # Debug and execution logs
│
├── notebooks/               # Jupyter notebooks for research
│
├── tests/                   # Unit tests
│
└── src/                     # Core source code
    ├── data_acquisition/    # Data scraping & loading
    ├── feature_engineering/ # Feature generation
    ├── technical_indicators/# Technical analysis
    ├── ml_models/           # Predictive models
    ├── time_series/         # ARIMA/Prophet forecasting
    ├── sentiment_analysis/  # News sentiment modeling
    ├── quant_models/        # Finance theory models
    ├── signal_aggregator/   # Combines signals via ML
    ├── backtesting/         # Strategy simulation
    ├── notification/        # Alert system
    └── utils/               # Shared utilities
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/trading_signal_ai.git
   cd trading_signal_ai
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Configuration

1. Update the ticker list in `configs/tickers.yaml`
2. Add your API keys in `configs/data_sources.yaml`

### Testing the API Connection

Run the provided test script to verify your Alpha Vantage API key is working:

```
python test_alpha_vantage.py AAPL
```

Results will be logged to `logs/pipeline.log` and sample data will be saved to `data/raw/`.

## License

MIT

## Acknowledgments

- Alpha Vantage for market data API
