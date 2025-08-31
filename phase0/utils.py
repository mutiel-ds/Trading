import os
import numpy as np
import pandas as pd
from numpy import floating

from datetime import datetime
from typing import TypeAlias, Optional, List, Dict
from logging import Logger, getLogger, basicConfig
from argparse import Namespace, ArgumentParser, ArgumentDefaultsHelpFormatter

basicConfig(level="INFO")
logger: Logger = getLogger(name="phase0")

Number: TypeAlias = int | float | floating

SYMBOL = "AAPL"
START_DATE = "2020-01-01"
END_DATE = "2025-01-01"
INTERVAL = "1d"

RESULTS_PATH = "phase0/results"
DATASETS_PATH = "datasets"

def parse_arguments() -> Namespace:
    """
    Parse command line arguments.
    """
    parser: ArgumentParser = ArgumentParser(
        description="Download and analyze stock data using yfinance",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    
    # Symbol parameter
    parser.add_argument(
        "-s", "--symbol",
        help="Stock symbol to download (e.g., AAPL, MSFT, GOOGL)",
        default=SYMBOL
    )
    
    # Date parameters
    parser.add_argument(
        "-sd", "--start-date",
        type=str,
        default=START_DATE,
        help="Start date for data download (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        "-ed", "--end-date",
        type=str,
        default=END_DATE,
        help="End date for data download (YYYY-MM-DD format)"
    )
    
    # Data parameters
    parser.add_argument(
        "-i", "--interval",
        choices=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"],
        default=INTERVAL,
        help="Data interval (note: intraday data < 1d requires paid subscription)"
    )
    
    return parser.parse_args()

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
        logger.info(msg="Trying to save data in the cache!")
        data.to_csv(path)
        logger.info(msg="Succesfully stored data in cache!")
        return True

    except Exception as e:
        logger.warning(msg=f"An error ocurred while storing data in cache: {e}")
        return False

def save_results(
    symbol: str,
    summary: pd.DataFrame,
    baseline_results: Dict[str, List[Dict[str, Number]]]
) -> None:
    """
    Stores the models results.

    Args:
        summary: Summary of the baseline results of the models
        baseline_results: Detailed results of each model
    """
    path: str = f"{RESULTS_PATH}/{symbol}"
    if not os.path.exists(path=path):
        os.mkdir(path=path)
    
    timestamp: str = datetime.now().strftime(format="%Y%m%d_%H%M%S")
    path += f"/{timestamp}"
    os.mkdir(path=path)

    summary.to_csv(f"{path}/baseline_results.csv", index=False)
    
    for model_name, results in baseline_results.items():
        if results:
            df: pd.DataFrame = pd.DataFrame(data=results)
            df.to_csv(f"{path}/{model_name}_detailed.csv", index=False)
            logger.info(msg=f"Saved detailed results for {model_name}")
    
    logger.info(msg=f"Results saved with timestamp: {timestamp}")

def final_assessment(baseline_results: Dict[str, List[Dict[str, Number]]]) -> None:
    """
    Shows the final assessment of the obtained results in the terminal.

    Args:
        baseline_results: Detailed results of each model
    """
    print("\n" + "="*60)
    print("EVALUACIÓN FINAL - ETAPA 0")
    print("="*60)

    working_models: List = []
    for model_name, results in baseline_results.items():
        if results and len(results) > 0:
            working_models.append(model_name)
            avg_mae: Number = np.mean([float(r['mae']) for r in results])
            avg_direction: Number = np.mean([float(r['directional_accuracy']) for r in results])
            print(f"✓ {model_name}: MAE={avg_mae:.2f}, Directional Accuracy={avg_direction:.1f}%")
        else:
            print(f"✗ {model_name}: No results")
    
    if len(working_models) >= 2:
        print(f"\n✅ ÉXITO: {len(working_models)} baselines funcionando correctamente")
        print("✅ Criterio para pasar a Etapa 1: CUMPLIDO")
    else:
        print(f"\n❌ PROBLEMA: Solo {len(working_models)} baselines funcionando")
        print("❌ Criterio para pasar a Etapa 1: NO CUMPLIDO")
    
    print("="*60)