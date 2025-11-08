"""
Time Series Forecasting Service
Handles time series analysis, forecasting, and anomaly detection
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

# Prophet for time series forecasting
try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False
    logging.warning("Prophet not available for time series forecasting")

# LSTM for time series
try:
    import tensorflow as tf
    from tensorflow import keras
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logging.warning("TensorFlow not available for LSTM time series")

# ARIMA
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    logging.warning("statsmodels not available for ARIMA")

# Anomaly detection
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


def detect_datetime_columns(df: pd.DataFrame) -> List[str]:
    """
    Detect columns that could be datetime/timestamp columns
    """
    datetime_cols = []
    
    for col in df.columns:
        # Check if already datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
            continue
        
        # Try to parse as datetime
        try:
            pd.to_datetime(df[col], errors='raise')
            datetime_cols.append(col)
        except:
            pass
    
    return datetime_cols


def prepare_time_series_data(
    df: pd.DataFrame,
    time_column: str,
    target_column: str
) -> pd.DataFrame:
    """
    Prepare dataframe for time series analysis
    """
    # Create a copy
    df_ts = df[[time_column, target_column]].copy()
    
    # Convert time column to datetime
    if not pd.api.types.is_datetime64_any_dtype(df_ts[time_column]):
        df_ts[time_column] = pd.to_datetime(df_ts[time_column])
    
    # Sort by time
    df_ts = df_ts.sort_values(time_column)
    
    # Remove missing values
    df_ts = df_ts.dropna()
    
    # Set time as index
    df_ts = df_ts.set_index(time_column)
    
    return df_ts


def forecast_with_prophet(
    df: pd.DataFrame,
    time_column: str,
    target_column: str,
    forecast_periods: int = 30,
    confidence_interval: float = 0.95
) -> Dict[str, Any]:
    """
    Forecast using Facebook Prophet
    
    Args:
        df: DataFrame with time series data
        time_column: Name of datetime column
        target_column: Name of target column to forecast
        forecast_periods: Number of periods to forecast ahead
        confidence_interval: Confidence interval for predictions (default 0.95)
    
    Returns:
        Dictionary with forecast results, trends, and metadata
    """
    if not HAS_PROPHET:
        raise ImportError("Prophet not installed. Install with: pip install prophet")
    
    try:
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        df_prophet = df[[time_column, target_column]].copy()
        df_prophet.columns = ['ds', 'y']
        
        # Convert to datetime
        if not pd.api.types.is_datetime64_any_dtype(df_prophet['ds']):
            df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
        
        # CRITICAL FIX: Remove timezone from datetime column (Prophet doesn't support timezones)
        if pd.api.types.is_datetime64_any_dtype(df_prophet['ds']):
            if df_prophet['ds'].dt.tz is not None:
                df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
        
        # Remove missing values
        df_prophet = df_prophet.dropna()
        
        # Sort by date
        df_prophet = df_prophet.sort_values('ds')
        
        # Initialize and fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=confidence_interval
        )
        
        model.fit(df_prophet)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=forecast_periods)
        
        # Make predictions
        forecast = model.predict(future)
        
        # Extract historical and forecast data
        historical_size = len(df_prophet)
        
        historical_data = {
            "dates": df_prophet['ds'].dt.strftime('%Y-%m-%d').tolist(),
            "values": df_prophet['y'].tolist()
        }
        
        forecast_data = {
            "dates": forecast['ds'].iloc[historical_size:].dt.strftime('%Y-%m-%d').tolist(),
            "values": forecast['yhat'].iloc[historical_size:].tolist(),
            "lower_bound": forecast['yhat_lower'].iloc[historical_size:].tolist(),
            "upper_bound": forecast['yhat_upper'].iloc[historical_size:].tolist()
        }
        
        # Extract trend components
        trend_components = {
            "trend": forecast['trend'].tolist(),
            "weekly": forecast['weekly'].tolist() if 'weekly' in forecast.columns else None,
            "yearly": forecast['yearly'].tolist() if 'yearly' in forecast.columns else None
        }
        
        # Calculate forecast quality metrics (on historical data)
        historical_predictions = forecast['yhat'].iloc[:historical_size].values
        historical_actuals = df_prophet['y'].values
        
        mape = np.mean(np.abs((historical_actuals - historical_predictions) / historical_actuals)) * 100
        rmse = np.sqrt(np.mean((historical_actuals - historical_predictions) ** 2))
        
        return {
            "success": True,
            "model_type": "Prophet",
            "historical_data": historical_data,
            "forecast_data": forecast_data,
            "trend_components": trend_components,
            "metrics": {
                "mape": float(mape),
                "rmse": float(rmse),
                "confidence_interval": confidence_interval
            },
            "metadata": {
                "forecast_periods": forecast_periods,
                "historical_size": historical_size,
                "target_column": target_column,
                "time_column": time_column
            }
        }
    
    except Exception as e:
        logging.error(f"Prophet forecasting failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model_type": "Prophet"
        }


def forecast_with_lstm(
    df: pd.DataFrame,
    time_column: str,
    target_column: str,
    forecast_periods: int = 30,
    lookback: int = 10
) -> Dict[str, Any]:
    """
    Forecast using LSTM neural network
    
    Args:
        df: DataFrame with time series data
        time_column: Name of datetime column
        target_column: Name of target column to forecast
        forecast_periods: Number of periods to forecast ahead
        lookback: Number of previous time steps to use for prediction
    
    Returns:
        Dictionary with forecast results and metadata
    """
    if not HAS_TENSORFLOW:
        raise ImportError("TensorFlow not installed. Install with: pip install tensorflow")
    
    try:
        import os as tf_os
        tf_os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        
        # Prepare time series data
        df_ts = prepare_time_series_data(df, time_column, target_column)
        values = df_ts[target_column].values
        
        # Normalize data
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        values_scaled = scaler.fit_transform(values.reshape(-1, 1)).flatten()
        
        # Create sequences for LSTM
        def create_sequences(data, lookback):
            X, y = [], []
            for i in range(len(data) - lookback):
                X.append(data[i:i+lookback])
                y.append(data[i+lookback])
            return np.array(X), np.array(y)
        
        X, y = create_sequences(values_scaled, lookback)
        
        # Reshape for LSTM [samples, time steps, features]
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        # Split into train and test
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Build LSTM model
        model = keras.Sequential([
            keras.layers.LSTM(50, activation='relu', return_sequences=True, input_shape=(lookback, 1)),
            keras.layers.LSTM(50, activation='relu'),
            keras.layers.Dense(25),
            keras.layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse')
        
        # Train model
        model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0, validation_split=0.2)
        
        # Make predictions on test set
        y_pred_scaled = model.predict(X_test, verbose=0).flatten()
        
        # Inverse transform predictions
        y_pred = scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
        
        # Calculate metrics
        rmse = np.sqrt(np.mean((y_test_actual - y_pred) ** 2))
        mape = np.mean(np.abs((y_test_actual - y_pred) / y_test_actual)) * 100
        
        # Forecast future values
        last_sequence = values_scaled[-lookback:]
        forecast_scaled = []
        
        for _ in range(forecast_periods):
            # Reshape for prediction
            X_pred = last_sequence.reshape(1, lookback, 1)
            # Predict next value
            next_val = model.predict(X_pred, verbose=0)[0, 0]
            forecast_scaled.append(next_val)
            # Update sequence
            last_sequence = np.append(last_sequence[1:], next_val)
        
        # Inverse transform forecast
        forecast_values = scaler.inverse_transform(np.array(forecast_scaled).reshape(-1, 1)).flatten()
        
        # Generate future dates
        last_date = df_ts.index[-1]
        freq = pd.infer_freq(df_ts.index[:50])  # Infer frequency from first 50 points
        if freq is None:
            freq = 'D'  # Default to daily
        
        future_dates = pd.date_range(start=last_date, periods=forecast_periods+1, freq=freq)[1:]
        
        return {
            "success": True,
            "model_type": "LSTM",
            "historical_data": {
                "dates": df_ts.index.strftime('%Y-%m-%d').tolist(),
                "values": values.tolist()
            },
            "forecast_data": {
                "dates": future_dates.strftime('%Y-%m-%d').tolist(),
                "values": forecast_values.tolist()
            },
            "metrics": {
                "rmse": float(rmse),
                "mape": float(mape)
            },
            "metadata": {
                "forecast_periods": forecast_periods,
                "lookback": lookback,
                "historical_size": len(values),
                "target_column": target_column,
                "time_column": time_column
            }
        }
    
    except Exception as e:
        logging.error(f"LSTM forecasting failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model_type": "LSTM"
        }


def detect_anomalies(
    df: pd.DataFrame,
    time_column: str,
    target_column: str,
    method: str = "isolation_forest",
    contamination: float = 0.1
) -> Dict[str, Any]:
    """
    Detect anomalies in time series data
    
    Args:
        df: DataFrame with time series data
        time_column: Name of datetime column
        target_column: Name of target column
        method: "isolation_forest" or "lof" (Local Outlier Factor)
        contamination: Expected proportion of outliers
    
    Returns:
        Dictionary with anomaly detection results
    """
    try:
        # Prepare data
        df_ts = prepare_time_series_data(df, time_column, target_column)
        values = df_ts[target_column].values.reshape(-1, 1)
        
        # Detect anomalies
        if method == "isolation_forest":
            detector = IsolationForest(contamination=contamination, random_state=42)
        elif method == "lof":
            detector = LocalOutlierFactor(contamination=contamination)
        else:
            raise ValueError(f"Unknown anomaly detection method: {method}")
        
        # Fit and predict
        if method == "isolation_forest":
            predictions = detector.fit_predict(values)
        else:
            predictions = detector.fit_predict(values)
        
        # -1 for anomalies, 1 for normal
        anomaly_indices = np.where(predictions == -1)[0]
        
        anomalies = {
            "dates": df_ts.index[anomaly_indices].strftime('%Y-%m-%d').tolist(),
            "values": df_ts[target_column].iloc[anomaly_indices].tolist(),
            "indices": anomaly_indices.tolist()
        }
        
        return {
            "success": True,
            "method": method,
            "anomalies": anomalies,
            "anomaly_count": len(anomaly_indices),
            "total_points": len(values),
            "anomaly_percentage": float(len(anomaly_indices) / len(values) * 100)
        }
    
    except Exception as e:
        logging.error(f"Anomaly detection failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "method": method
        }


def analyze_time_series(
    df: pd.DataFrame,
    time_column: str,
    target_column: str,
    forecast_periods: int = 30,
    forecast_method: str = "prophet"
) -> Dict[str, Any]:
    """
    Comprehensive time series analysis including forecasting and anomaly detection
    
    Args:
        df: DataFrame with time series data
        time_column: Name of datetime column
        target_column: Name of target column
        forecast_periods: Number of periods to forecast
        forecast_method: "prophet", "lstm", or "both"
    
    Returns:
        Dictionary with complete time series analysis
    """
    results = {
        "time_column": time_column,
        "target_column": target_column,
        "datetime_columns": detect_datetime_columns(df)
    }
    
    # Forecasting with error handling
    if forecast_method in ["prophet", "both"]:
        try:
            prophet_results = forecast_with_prophet(df, time_column, target_column, forecast_periods)
            results["prophet_forecast"] = prophet_results
            logging.info("✅ Prophet forecast completed successfully")
        except Exception as e:
            logging.error(f"❌ Prophet forecast failed: {str(e)}", exc_info=True)
            results["prophet_forecast"] = {
                "success": False,
                "error": str(e),
                "message": "Prophet forecasting failed. This might be due to insufficient data or data format issues."
            }
    
    if forecast_method in ["lstm", "both"]:
        try:
            lstm_results = forecast_with_lstm(df, time_column, target_column, forecast_periods)
            results["lstm_forecast"] = lstm_results
            logging.info("✅ LSTM forecast completed successfully")
        except Exception as e:
            logging.error(f"❌ LSTM forecast failed: {str(e)}", exc_info=True)
            results["lstm_forecast"] = {
                "success": False,
                "error": str(e),
                "message": "LSTM forecasting failed. This might be due to insufficient data or TensorFlow issues."
            }
    
    # Anomaly detection
    try:
        anomaly_results = detect_anomalies(df, time_column, target_column)
        results["anomaly_detection"] = anomaly_results
    except Exception as e:
        logging.error(f"❌ Anomaly detection failed: {str(e)}")
        results["anomaly_detection"] = {
            "success": False,
            "error": str(e)
        }
    
    return results



async def explain_forecast_with_ai(
    forecast_data: Dict,
    method: str,
    target_column: str
) -> str:
    """
    Get AI explanation of time series forecast using Azure OpenAI
    
    Args:
        forecast_data: Forecast results with predictions
        method: Forecasting method used ("prophet", "lstm", or "both")
        target_column: Name of target variable
    
    Returns:
        Human-readable forecast explanation
    """
    try:
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        if not azure_service.is_available():
            return f"Forecast generated using {method} method for {target_column}."
        
        # Extract key metrics
        mape = forecast_data.get('mape', 'N/A')
        forecast_values = forecast_data.get('forecast', [])
        trend = "increasing" if len(forecast_values) > 1 and forecast_values[-1] > forecast_values[0] else "decreasing"
        
        context = f"""
