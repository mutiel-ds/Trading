import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

from numpy import floating
from typing import Dict, List, Tuple, Any, Callable


from phase0.utils import logger, Number
from phase0.data_preparation import get_split_data

class WalkForwardBackTester:
    """
    Walk-forward backtesting framework for time series models.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        splits: List[Tuple[int, int, int, int]]
    ) -> None:
        self.data: pd.DataFrame = data
        self.splits: List[Tuple[int, int, int, int]] = splits
        self.results: List = []

    def _calculate_metrics(
        self,
        actual: pd.Series,
        predicted: pd.Series,
        target_returns: pd.Series
    ) -> Dict[str, Number]:
        """
        Calculate evaluation metrics.
        
        Args:
            actual: Actual prices
            predicted: Predicted prices
            target_returns: Actual returns for directional accuracy
        
        Returns:
            Dictionary of metrics
        """
        mask: pd.Series = ~(actual.isna() | predicted.isna())
        actual_clean: pd.Series = pd.Series(data=actual[mask])
        predicted_clean: pd.Series = pd.Series(data=predicted[mask])
        returns_clean: pd.Series = pd.Series(data=target_returns[mask])

        if len(actual_clean) == 0:
            logger.warning(msg=f"No actual prices available after removing NaN values")
            return {}

        mae: Number = mean_absolute_error(y_true=actual_clean, y_pred=predicted_clean)
        rmse: Number = np.sqrt(mean_squared_error(y_true=actual_clean, y_pred=predicted_clean))
        mape: Number = np.mean(np.abs((actual_clean - predicted_clean) / actual_clean)) * 100

        directional_accuracy: Number = np.nan
        if len(returns_clean) > 0:
            pred_direction: np.ndarray = (predicted_clean > actual_clean.shift(periods=1)).astype(int)
            actual_direction: np.ndarray = (returns_clean > 0).astype(int)
            
            min_len: int = min(len(pred_direction), len(actual_direction))
            pred_direction = pd.Series(data=pred_direction).iloc[-min_len:]
            actual_direction = pd.Series(data=actual_direction).iloc[-min_len:]
            
            directional_accuracy = np.mean(pred_direction == actual_direction) * 100

        return {
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "directional_accuracy": directional_accuracy,
            "n_predictions": len(actual_clean)
        }

    def run_baseline_models(self) -> Dict[str, List[Dict[str, Number]]]:
        """
        Run baseline models on all splits.
        
        Returns:
            Dictionary with baseline results
        """
        logger.info("Running baseline models...")
        
        baseline_results: Dict[str, List[Dict[str, Number]]] = {
            'naive': [],
            'sma_5': [],
            'sma_20': []
        }

        for idx, (train_start, train_end, test_start, test_end) in enumerate(iterable=self.splits):
            train_data, test_data = get_split_data(
                data=self.data,
                train_start=train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end
            )

            if (len(train_data) == 0) or (len(test_data) == 0):
                logger.warning(msg=f"Skipping iteration #{idx}: Empty train or test data.")
                continue

            naive_pred: pd.DataFrame | pd.Series = test_data["Close"].shift(1).fillna(test_data["Close"].iloc[0])
            naive_metrics: Dict[str, Number] = self._calculate_metrics(
                actual=pd.Series(data=test_data["Close"]),
                predicted=pd.Series(data=naive_pred),
                target_returns=pd.Series(data=test_data["target_return"])
            )
            baseline_results["naive"].append(naive_metrics)

            if "sma_5" in train_data.columns:
                sma_5_pred: pd.DataFrame | pd.Series = test_data['sma_5'].shift(1).fillna(test_data['Close'].iloc[0])
                sma_5_metrics: Dict[str, Number] = self._calculate_metrics(
                    actual=pd.Series(data=test_data['Close']),
                    predicted=pd.Series(data=sma_5_pred),
                    target_returns=pd.Series(data=test_data['target_return'])
                )
                baseline_results['sma_5'].append(sma_5_metrics)
            
            if 'sma_20' in train_data.columns:
                sma_20_pred: pd.DataFrame | pd.Series = test_data['sma_20'].shift(1).fillna(test_data['Close'].iloc[0])
                sma_20_metrics: Dict[str, Number] = self._calculate_metrics(
                    actual=pd.Series(data=test_data['Close']),
                    predicted=pd.Series(data=sma_20_pred),
                    target_returns=pd.Series(data=test_data['target_return'])
                )
                baseline_results['sma_20'].append(sma_20_metrics)
        
        return baseline_results

    def run_custom_model(
        self,
        model_func: Callable,
        model_name: str,
        **kwargs
    ) -> List[Dict[str, Number]]:
        """
        Run a custom model on all splits.
        
        Args:
            model_func: Function that takes (train_data, test_data) and returns predictions
            model_name: Name of the model for logging
            **kwargs: Additional arguments for the model function
        
        Returns:
            List of metric dictionaries for each split
        """
        logger.info(msg=f"Running custom model: {model_name}")

        results: List[Dict[str, Number]] = []
        for idx, (train_start, train_end, test_start, test_end) in enumerate(iterable=self.splits):
            train_data, test_data = get_split_data(
                data=self.data,
                train_start=train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end
            )

            if (len(train_data) == 0) or (len(test_data) == 0):
                logger.warning(msg=f"Skipping iteration #{idx}: Empty train or test data.")
                continue

            try:
                predictions = model_func(train_data, test_data, **kwargs)
                metrics: Dict[str, Number] = self._calculate_metrics(
                    actual=pd.Series(data=test_data["Close"]),
                    predicted=predictions,
                    target_returns=pd.Series(data=test_data["target_returns"])
                )
                
                metrics["split"] = idx
                results.append(metrics)
            
            except Exception as e:
                logger.error(msg=f"Error in split #{idx} for {model_name}: {e}")
                continue

        return results

    def summarize_results(self, results: Dict[str, List[Dict[str, Number]]]) -> pd.DataFrame:
        """
        Summarize results across all splits.
        
        Args:
            results: Dictionary with model results
            
        Returns:
            Summary DataFrame
        """
        summary_data: List = []
        for model_name, model_results in results.items():
            if not model_results:
                continue
                
            df: pd.DataFrame = pd.DataFrame(data=model_results)
            summary: Dict[str, Any] = {
                'model': model_name,
                'n_splits': len(model_results),
                'avg_mae': df['mae'].mean(),
                'std_mae': df['mae'].std(),
                'avg_rmse': df['rmse'].mean(),
                'std_rmse': df['rmse'].std(),
                'avg_mape': df['mape'].mean(),
                'std_mape': df['mape'].std(),
                'avg_directional_accuracy': df['directional_accuracy'].mean(),
                'std_directional_accuracy': df['directional_accuracy'].std()
            }
            
            summary_data.append(summary)
        
        return pd.DataFrame(data=summary_data)

    def plot_results(self, results: Dict[str, List[Dict[str, Number]]], metric: str = 'mae') -> None:
        """
        Plot results across splits for comparison.
        
        Args:
            results: Dictionary with model results
            metric: Metric to plot
        """
        plt.figure(figsize=(12, 6))
        
        for model_name, model_results in results.items():
            if not model_results:
                continue
                
            # Extract metric values
            values: List[float] = [float(r.get(metric, np.nan)) for r in model_results]
            splits: List[int] = list(range(len(values)))
            
            plt.plot(splits, values, marker='o', label=model_name, alpha=0.7)
        
        plt.xlabel(xlabel='Split Index')
        plt.ylabel(ylabel=metric.upper())
        plt.title(label=f'{metric.upper()} Across Walk-Forward Splits')
        plt.legend()
        plt.grid(visible=True, alpha=0.3)
        plt.tight_layout()
        plt.show()