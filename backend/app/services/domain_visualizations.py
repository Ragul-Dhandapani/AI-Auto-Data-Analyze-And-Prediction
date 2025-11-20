"""
Domain-Specific Visualization Service
Generates intelligent, context-aware charts based on detected domain
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)


def generate_capacity_whatif_scenario(
    df: pd.DataFrame,
    target_column: str,
    time_column: Optional[str] = None,
    thresholds: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Generate capacity what-if scenarios with forecasting
    Used for SRE/Infrastructure and Capacity Planning domains
    """
    
    if thresholds is None:
        thresholds = {"soft": 75, "hard": 90}
    
    # Get current utilization
    current_util = df[target_column].mean()
    peak_util = df[target_column].max()
    min_util = df[target_column].min()
    
    # Calculate headroom
    soft_headroom = thresholds["soft"] - current_util
    hard_headroom = thresholds["hard"] - current_util
    
    # Simple linear forecast (next 30 days)
    n_points = len(df)
    X = np.arange(n_points).reshape(-1, 1)
    y = df[target_column].values
    
    # Fit linear model
    model = LinearRegression()
    model.fit(X, y)
    
    # Forecast next 30 points
    future_X = np.arange(n_points, n_points + 30).reshape(-1, 1)
    forecast = model.predict(future_X)
    
    # Calculate trend
    trend_slope = model.coef_[0]
    trend_direction = "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable"
    
    # Estimate days to threshold
    days_to_soft = None
    days_to_hard = None
    
    if trend_slope > 0:
        # Calculate when we'll hit thresholds
        if current_util < thresholds["soft"]:
            days_to_soft = int((thresholds["soft"] - current_util) / trend_slope)
        if current_util < thresholds["hard"]:
            days_to_hard = int((thresholds["hard"] - current_util) / trend_slope)
    
    # Prepare chart data
    historical_data = [
        {"index": i, "value": float(val), "type": "actual"}
        for i, val in enumerate(df[target_column].values[-30:])  # Last 30 points
    ]
    
    forecast_data = [
        {"index": n_points + i, "value": float(val), "type": "forecast"}
        for i, val in enumerate(forecast[:30])
    ]
    
    return {
        "chart_type": "capacity_whatif",
        "current_utilization": round(current_util, 2),
        "peak_utilization": round(peak_util, 2),
        "min_utilization": round(min_util, 2),
        "soft_threshold": thresholds["soft"],
        "hard_threshold": thresholds["hard"],
        "soft_headroom": round(soft_headroom, 2),
        "hard_headroom": round(hard_headroom, 2),
        "trend_direction": trend_direction,
        "trend_slope": round(trend_slope, 4),
        "days_to_soft_threshold": days_to_soft,
        "days_to_hard_threshold": days_to_hard,
        "historical_data": historical_data,
        "forecast_data": forecast_data,
        "recommendation": _generate_capacity_recommendation(current_util, trend_slope, thresholds)
    }


