# Phase 0: Data Preparation and Environment Setup

## 📋 Overview

Phase 0 implements the foundational infrastructure for the trading prediction system as outlined in the project roadmap. This phase focuses on establishing a robust data pipeline, implementing walk-forward backtesting, and creating baseline models for comparison.

## 🎯 Objectives

- **Data Infrastructure**: Download, clean, and preprocess stock data from Yahoo Finance
- **Feature Engineering**: Create basic technical indicators and target variables
- **Walk-Forward Validation**: Implement time series cross-validation without data leakage
- **Baseline Models**: Establish naive and simple moving average baselines
- **Results Framework**: Create reproducible evaluation and reporting system

## 🏗️ Architecture

### Core Modules

#### `data_preparation.py`
- **`download_stock_data()`**: Downloads stock data using yfinance
- **`preprocess_stock_data()`**: Handles MultiIndex columns and data cleaning
- **`postprocess_stock_data()`**: Creates technical features and target variables
- **`get_stock_data()`**: Orchestrates the complete data pipeline
- **`create_walk_forward_splits()`**: Generates temporal splits for validation

#### `backtesting.py`
- **`WalkForwardBacktester`**: Main backtesting class
- **`run_baseline_models()`**: Executes naive, SMA5, and SMA20 baselines
- **`run_custom_model()`**: Framework for testing custom models
- **`_calculate_metrics()`**: Computes MAE, RMSE, MAPE, and directional accuracy

#### `main.py`
- **Main execution script** that orchestrates the complete Phase 0 workflow
- **Results generation** with timestamped CSV outputs
- **Performance assessment** against success criteria

#### `utils.py`
- **Logging configuration** and utility functions
- **Type definitions** for consistent code structure

## 📊 Data Pipeline

### 1. Data Download
```python
# Downloads AAPL data from 2020-2024
stock_data = download_stock_data(
    symbol="AAPL",
    start_date="2020-01-01",
    end_date="2025-01-01",
    interval="1d"
)
```

### 2. Data Preprocessing
- **MultiIndex handling**: Automatically flattens yfinance column structure
- **Missing data**: Removes rows with incomplete OHLC data
- **Data validation**: Ensures positive prices and valid volume data
- **Temporal alignment**: Sorts data chronologically

### 3. Feature Engineering
- **Returns**: Percentage and logarithmic returns
- **Target variables**: Next-day return and direction (binary)
- **Technical indicators**: SMA5, SMA20, rolling volatility
- **Price changes**: Absolute and percentage price movements

## 🔄 Walk-Forward Validation

### Split Configuration
- **Training window**: 252 days (~1 trading year)
- **Testing window**: 63 days (~3 trading months)
- **Step size**: 21 days (~1 trading month)
- **Total splits**: 46 splits covering 4+ years of data

### Validation Process
1. **Split creation**: Temporal division without overlap
2. **Model training**: Fit on training window
3. **Prediction**: Generate forecasts for test window
4. **Evaluation**: Calculate metrics on out-of-sample data
5. **Rolling**: Move forward and repeat

## 📈 Baseline Models

### 1. Naive Model
- **Strategy**: Tomorrow's price = Today's price
- **Use case**: Simplest possible baseline
- **Expected performance**: ~50% directional accuracy

### 2. SMA5 Model
- **Strategy**: Tomorrow's price = 5-day simple moving average
- **Use case**: Short-term trend following
- **Expected performance**: Best directional accuracy

### 3. SMA20 Model
- **Strategy**: Tomorrow's price = 20-day simple moving average
- **Use case**: Medium-term trend following
- **Expected performance**: Higher error, moderate directional accuracy

## 📊 Evaluation Metrics

### Primary Metrics
- **MAE (Mean Absolute Error)**: Average absolute price prediction error
- **RMSE (Root Mean Square Error)**: Penalizes large errors more heavily
- **MAPE (Mean Absolute Percentage Error)**: Error relative to actual price
- **Directional Accuracy**: Percentage of correct up/down predictions

### Success Criteria
- **Baselines operational**: All 3 models must run successfully
- **Reproducible results**: Consistent performance across splits
- **No data leakage**: Strict temporal separation maintained

## 🚀 Usage

