import pandas as pd
from typing import Dict, List, Optional, Tuple

from phase0.utils import Number, logger, Namespace
from phase0.backtesting import WalkForwardBackTester
from phase0.utils import parse_arguments, save_results, final_assessment
from phase0.data_preparation import get_stock_data, create_walk_forward_splits

from phase0.utils import RESULTS_PATH

def main() -> None:
    """
    Main function for Phase 0 implementation.
    """
    logger.info(msg="Starting Phase 0: Data Preparation and Environment Setup.")

    logger.info(msg="Step 0: Setting up variables!")
    args: Namespace = parse_arguments()

    logger.info(msg="Step 1: Downloading and Cleaning data.")
    stock_data: Optional[pd.DataFrame] = get_stock_data(
        symbol=args.symbol,
        start_date=args.start_date,
        end_date=args.end_date,
        interval=args.interval
    )

    if stock_data is None:
        logger.error(msg="Failed to download data. Exiting.")
        return

    logger.info(msg=f"Dataset shape: {stock_data.shape}")
    logger.info(msg=f"Date range: {stock_data.index[0]} to {stock_data.index[-1]}")
    logger.info(msg=f"Columns: {list(stock_data.columns)}")

    logger.info(msg="Step 2: Creating walk-forward splits.")
    splits: List[Tuple[int, int, int, int]] = create_walk_forward_splits(data=stock_data)
    
    if not splits:
        logger.error(msg="Failed to create splits. Exiting.")
        return

    logger.info(msg="Step 3: Initializing backtester.")
    backtester: WalkForwardBackTester = WalkForwardBackTester(data=stock_data, splits=splits)

    logger.info(msg="Step 4: Running baseline models.")
    baseline_results: Dict[str, List[Dict[str, Number]]] = backtester.run_baseline_models()

    logger.info(msg="Step 5: Summarizing results.")
    summary: pd.DataFrame = backtester.summarize_results(results=baseline_results)

    print("\n" + "="*60)
    print("ETAPA 0 - RESULTADOS DE BASELINES")
    print("="*60)
    print(summary.to_string(index=False))
    print("="*60)

    logger.info(msg="Step 6: Creating visualization.")
    backtester.plot_results(results=baseline_results, metric='mae')
    backtester.plot_results(results=baseline_results, metric='directional_accuracy')

    logger.info(msg="Step 7: Saving results")
    save_results(
        symbol=args.symbol,
        summary=summary,
        baseline_results=baseline_results
    )

    logger.info(msg="Step 8: Final assessment")
    final_assessment(baseline_results=baseline_results)
    
    logger.info(msg="Phase 0 completed successfully!")

if __name__ == "__main__":
    main()