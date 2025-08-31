import os
import numpy as np
import pandas as pd
from datetime import datetime

from typing import Dict, List, Optional, Tuple

from phase0.utils import Number, logger
from phase0.backtesting import WalkForwardBackTester
from phase0.data_preparation import get_stock_data, create_walk_forward_splits

from phase0.utils import SYMBOL, START_DATE, END_DATE, RESULTS_PATH

def main() -> None:
    """
    Main function for Phase 0 implementation.
    """
    logger.info(msg="Starting Phase 0: Data Preparation and Environment Setup.")

    logger.info(msg="Step 1: Downloading and Cleaning data.")
    stock_data: Optional[pd.DataFrame] = get_stock_data(
        symbol=SYMBOL,
        start_date=START_DATE,
        end_date=END_DATE
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
    timestamp: str = datetime.now().strftime(format="%Y%m%d_%H%M%S")
    os.mkdir(path=f"{RESULTS_PATH}/{timestamp}")

    summary.to_csv(f"{RESULTS_PATH}/{timestamp}/baseline_results.csv", index=False)
    
    for model_name, results in baseline_results.items():
        if results:
            df: pd.DataFrame = pd.DataFrame(data=results)
            df.to_csv(f"{RESULTS_PATH}/{timestamp}/{model_name}_detailed.csv", index=False)
            logger.info(msg=f"Saved detailed results for {model_name}")
    
    logger.info(msg=f"Results saved with timestamp: {timestamp}")

    logger.info(msg="Step 8: Final assessment")
    
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
    
    logger.info(msg="Phase 0 completed successfully!")

if __name__ == "__main__":
    main()