def generate_headroom_vs_threshold_chart(
    df: pd.DataFrame,
    target_column: str,
    thresholds: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Generate headroom vs threshold bar chart
    Shows current utilization against soft and hard thresholds
    """
    
    if thresholds is None:
        thresholds = {"soft": 75, "hard": 90}
    
    current_util = df[target_column].mean()
    peak_util = df[target_column].max()
    
    # Calculate percentages
    soft_usage_pct = (current_util / thresholds["soft"]) * 100
    hard_usage_pct = (current_util / thresholds["hard"]) * 100
    
    # Status determination
    status = "healthy"
    if current_util >= thresholds["hard"]:
        status = "critical"
    elif current_util >= thresholds["soft"]:
        status = "warning"
    
    return {
        "chart_type": "headroom_threshold",
        "current_utilization": round(current_util, 2),
        "peak_utilization": round(peak_util, 2),
        "soft_threshold": thresholds["soft"],
        "hard_threshold": thresholds["hard"],
        "soft_usage_percentage": round(soft_usage_pct, 1),
        "hard_usage_percentage": round(hard_usage_pct, 1),
        "status": status,
        "bars": [
            {
                "label": "Current Utilization",
                "value": round(current_util, 2),
                "threshold": thresholds["hard"],
                "color": "#3b82f6" if status == "healthy" else "#f59e0b" if status == "warning" else "#ef4444"
            },
            {
                "label": "Peak Utilization",
                "value": round(peak_util, 2),
                "threshold": thresholds["hard"],
                "color": "#8b5cf6"
            },
            {
                "label": "Soft Threshold",
                "value": thresholds["soft"],
                "threshold": thresholds["hard"],
                "color": "#f59e0b"
            },
            {
                "label": "Hard Threshold",
                "value": thresholds["hard"],
                "threshold": 100,
                "color": "#ef4444"
            }
        ]
    }


def generate_yoy_comparison_chart(
    df: pd.DataFrame,
    target_column: str,
    time_column: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate Year-over-Year comparison chart
    Used for Food Economics, Trading, etc.
    """
    
    # If no time column specified, try to find one
    if time_column is None:
        time_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if time_cols:
            time_column = time_cols[0]
    
    if time_column and time_column in df.columns:
        # Parse dates
        try:
            df['parsed_date'] = pd.to_datetime(df[time_column])
            df['year'] = df['parsed_date'].dt.year
            df['month'] = df['parsed_date'].dt.month
            
            # Group by year and month
            yoy_data = df.groupby(['year', 'month'])[target_column].mean().reset_index()
            
            # Pivot to compare years
            years = sorted(yoy_data['year'].unique())
            
            chart_data = []
            for month in range(1, 13):
                month_data = {"month": month, "month_name": datetime(2000, month, 1).strftime('%b')}
                for year in years:
                    year_val = yoy_data[(yoy_data['year'] == year) & (yoy_data['month'] == month)][target_column].values
                    month_data[f"year_{year}"] = float(year_val[0]) if len(year_val) > 0 else None
                chart_data.append(month_data)
            
            return {
                "chart_type": "yoy_comparison",
                "years": [int(y) for y in years],
                "data": chart_data,
                "metric": target_column
            }
        except Exception as e:
            logger.warning(f"Could not parse time column for YoY: {e}")
    
    # Fallback: simple aggregation by index buckets
    n_buckets = 12
    bucket_size = len(df) // n_buckets
    
    chart_data = []
    for i in range(n_buckets):
        start_idx = i * bucket_size
        end_idx = (i + 1) * bucket_size if i < n_buckets - 1 else len(df)
        bucket_val = df.iloc[start_idx:end_idx][target_column].mean()
        
        chart_data.append({
            "period": i + 1,
            "value": round(float(bucket_val), 2)
        })
    
    return {
        "chart_type": "yoy_comparison",
        "data": chart_data,
        "metric": target_column,
        "note": "Showing temporal aggregation (no time column detected)"
    }


def generate_percentile_chart(
    df: pd.DataFrame,
    target_column: str
) -> Dict[str, Any]:
    """
    Generate latency percentile chart (p50, p95, p99)
    Used for Latency/Performance domain
    """
    
    values = df[target_column].dropna()
    
    percentiles = {
        "p50": values.quantile(0.50),
        "p90": values.quantile(0.90),
        "p95": values.quantile(0.95),
        "p99": values.quantile(0.99),
        "max": values.max(),
        "mean": values.mean(),
        "median": values.median()
    }
    
    # Convert to regular Python floats
    percentiles = {k: float(v) for k, v in percentiles.items()}
    
    # Calculate SLA compliance (assuming p95 should be < 100ms, p99 < 500ms)
    sla_thresholds = {"p95": 100, "p99": 500}
    sla_compliance = {
        "p95": percentiles["p95"] < sla_thresholds["p95"],
        "p99": percentiles["p99"] < sla_thresholds["p99"]
    }
    
    return {
        "chart_type": "percentile_distribution",
        "percentiles": percentiles,
        "sla_thresholds": sla_thresholds,
        "sla_compliance": sla_compliance,
        "bars": [
            {"label": "P50 (Median)", "value": percentiles["p50"], "color": "#10b981"},
            {"label": "P90", "value": percentiles["p90"], "color": "#3b82f6"},
            {"label": "P95", "value": percentiles["p95"], "color": "#f59e0b"},
            {"label": "P99", "value": percentiles["p99"], "color": "#ef4444"},
            {"label": "Max", "value": percentiles["max"], "color": "#7c3aed"}
        ]
    }


def generate_volume_analysis_chart(
    df: pd.DataFrame,
    target_column: str,
    time_column: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate volume analysis for trading/payments domain
    """
    
    total_volume = df[target_column].sum()
    avg_volume = df[target_column].mean()
    peak_volume = df[target_column].max()
    
    # Calculate volume distribution
    quartiles = df[target_column].quantile([0.25, 0.5, 0.75]).to_dict()
    
    # Detect anomalies (values > 3 std from mean)
    mean = df[target_column].mean()
    std = df[target_column].std()
    anomaly_threshold = mean + (3 * std)
    anomalies = df[df[target_column] > anomaly_threshold]
    
    return {
        "chart_type": "volume_analysis",
        "total_volume": round(float(total_volume), 2),
        "average_volume": round(float(avg_volume), 2),
        "peak_volume": round(float(peak_volume), 2),
        "quartiles": {k: round(float(v), 2) for k, v in quartiles.items()},
        "anomaly_count": len(anomalies),
        "anomaly_threshold": round(float(anomaly_threshold), 2),
        "distribution": {
            "low": len(df[df[target_column] < quartiles[0.25]]),
            "medium": len(df[(df[target_column] >= quartiles[0.25]) & (df[target_column] < quartiles[0.75])]),
            "high": len(df[df[target_column] >= quartiles[0.75]])
        }
    }


def _generate_capacity_recommendation(current_util: float, trend_slope: float, thresholds: Dict) -> str:
    """Generate capacity planning recommendation"""
    
    if current_util >= thresholds["hard"]:
        return "🚨 CRITICAL: Immediate capacity expansion required. Current utilization exceeds hard threshold."
    elif current_util >= thresholds["soft"]:
        if trend_slope > 0:
            return "⚠️ WARNING: Approaching capacity limits with increasing trend. Plan capacity expansion within 7-14 days."
        else:
            return "⚠️ CAUTION: Utilization above soft threshold but trend is stable/decreasing. Monitor closely."
    else:
        if trend_slope > 0.5:
            return "📈 PROACTIVE: Healthy utilization but strong growth trend. Plan capacity review in 30 days."
        else:
            return "✅ OPTIMAL: Utilization is healthy with stable trend. Continue monitoring."


def generate_domain_specific_charts(
    domain: str,
    df: pd.DataFrame,
    target_column: str,
    viz_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate all relevant charts for a specific domain
    """
    
    charts = []
    primary_chart_types = viz_config.get("primary_charts", [])
    thresholds = viz_config.get("thresholds")
    
    try:
        for chart_type in primary_chart_types:
            if chart_type == "capacity_whatif":
                chart = generate_capacity_whatif_scenario(df, target_column, thresholds=thresholds)
                charts.append(chart)
            
            elif chart_type == "headroom_bar":
                chart = generate_headroom_vs_threshold_chart(df, target_column, thresholds=thresholds)
                charts.append(chart)
            
            elif chart_type == "yoy_comparison":
                chart = generate_yoy_comparison_chart(df, target_column)
                charts.append(chart)
            
            elif chart_type == "percentile_chart":
                chart = generate_percentile_chart(df, target_column)
                charts.append(chart)
            
            elif chart_type == "volume_analysis":
                chart = generate_volume_analysis_chart(df, target_column)
                charts.append(chart)
    
    except Exception as e:
        logger.error(f"Error generating domain charts: {e}")
    
    return charts