Time Series Forecast Analysis:
- Target Variable: {target_column}
- Method: {method}
- Forecast Periods: {len(forecast_values)}
- MAPE (Error): {mape}
- Trend Direction: {trend}
- First Predicted Value: {forecast_values[0] if forecast_values else 'N/A'}
- Last Predicted Value: {forecast_values[-1] if len(forecast_values) > 0 else 'N/A'}

Task: Explain this forecast in business terms:
1. What is the overall trend? (increasing/decreasing/stable)
2. Is the forecast accurate? (based on MAPE)
3. What does this mean for business planning?
4. Any concerns or recommendations?

Keep it concise (3-4 sentences) and actionable.
"""
        
        explanation = await azure_service.generate_completion(
            prompt=context,
            max_tokens=500,
            temperature=0.5
        )
        
        return explanation
    
    except Exception as e:
        logger.error(f"Forecast explanation failed: {str(e)}")
        return f"Forecast completed using {method}. MAPE: {forecast_data.get('mape', 'N/A')}"


async def explain_anomalies_with_ai(
    anomalies: Dict,
    target_column: str,
    data_context: Dict = None
) -> str:
    """
    Get AI explanation of detected anomalies using Azure OpenAI
    
    Args:
        anomalies: Anomaly detection results
        target_column: Name of target variable
        data_context: Optional context about the data
    
    Returns:
        Human-readable anomaly explanation
    """
    try:
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        anomaly_count = anomalies.get('anomaly_count', 0)
        anomaly_percentage = anomalies.get('anomaly_percentage', 0)
        
        if not azure_service.is_available():
            return f"Detected {anomaly_count} anomalies ({anomaly_percentage:.1f}% of data) in {target_column}."
        
        context = f"""
