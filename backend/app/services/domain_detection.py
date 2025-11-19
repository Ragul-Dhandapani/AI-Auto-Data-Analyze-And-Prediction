"""
Domain Detection Service
Automatically detects the business domain from column names and data patterns
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import re
from collections import Counter


# Domain patterns - keywords that suggest specific domains
DOMAIN_PATTERNS = {
    "sre_infrastructure": [
        # CPU/Memory metrics
        "cpu", "processor", "core", "memory", "mem", "ram", "disk", "storage",
        # Network metrics
        "network", "bandwidth", "latency", "throughput", "packet", "bytes",
        # System metrics
        "uptime", "availability", "sla", "error_rate", "response_time",
        # Resource metrics
        "utilization", "util", "capacity", "load", "usage", "allocated",
        # Infrastructure terms
        "server", "node", "host", "instance", "container", "pod", "cluster"
    ],
    
    "trading_finance": [
        # Trading terms
        "trade", "order", "execution", "book", "bid", "ask", "spread",
        # Financial instruments
        "stock", "equity", "bond", "derivative", "option", "future", "fx", "forex",
        # Money/Value
        "price", "value", "amount", "notional", "premium", "pnl", "profit", "loss",
        # Volume
        "volume", "quantity", "qty", "size", "lot", "shares",
        # Market data
        "ticker", "symbol", "market", "exchange"
    ],
    
    "payments": [
        # Transaction terms
        "payment", "transaction", "txn", "transfer", "purchase", "refund",
        # Payment methods
        "card", "credit", "debit", "wallet", "upi", "paypal", "stripe",
        # Money
        "amount", "fee", "charge", "total", "balance", "currency",
        # Status
        "status", "pending", "approved", "declined", "failed", "success",
        # Customer
        "merchant", "customer", "vendor", "buyer", "seller"
    ],
    
    "capacity_planning": [
        # Capacity terms
        "capacity", "headroom", "threshold", "limit", "max", "peak", "baseline",
        # Forecasting
        "forecast", "prediction", "projected", "estimated", "predicted",
        # Growth
        "growth", "trend", "rate", "increase", "decrease", "change",
        # Planning
        "required", "allocated", "available", "reserved", "provisioned"
    ],
    
    "food_economics": [
        # Food items
        "food", "grain", "wheat", "rice", "corn", "vegetable", "fruit", "meat",
        # Pricing
        "price", "cost", "expense", "inflation", "cpi", "index",
        # Supply/Demand
        "supply", "demand", "production", "consumption", "yield", "harvest",
        # Market
        "market", "commodity", "agriculture", "farming"
    ],
    
    "travel_transportation": [
        # Travel terms
        "travel", "trip", "journey", "route", "distance", "duration",
        # Transportation modes
        "flight", "train", "bus", "car", "taxi", "uber", "lyft",
        # Locations
        "origin", "destination", "airport", "station", "stop", "city",
        # Booking
        "booking", "reservation", "ticket", "fare", "passenger"
    ],
    
    "expenses_budget": [
        # Expense terms
        "expense", "cost", "spending", "expenditure", "outlay",
        # Budget
        "budget", "allocated", "planned", "actual", "variance",
        # Categories
        "category", "department", "project", "account", "gl",
        # Financial
        "invoice", "receipt", "reimbursement", "claim"
    ],
    
    "latency_performance": [
        # Latency terms
        "latency", "delay", "lag", "time", "duration", "elapsed",
        # Performance
        "performance", "speed", "throughput", "bandwidth", "fps",
        # Response
        "response", "request", "call", "api", "endpoint",
        # Percentiles
        "p50", "p95", "p99", "percentile", "median", "average", "mean"
    ]
}


# Visualization templates for each domain
DOMAIN_VISUALIZATION_CONFIGS = {
    "sre_infrastructure": {
        "primary_charts": ["time_series_with_threshold", "capacity_whatif", "headroom_bar"],
        "metrics_focus": ["utilization", "capacity", "peak", "average"],
        "thresholds": {"soft": 75, "hard": 90},
        "forecasting_method": "linear_with_capacity"
    },
    
    "trading_finance": {
        "primary_charts": ["volume_analysis", "price_movement", "yoy_comparison"],
        "metrics_focus": ["volume", "value", "price", "quantity"],
        "thresholds": None,
        "forecasting_method": "time_series"
    },
    
    "payments": {
        "primary_charts": ["transaction_volume", "success_rate", "anomaly_detection"],
        "metrics_focus": ["amount", "count", "success_rate", "failure_rate"],
        "thresholds": {"success_rate_min": 95},
        "forecasting_method": "trend_with_seasonality"
    },
    
    "capacity_planning": {
        "primary_charts": ["capacity_whatif", "headroom_vs_threshold", "growth_projection"],
        "metrics_focus": ["current_capacity", "forecasted_demand", "headroom"],
        "thresholds": {"soft": 75, "hard": 90},
        "forecasting_method": "linear_with_capacity"
    },
    
    "food_economics": {
        "primary_charts": ["yoy_comparison", "seasonality", "price_index"],
        "metrics_focus": ["price", "inflation", "supply", "demand"],
        "thresholds": None,
        "forecasting_method": "seasonal_decomposition"
    },
    
    "travel_transportation": {
        "primary_charts": ["route_analysis", "demand_forecast", "pricing_trends"],
        "metrics_focus": ["fare", "distance", "duration", "passengers"],
        "thresholds": None,
        "forecasting_method": "time_series"
    },
    
    "expenses_budget": {
        "primary_charts": ["budget_vs_actual", "category_breakdown", "trend_analysis"],
        "metrics_focus": ["amount", "budget", "variance", "percentage"],
        "thresholds": {"budget_variance_max": 10},
        "forecasting_method": "linear"
    },
    
    "latency_performance": {
        "primary_charts": ["percentile_chart", "latency_heatmap", "sla_compliance"],
        "metrics_focus": ["latency", "p50", "p95", "p99"],
        "thresholds": {"latency_p95_max": 100, "latency_p99_max": 500},
        "forecasting_method": "moving_average"
    }
}


def detect_domain(df: pd.DataFrame, feature_columns: List[str], target_column: str) -> Dict[str, Any]:
    """
    Detect the business domain from column names and data patterns
    
    Returns:
        Dict with:
        - domain: str (detected domain)
        - confidence: float (0-1)
        - matched_keywords: List[str]
        - visualization_config: Dict
    """
    
    # Combine all column names for analysis
    all_columns = feature_columns + [target_column]
    column_text = " ".join(all_columns).lower()
    
    # Score each domain based on keyword matches
    domain_scores = {}
    domain_matches = {}
    
    for domain, keywords in DOMAIN_PATTERNS.items():
        matches = []
        score = 0
        
        for keyword in keywords:
            # Check if keyword appears in column names
            if re.search(r'\b' + keyword + r'\b', column_text):
                matches.append(keyword)
                # Weight based on keyword importance (longer keywords = more specific)
                weight = len(keyword) / 10.0 + 1.0
                score += weight
        
        if matches:
            domain_scores[domain] = score
            domain_matches[domain] = matches
    
    # If no matches, default to generic
    if not domain_scores:
        return {
            "domain": "generic",
            "confidence": 0.0,
            "matched_keywords": [],
            "visualization_config": {
                "primary_charts": ["time_series", "bar_chart"],
                "metrics_focus": ["value", "count"],
                "thresholds": None,
                "forecasting_method": "linear"
            },
            "domain_description": "Generic analysis - no specific domain detected"
        }
    
    # Get best matching domain
    best_domain = max(domain_scores, key=domain_scores.get)
    best_score = domain_scores[best_domain]
    
    # Calculate confidence (normalize by number of matches)
    max_possible_score = len(DOMAIN_PATTERNS[best_domain]) * 2.0  # Rough estimate
    confidence = min(best_score / max_possible_score, 1.0)
    
    # Get visualization config
    viz_config = DOMAIN_VISUALIZATION_CONFIGS.get(best_domain, {})
    
    # Domain descriptions
    domain_descriptions = {
        "sre_infrastructure": "Site Reliability Engineering & Infrastructure Monitoring",
        "trading_finance": "Trading & Financial Markets Analysis",
        "payments": "Payment Processing & Transaction Analysis",
        "capacity_planning": "Resource Capacity Planning & Forecasting",
        "food_economics": "Food Prices & Agricultural Economics",
        "travel_transportation": "Travel & Transportation Analytics",
        "expenses_budget": "Expense Management & Budget Analysis",
        "latency_performance": "Latency & Performance Monitoring"
    }
    
    return {
        "domain": best_domain,
        "confidence": confidence,
        "matched_keywords": domain_matches[best_domain],
        "visualization_config": viz_config,
        "domain_description": domain_descriptions.get(best_domain, best_domain.replace("_", " ").title())
    }


def get_domain_specific_insights(
    domain: str,
    df: pd.DataFrame,
    target_column: str,
    predictions: Any = None
) -> Dict[str, Any]:
    """
    Generate domain-specific insights and recommendations
    """
    
    insights = {
        "domain": domain,
        "recommendations": [],
        "key_metrics": {},
        "alerts": []
    }
    
    if domain == "sre_infrastructure":
        # Check for capacity issues
        if target_column and target_column in df.columns:
            current_util = df[target_column].mean()
            peak_util = df[target_column].max()
            
            insights["key_metrics"] = {
                "current_utilization": f"{current_util:.1f}%",
                "peak_utilization": f"{peak_util:.1f}%",
                "headroom": f"{100 - current_util:.1f}%"
            }
            
            if current_util > 75:
                insights["alerts"].append({
                    "level": "warning",
                    "message": f"Current utilization ({current_util:.1f}%) is approaching capacity threshold (75%)"
                })
            
            if peak_util > 90:
                insights["alerts"].append({
                    "level": "critical",
                    "message": f"Peak utilization ({peak_util:.1f}%) exceeds hard threshold (90%)"
                })
            
            insights["recommendations"] = [
                "Monitor capacity trends closely",
                "Consider scaling resources if utilization consistently > 75%",
                "Set up automated alerts for threshold violations"
            ]
    
    elif domain == "trading_finance":
        insights["recommendations"] = [
            "Analyze volume patterns during market hours",
            "Monitor for unusual trading activity",
            "Track price volatility and spreads"
        ]
    
    elif domain == "payments":
        if target_column and "status" in target_column.lower():
            success_rate = (df[target_column] == "success").mean() * 100 if target_column in df.columns else None
            if success_rate and success_rate < 95:
                insights["alerts"].append({
                    "level": "warning",
                    "message": f"Payment success rate ({success_rate:.1f}%) is below target (95%)"
                })
    
    # Add more domain-specific logic as needed
    
    return insights
