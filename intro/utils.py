from typing import TypeAlias
from datetime import date, timedelta
from logging import Logger, getLogger, basicConfig
from argparse import Namespace, ArgumentParser, ArgumentDefaultsHelpFormatter

basicConfig(level="INFO")
logger: Logger = getLogger(name="intro")

Number: TypeAlias = int | float

def parse_arguments() -> Namespace:
    """
    Parse command line arguments.
    """
    parser: ArgumentParser = ArgumentParser(
        description="Download and analyze stock data using yfinance",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    
    # Mandatory parameter
    parser.add_argument(
        "-s", "--symbol",
        required=True,
        help="Stock symbol to download (e.g., AAPL, MSFT, GOOGL)"
    )
    
    # Date parameters
    parser.add_argument(
        "-sd", "--start-date",
        type=str,
        default=(date.today() - timedelta(days=365)).strftime(format="%Y-%m-%d"),
        help="Start date for data download (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        "-ed", "--end-date",
        type=str,
        default=date.today().strftime(format="%Y-%m-%d"),
        help="End date for data download (YYYY-MM-DD format)"
    )
    
    # Data parameters
    parser.add_argument(
        "-i", "--interval",
        choices=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"],
        default="1d",
        help="Data interval (note: intraday data < 1d requires paid subscription)"
    )
    
    parser.add_argument(
        "-p", "--period",
        choices=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
        help="Alternative to start/end dates - period to download"
    )
    
    # Output parameters
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Save plot to file (e.g., --output chart.png)"
    )
    
    parser.add_argument(
        "-np", "--no-plot",
        action="store_true",
        help="Skip plotting and only download data"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Analysis parameters
    parser.add_argument(
        "-ss", "--show-stats",
        action="store_true",
        help="Display basic statistics about the stock data"
    )
    
    parser.add_argument(
        "-ma", "--moving-averages",
        nargs="+",
        type=int,
        default=[20, 50],
        help="Show moving averages for specified periods (e.g., --moving-averages 20 50 200)"
    )
    
    return parser.parse_args()