Anomaly Detection Results:
- Target Variable: {target_column}
- Total Anomalies: {anomaly_count}
- Percentage: {anomaly_percentage:.2f}%
- Detection Method: Isolation Forest + LOF

Context:
{data_context if data_context else 'Standard time series data'}

Task: Explain these anomalies in business context:
1. What are anomalies and why do they matter?
2. Is {anomaly_percentage:.1f}% concerning? (normal range is 1-5%)
3. What could cause these anomalies in {target_column}?
4. Recommended actions?

Be specific and actionable (3-4 sentences).
"""
        
        explanation = await azure_service.generate_completion(
            prompt=context,
            max_tokens=500,
            temperature=0.5
        )
        
        return explanation
    
    except Exception as e:
        logger.error(f"Anomaly explanation failed: {str(e)}")
        return f"{anomaly_count} anomalies detected ({anomaly_percentage:.1f}%)."


async def generate_time_series_insights(
    forecast_results: Dict,
    anomaly_results: Dict,
    target_column: str,
    method: str
) -> str:
    """
    Generate comprehensive time series analysis insights using Azure OpenAI
    
    Args:
        forecast_results: Forecast data
        anomaly_results: Anomaly detection data
        target_column: Target variable name
        method: Forecasting method
    
    Returns:
        Comprehensive insights summary
    """
    try:
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        if not azure_service.is_available():
            return "Time series analysis completed successfully."
        
        # Extract key info
        mape = forecast_results.get('mape', 'N/A')
        anomaly_count = anomaly_results.get('anomaly_count', 0)
        anomaly_pct = anomaly_results.get('anomaly_percentage', 0)
        
        context = f"""
Complete Time Series Analysis for {target_column}:

Forecast Results:
- Method: {method}
- Accuracy (MAPE): {mape}
- Forecast Trend: {forecast_results.get('trend', 'N/A')}

Anomaly Detection:
- Anomalies Found: {anomaly_count} ({anomaly_pct:.1f}%)

Task: Provide executive summary:
1. Overall assessment (forecast quality + data quality)
2. Key findings and patterns
3. Business implications
4. Strategic recommendations

Format as bullet points, 4-5 key points total.
"""
        
        insights = await azure_service.generate_completion(
            prompt=context,
            max_tokens=700,
            temperature=0.4
        )
        
        return insights
    
    except Exception as e:
        logger.error(f"Time series insights generation failed: {str(e)}")
        return f"Time series analysis: Forecast MAPE {mape}, {anomaly_count} anomalies detected."

