import numpy as np
import pandas as pd
import yfinance as yf

from datetime import date, datetime
from typing import List, Tuple, Optional

from phase0.utils import logger
from phase0.utils import check_cached_datasets, save_dataset

def download_stock_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str
) -> Optional[pd.DataFrame]:
    """
    Download stock data using yfinance.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval

    Returns:
        The stock data as a DataFrame.
    """
    try:
        start_dt: date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt: date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        logger.info(msg=f"Downloading stock data for '{symbol}' from {start_date} to {end_date} with {interval} interval")
        stock_data: Optional[pd.DataFrame] = yf.download(
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
    
    except Exception as e:
        logger.error(msg=f"Error in download_stock_data: {e}")
        return None

def preprocess_stock_data(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Clean and prepare stock data for analysis.
    
    Args:
        data: Raw stock data from yfinance
        symbol: Stock symbol for logging
    
    Returns:
        Cleaned DataFrame
    """
    cleaned: pd.DataFrame = data.copy()
    
    logger.info(msg=f"Raw data columns: {list(cleaned.columns)}")
    logger.info(msg=f"Raw data shape: {cleaned.shape}")
    logger.info(msg=f"Raw data head:\n{cleaned.head()}")
    
    if not isinstance(cleaned.index, pd.DatetimeIndex):
        cleaned.index = pd.to_datetime(cleaned.index)
    
    if isinstance(cleaned.columns, pd.MultiIndex):
        logger.info(msg="Detected MultiIndex columns, flattening...")
        cleaned.columns = cleaned.columns.get_level_values(level=0)
        logger.info(msg=f"Flattened columns: {list(cleaned.columns)}")
    
    expected_columns: List[str] = ["Open", "High", "Low", "Close", "Volume"]
    available_columns: List[str] = list(cleaned.columns)
    
    missing_columns: List[str] = [col for col in expected_columns if col not in available_columns]
    if missing_columns:
        logger.warning(msg=f"Missing expected columns: {missing_columns}")
        logger.warning(msg=f"Available columns: {available_columns}")
        
        lowercase_columns: List[str] = [col.lower() for col in available_columns]
        for expected_col in missing_columns:
            if expected_col.lower() in lowercase_columns:
                actual_col: str = available_columns[lowercase_columns.index(expected_col.lower())]
                cleaned = cleaned.rename(columns={actual_col: expected_col})
                logger.info(msg=f"Renamed column '{actual_col}' to '{expected_col}'")
    
    missing_columns = [col for col in ["Open", "High", "Low", "Close"] if col not in cleaned.columns]
    if missing_columns:
        logger.error(msg=f"Cannot proceed: missing required columns: {missing_columns}")
        logger.error(msg=f"Available columns after processing: {list(cleaned.columns)}")
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    n_rows: int = len(cleaned)
    cleaned.dropna(subset=["Open", "High", "Low", "Close"], inplace=True)
    if len(cleaned) < n_rows:
        logger.info(msg=f"Removed {n_rows - len(cleaned)} rows with missing OHLC data!")
        n_rows = len(cleaned)
    
    cleaned = cleaned.loc[
        (cleaned['Open'] > 0) & 
        (cleaned['High'] > 0) & 
        (cleaned['Low'] > 0) & 
        (cleaned['Close'] > 0)
    ]
    if len(cleaned) < n_rows:
        logger.info(msg=f"Removed {n_rows - len(cleaned)} rows with zero or negative prices!")
        n_rows = len(cleaned)

    cleaned["Volume"] = cleaned["Volume"].fillna(0)
    cleaned.sort_index(inplace=True)
    
    logger.info(msg=f"Preprocessing completed. Final shape: {cleaned.shape}")
    return cleaned

def postprocess_stock_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add basic features to the stock data.
    
    Args:
        data: Cleaned stock data
    
    Returns:
        DataFrame with additional features
    """
    processed: pd.DataFrame = data.copy()

    processed["returns"] = processed["Close"].pct_change()
    processed["log_returns"] = np.log(processed["Close"] / processed["Close"].shift(1))

    processed["target_return"] = processed["returns"].shift(-1)
    processed["target_direction"] = (processed["target_return"] > 0).astype(int)

    processed["sma_5"] = processed["Close"].rolling(window=5).mean()
    processed["sma_20"] = processed["Close"].rolling(window=20).mean()

    processed["volatility_20"] = processed["returns"].rolling(window=20).std()

    processed["price_change"] = processed["Close"] - processed["Close"].shift(1)
    processed["price_change_pct"] = processed["price_change"] / processed["Close"].shift(1) * 100

    return processed

def get_stock_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    Download and process stock data for analysis.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval (default: '1d' for daily)
    
    Returns:
        Cleaned DataFrame with OHLCV data and returns
    """
    cached_dataset: Optional[pd.DataFrame] = check_cached_datasets(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    if cached_dataset is not None:
        return cached_dataset

    raw_data: Optional[pd.DataFrame] = download_stock_data(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    if raw_data is None:
        return None

    preprocessed: pd.DataFrame = preprocess_stock_data(
        data=raw_data,
        symbol=symbol
    )

    postprocessed: pd.DataFrame = postprocess_stock_data(
        data=preprocessed
    )
    save_dataset(
        data=postprocessed,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )

    return postprocessed

def create_walk_forward_splits(
    data: pd.DataFrame,
    train_size: int = 250, # aprox. 1 year of trading days
    test_size: int = 63, # aprox. 3 months of trading days
    step_size: int = 21 # aprox. 1 month step
) -> List[Tuple[int, int, int, int]]:
    """
    Create walk-forward splits for time series validation.
    
    Args:
        data: Stock data DataFrame
        train_size: Number of days for training
        test_size: Number of days for testing
        step_size: Number of days to step forward
    
    Returns:
        List of (train_start, train_end, test_start, test_end) tuples
    """
    splits: List[Tuple[int, int, int, int]] = []
    total_days: int = len(data)

    if total_days < train_size + test_size:
        logger.warning(msg=f"Insufficient data: {total_days} days, need at least {train_size + test_size}!")
        return splits

    for start_idx in range(0, total_days - train_size - test_size + 1, step_size):
        train_start: int = start_idx
        train_end: int = start_idx + train_size
        
        test_start: int = train_end
        test_end: int = min(test_start + test_size, total_days)

        splits.append((train_start, train_end, test_start, test_end))

    logger.info(msg=f"Created {len(splits)} walk-forward splits.")
    return splits

def get_split_data(
    data: pd.DataFrame,
    train_start: int,
    train_end: int,
    test_start: int,
    test_end: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get training and testing data for a specific split.
    
    Args:
        data: Full dataset
        train_start, train_end, test_start, test_end: Split indices
    
    Returns:
        Tuple of (train_data, test_data)
    """
    train_data: pd.DataFrame = data.iloc[train_start:train_end].copy()
    test_data: pd.DataFrame = data.iloc[test_start:test_end].copy()

    train_data.dropna(inplace=True)
    test_data.dropna(inplace=True)

    return train_data, test_data