### Quick Start
```bash
# From project root directory
python3 -m phase0.main
```

### Expected Output
```
INFO:phase0:Starting Phase 0: Data Preparation and Environment Setup
INFO:phase0:Step 1: Downloading and Cleaning data
INFO:phase0:Step 2: Creating walk-forward splits
INFO:phase0:Step 3: Initializing backtester
INFO:phase0:Step 4: Running baseline models
INFO:phase0:Step 5: Summarizing results
INFO:phase0:Step 6: Creating visualization
INFO:phase0:Step 7: Saving results
INFO:phase0:Step 8: Final assessment
```

### Results Location
- **Summary**: `phase0/results/{timestamp}/baseline_results.csv`
- **Detailed**: `phase0/results/{timestamp}/{model}_detailed.csv`
- **Visualizations**: Generated plots displayed during execution

## 🔧 Configuration

### Data Parameters
```python
SYMBOL = "AAPL"           # Stock symbol
START_DATE = "2020-01-01" # Start date for data
END_DATE = "2025-01-01"   # End date for data
INTERVAL = "1d"           # Data frequency
```

### Validation Parameters
```python
TRAIN_SIZE = 252          # Training window (days)
TEST_SIZE = 63            # Testing window (days)
STEP_SIZE = 21            # Step between splits (days)
```

## 📁 File Structure

```
phase0/
├── README.md              # This file
├── main.py                # Main execution script
├── data_preparation.py    # Data pipeline and preprocessing
├── backtesting.py         # Walk-forward backtesting framework
├── utils.py               # Utilities and type definitions
├── __init__.py            # Package initialization
├── results/               # Generated results (auto-created)
│   └── {timestamp}/      # Timestamped result folders
│       ├── baseline_results.csv
│       ├── naive_detailed.csv
│       ├── sma_5_detailed.csv
│       └── sma_20_detailed.csv
└── __pycache__/          # Python cache (auto-created)
```

## 🧪 Testing and Validation

### Data Quality Checks
- **Completeness**: No missing OHLC data
- **Validity**: All prices > 0, volume >= 0
- **Temporal**: Chronological order maintained
- **Features**: All technical indicators calculated correctly

### Model Validation
- **Reproducibility**: Same results with fixed seeds
- **Temporal consistency**: Performance across different time periods
- **Metric stability**: Low standard deviation across splits

## 🚨 Troubleshooting

### Common Issues

#### Module Import Errors
```bash
# Solution: Run as module from project root
python3 -m phase0.main
```

#### Missing Dependencies
```bash
# Install required packages
pip3 install pandas numpy yfinance matplotlib scikit-learn
```

#### Data Download Failures
- Check internet connection
- Verify stock symbol validity
- Ensure date range is reasonable

### Debug Configuration
Use the provided `.vscode/launch.json` configurations:
- **Debug Phase 0 as Module**: Recommended for development
- **Debug Current File**: For individual file debugging

## 📈 Performance Expectations

### Baseline Performance (AAPL 2020-2024)
| Model | MAE | RMSE | Directional Accuracy |
|-------|-----|------|---------------------|
| Naive | 1.97 | 2.57 | 47.0% |
| SMA5  | 3.04 | 3.79 | 53.6% |
| SMA20 | 5.70 | 6.79 | 49.2% |

### Success Indicators
- ✅ All baselines operational
- ✅ 46+ walk-forward splits created
- ✅ Results saved with timestamps
- ✅ No data leakage detected
- ✅ Reproducible performance metrics

## 🔮 Next Steps

Phase 0 establishes the foundation for:
- **Phase 1**: ARIMA/SARIMA and Prophet models
- **Phase 2**: Machine learning with engineered features
- **Phase 3**: Deep learning for time series
- **Phase 4**: Multimodal approaches

## 📚 References

- **Walk-Forward Analysis**: Time series validation methodology
- **Technical Indicators**: SMA, volatility, momentum calculations
- **Data Preprocessing**: Handling financial data idiosyncrasies
- **Baseline Models**: Simple but effective comparison models

---

**Status**: ✅ **COMPLETED** - Ready for Phase 1 implementation
**Last Updated**: August 30, 2025
**Version**: 1.0.0
