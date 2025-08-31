# Trading Stock Analysis Tool

A Python-based stock analysis tool that downloads stock data using yfinance and provides visualization and analysis capabilities.

## Features

- Download stock data with flexible date ranges and intervals
- Interactive plotting with matplotlib
- Moving average calculations
- Basic statistical analysis
- Command-line interface with various options
- Save plots to files
- Volume analysis

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Download and plot AAPL stock data for the last year
python main.py -s AAPL

# Download and plot MSFT stock data with custom date range
python main.py -s MSFT --start-date 2023-01-01 --end-date 2023-12-31

# Download data for a specific period
python main.py -s GOOGL --period 6mo
```

### Command Line Options

#### Required Parameters
- `-s, --symbol`: Stock symbol (e.g., AAPL, MSFT, GOOGL)

#### Optional Parameters

**Date Parameters:**
- `-sd, --start-date`: Start date (YYYY-MM-DD format, default: 1 year ago)
- `-ed, --end-date`: End date (YYYY-MM-DD format, default: today)
- `-p, --period`: Alternative to start/end dates (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

**Data Parameters:**
- `-i, --interval`: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo, default: 1d)

**Output Parameters:**
- `-o, --output`: Save plot to file (e.g., --output chart.png)
- `-np, --no-plot`: Skip plotting and only download data
- `-v, --verbose`: Enable verbose logging

**Analysis Parameters:**
- `-ss, --show-stats`: Display basic statistics about the stock data
- `-ma, --moving-averages`: Show moving averages for specified periods (default: 20, 50)

### Examples

```bash
# Download AAPL data for the last 6 months with 20 and 200-day moving averages
python main.py -s AAPL --period 6mo --moving-averages 20 200

# Download MSFT data for 2023 and save the plot
python main.py -s MSFT --start-date 2023-01-01 --end-date 2023-12-31 --output msft_2023.png

# Download GOOGL data with 5-minute intervals (requires paid subscription)
python main.py -s GOOGL --period 5d --interval 5m

# Download TSLA data and show statistics without plotting
python main.py -s TSLA --show-stats --no-plot

# Download NVDA data with verbose logging
python main.py -s NVDA --verbose --show-stats
```

## Notes

- Intraday data (intervals < 1d) may require a paid yfinance subscription
- The script automatically handles date format conversion
- Moving averages are only shown if there's enough data for the specified period
- Plots include both price data and volume information
- All dates should be in YYYY-MM-DD format

## Dependencies

- yfinance: Yahoo Finance data downloader
- pandas: Data manipulation and analysis
- matplotlib: Plotting and visualization
- argparse: Command-line argument parsing
