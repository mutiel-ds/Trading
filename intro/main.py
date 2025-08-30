from argparse import Namespace
from typing import Optional, Any
from datetime import datetime, date

import pandas as pd
import yfinance as yf
from numpy import ndarray
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from intro.utils import logger, basicConfig
from intro.utils import parse_arguments, Number

def download_stock_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str,
    period: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Download stock data using yfinance.

    Args:
        symbol: The stock symbol to download data for.
        start_date: The start date for the data download.
        end_date: The end date for the data download.
        interval: The interval for the data download.
        period: The period for the data download.

    Returns:
        The stock data as a DataFrame.
    """
    try:
        start_dt: date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt: date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        logger.info(msg=f"Downloading stock data for '{symbol}' from {start_date} to {end_date} with {interval} interval")
        stock_data: Optional[pd.DataFrame] = yf.download(
                tickers=symbol,
                period=period,
                interval=interval,
                auto_adjust=True
            ) if period else yf.download(
                tickers=symbol,
                start=start_dt,
                end=end_dt,
                interval=interval,
                auto_adjust=True
            )
        
        if (stock_data is None) or (stock_data.empty):
            logger.error(msg=f"No stock data found for '{symbol}'!")
            return None

        logger.info(msg=f"Successfully downloaded {len(stock_data)} rows of stock data for '{symbol}'")
        return stock_data
        
    except ValueError as e:
        logger.error(msg=f"Invalid date format: {e}")
        return None
    except Exception as e:
        logger.error(msg=f"Error downloading data: {e}")
        return None

def display_statistics(
    stock_data: pd.DataFrame,
    symbol: str
) -> None:
    """
    Display basic statistics about the stock data.

    Args:
        stock_data: The stock data to display statistics for.
        symbol: The symbol of the stock to display statistics for.
    """
    print(f"\n=== Statistics for {symbol} ===")
    if not isinstance(stock_data.index, pd.DatetimeIndex):
        stock_data.index = pd.to_datetime(stock_data.index)
    
    start_date: pd.Index | str = stock_data.index[0].strftime('%Y-%m-%d') if hasattr(stock_data.index[0], 'strftime') else str(stock_data.index[0])
    end_date: pd.Index | str = stock_data.index[-1].strftime('%Y-%m-%d') if hasattr(stock_data.index[-1], 'strftime') else str(stock_data.index[-1])
    
    print(f"Data period: {start_date} to {end_date}")
    print(f"Total trading days: {len(stock_data)}")
    
    # Get numeric values safely    
    current_price: Number = stock_data['Close'].iloc[-1].item()
    print(f"Current price: ${current_price:.2f}")

    initial_price: Number = stock_data['Close'].iloc[0].item()
    price_change: Number = current_price - initial_price
    print(f"Price change: ${price_change:.2f}")

    price_change_pct: Number = ((current_price / initial_price) - 1) * 100
    print(f"Price change %: {price_change_pct:.2f}%")

    highest_price: Any = stock_data['High'].max()
    highest_price_float: Number = float(highest_price.iloc[0]) if not isinstance(highest_price, Number) else highest_price
    print(f"Highest price: ${highest_price_float:.2f}")
    
    
    lowest_price: Any = stock_data['Low'].min()
    lowest_price_float: Number = float(lowest_price.iloc[0]) if not isinstance(lowest_price, Number) else lowest_price
    print(f"Lowest price: ${lowest_price_float:.2f}")

    avg_volume: Any = stock_data['Volume'].mean()
    avg_volume_float: Number = float(avg_volume.iloc[0]) if not isinstance(avg_volume, Number) else avg_volume
    print(f"Average volume: {avg_volume_float:.0f}")

def plot_stock_data(
    stock_data: pd.DataFrame,
    symbol: str,
    moving_averages: list,
    output_file: Optional[str] = None
) -> None:
    """
    Plot stock data with optional moving averages.

    Args:
        stock_data: The stock data to plot.
        symbol: The symbol of the stock to plot.
        moving_averages: The moving averages to plot.
        output_file: Where to save the plot if needed.
    """
    plt.figure(figsize=(14, 8))
    plt.plot(stock_data.index, stock_data["Close"], label=f"{symbol} Close Price", linewidth=2)
    
    for period in moving_averages:
        if len(stock_data) >= period:
            ma: Any = stock_data["Close"].rolling(window=period).mean()
            plt.plot(stock_data.index, ma, label=f"{period}-day MA", alpha=0.7, linewidth=1.5)
    
    ax1: Axes = plt.gca()
    ax2: Axes = ax1.twinx()
    try:
        volume_col: pd.DataFrame | pd.Series = stock_data["Volume"]
        if hasattr(volume_col, "to_numpy"):
            volume_data: ndarray = volume_col.to_numpy()
        else:
            volume_data = pd.Series(data=volume_col).to_numpy()

        volume: pd.Series = pd.Series(data=volume_data).fillna(0)
        ax2.bar(x=stock_data.index, height=volume, alpha=0.3, color="gray", label="Volume")

    except Exception as e:
        logger.warning(msg=f"Could not plot volume data: {e}")
    
    plt.title(label=f"{symbol} Stock Price Evolution", fontsize=16, fontweight="bold")
    ax1.set_xlabel(xlabel="Date", fontsize=12)
    ax1.set_ylabel(ylabel="Price (USD)", fontsize=12)
    ax2.set_ylabel(ylabel="Volume", fontsize=12)
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    
    plt.grid(visible=True, alpha=0.3)
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        logger.info(msg=f"Plot saved to {output_file}")
    
    plt.show()

def main() -> None:
    """Main function to run the stock analysis."""
    args: Namespace = parse_arguments()
    
    # Set logging level
    if args.verbose:
        basicConfig(level="DEBUG")
    
    # Download stock data
    stock_data: Optional[pd.DataFrame] = download_stock_data(
        symbol=args.symbol,
        start_date=args.start_date,
        end_date=args.end_date,
        interval=args.interval,
        period=args.period
    )
    
    if stock_data is None:
        logger.error(msg="Failed to download stock data. Exiting.")
        return
    
    # Display statistics if requested
    if args.show_stats:
        display_statistics(stock_data, args.symbol)
    
    # Plot data unless --no-plot is specified
    if not args.no_plot:
        plot_stock_data(
            stock_data=stock_data,
            symbol=args.symbol,
            moving_averages=args.moving_averages,
            output_file=args.output
        )

if __name__ == "__main__":
    main()