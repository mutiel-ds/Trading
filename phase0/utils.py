import os
import logging
import pandas as pd
from numpy import floating
from logging import Logger, getLogger, basicConfig

from typing import TypeAlias, Optional

basicConfig(level="INFO")
logger: Logger = getLogger(name="phase0")

Number: TypeAlias = int | float | floating

SYMBOL = "AAPL"
START_DATE = "2020-01-01"
END_DATE = "2025-01-01"

RESULTS_PATH = "phase0/results"
DATASETS_PATH = "datasets"

def dataset_path(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str
) -> str:
    """
    Construct dataset path in dataset.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval (default: '1d' for daily)

    Returns:
        Dataset path for the given request.
    """
    if not os.path.exists(path=DATASETS_PATH):
        logger.info(msg=f"Creating '{DATASETS_PATH}' directory!")
        os.mkdir(path=DATASETS_PATH)

    path: str = f"{DATASETS_PATH}/{symbol}/"
    if not os.path.exists(path=path):
        logger.info(msg=f"Creating '{path}' directory!")
        os.mkdir(path=path)

    path += f"{start_date.replace('-', '')}_{end_date.replace('-', '')}_{interval}.csv"
    return path

def check_cached_datasets(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str
) -> Optional[pd.DataFrame]:
    """
    Check if the requested data has already been downloaded and is in cache.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval (default: '1d' for daily)

    Returns:
        The cached data if available.
    """
    path: str = dataset_path(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    try:
        logger.info(msg="Searching dataset from cache!")
        dataset: pd.DataFrame = pd.read_csv(path)
        logger.info(msg="Dataset found in cache!")
        return dataset
    
    except FileNotFoundError:
        logger.info(msg="Dataset not found in cache, retrieving it!")
        return None

def save_dataset(
    data: pd.DataFrame,
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str
) -> bool:
    """
    Stores data in cache.

    Args:
        data: Pandas DataFrame object containing processed stock data
        symbol: Stock symbol (e.g., 'AAPL')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval (default: '1d' for daily)

    Returns:
        A boolean indicating whether it was succesffully stored or not.
    """
    path: str = dataset_path(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    try:
        logging.info(msg="Trying to save data in the cache!")
        data.to_csv(path)
        logging.info(msg="Succesfully stored data in cache!")
        return True

    except Exception as e:
        logging.warning(msg=f"An error ocurred while storing data in cache: {e}")
        return False