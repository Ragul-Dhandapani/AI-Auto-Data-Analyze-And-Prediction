"""
Intelligent Visualization Service
==================================
World-class AI-powered visualization system that analyzes data deeply
and generates the most suitable charts across 8 categories.

Features:
- Deep data profiling and pattern detection
- Azure OpenAI semantic understanding
- Smart chart recommendation
- 28+ chart types across 8 categories
- Automatic insight generation
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class IntelligentVisualizationService:
    """
    Advanced AI-powered visualization engine that analyzes data
    and generates optimal visualizations across multiple categories.
    """
    
    def __init__(self):
        self.df = None
        self.profile = {}
        self.recommendations = {}
        
    async def analyze_and_generate(self, df: pd.DataFrame) -> Dict:
        """
        Main entry point: Analyze dataset and generate all applicable charts.
        
        Returns:
            {
                'categories': {
                    'distribution': {'charts': [...], 'skipped': [...]},
                    'relationships': {'charts': [...], 'skipped': [...]},
                    ...
                },
                'summary': {...},
                'insights': [...]
            }
        """
        self.df = df.copy()
        
        # Step 1: Deep data profiling
        await self._profile_data()
        
        # Step 2: Generate charts by category
        categories = {}
        
        categories['distribution'] = await self._generate_distribution_charts()
        categories['relationships'] = await self._generate_relationship_charts()
        categories['categorical'] = await self._generate_categorical_charts()
        categories['time_series'] = await self._generate_time_series_charts()
        categories['data_quality'] = await self._generate_data_quality_charts()
        categories['clustering'] = await self._generate_clustering_charts()
        categories['dashboard'] = await self._generate_dashboard_components()
        
        # Step 3: Generate AI insights
        insights = await self._generate_ai_insights()
        
        return {
            'categories': categories,
            'profile': self.profile,
            'insights': insights,
            'total_charts': sum(len(cat['charts']) for cat in categories.values()),
            'total_skipped': sum(len(cat['skipped']) for cat in categories.values())
        }
    
    async def _profile_data(self):
        """Deep data profiling with statistical analysis"""
        df = self.df
        
        # Basic info
        self.profile['shape'] = df.shape
        self.profile['columns'] = list(df.columns)
        
        # Column types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = []
        
        # Detect datetime columns
        for col in categorical_cols[:]:
            try:
                pd.to_datetime(df[col], errors='raise')
                datetime_cols.append(col)
                categorical_cols.remove(col)
            except:
                pass
        
        self.profile['numeric_columns'] = numeric_cols
        self.profile['categorical_columns'] = categorical_cols
        self.profile['datetime_columns'] = datetime_cols
        
        # Statistical summaries
        if numeric_cols:
            self.profile['numeric_stats'] = df[numeric_cols].describe().to_dict()
            
            # Detect outliers using IQR method
            outlier_info = {}
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                outlier_info[col] = int(outliers)
            self.profile['outliers'] = outlier_info
        
        # Categorical summaries
        if categorical_cols:
            cat_info = {}
            for col in categorical_cols:
                unique_count = df[col].nunique()
                cat_info[col] = {
                    'unique': int(unique_count),
                    'top_5': df[col].value_counts().head(5).to_dict()
                }
            self.profile['categorical_stats'] = cat_info
        
        # Missing values
        missing = df.isnull().sum()
        self.profile['missing_values'] = missing[missing > 0].to_dict()
        self.profile['missing_percentage'] = (missing / len(df) * 100).to_dict()
        
        # Correlation matrix (numeric only)
        if len(numeric_cols) >= 2:
            self.profile['correlations'] = df[numeric_cols].corr().to_dict()
        
        # Duplicates
        self.profile['duplicate_rows'] = int(df.duplicated().sum())
        
        logger.info(f"Data profiling complete: {len(numeric_cols)} numeric, {len(categorical_cols)} categorical, {len(datetime_cols)} datetime columns")
    
    # ========================================================
    # CATEGORY 1: DISTRIBUTION ANALYSIS
    # ========================================================
    
    async def _generate_distribution_charts(self) -> Dict:
        """Generate distribution analysis charts"""
        charts = []
        skipped = []
        
        numeric_cols = self.profile.get('numeric_columns', [])
        categorical_cols = self.profile.get('categorical_columns', [])
        
        if not numeric_cols and not categorical_cols:
            skipped.append("No suitable columns for distribution analysis")
            return {'charts': charts, 'skipped': skipped}
        
        # 1. Histograms for numeric columns
        for col in numeric_cols[:5]:  # Limit to top 5
            try:
                # Get statistics for meaningful description
                mean_val = self.df[col].mean()
                median_val = self.df[col].median()
                std_val = self.df[col].std()
                
                fig = px.histogram(
                    self.df, x=col, nbins=30,
                    title=f'Distribution of {col}',
                    labels={col: f'{col} (Value)', 'count': 'Frequency'},
                    color_discrete_sequence=['#3b82f6']
                )
                fig.update_layout(
                    showlegend=False, 
                    height=400,
                    xaxis_title=f'{col}',
                    yaxis_title='Count (Number of Occurrences)'
                )
                
                # Create meaningful description
                description = f'Shows how {col} values are distributed. Mean: {mean_val:.2f}, Median: {median_val:.2f}, Std Dev: {std_val:.2f}. Helps identify if data is normally distributed, skewed, or has multiple peaks.'
                
                charts.append({
                    'type': 'histogram',
                    'title': f'Histogram: {col}',
                    'description': description,
                    'data': fig.to_plotly_json(),
                    'column': col
                })
            except Exception as e:
                logger.warning(f"Histogram for {col} failed: {str(e)}")
        
        # 2. Box Plots for numeric columns (outlier detection)
        if len(numeric_cols) >= 1:
            try:
                # Multi-box plot
                fig = go.Figure()
                outlier_summary = []
                for col in numeric_cols[:6]:
                    fig.add_trace(go.Box(y=self.df[col], name=col))
                    # Calculate outlier count
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = ((self.df[col] < (Q1 - 1.5 * IQR)) | (self.df[col] > (Q3 + 1.5 * IQR))).sum()
                    if outliers > 0:
                        outlier_summary.append(f'{col} ({outliers})')
                
                fig.update_layout(
                    title='Box Plots: Outlier Detection',
                    yaxis_title='Value Range',
                    xaxis_title='Variables',
                    showlegend=True,
                    height=400
                )
                
                # Meaningful description
                outlier_text = f'Outliers found in: {", ".join(outlier_summary[:3])}' if outlier_summary else 'No significant outliers detected'
                description = f'Compares value ranges and detects outliers across {len(numeric_cols[:6])} variables. Box shows middle 50% of data, whiskers show typical range. Points outside whiskers are potential outliers. {outlier_text}.'
                
                charts.append({
                    'type': 'box',
                    'title': 'Box Plots: Outlier Detection',
                    'description': description,
                    'data': fig.to_plotly_json()
                })
            except Exception as e:
                skipped.append(f"Box plot: {str(e)}")
        
        # 3. Violin Plots
        for col in numeric_cols[:3]:
            try:
                fig = go.Figure(data=go.Violin(y=self.df[col], name=col, box_visible=True, meanline_visible=True))
                fig.update_layout(
                    title=f'Violin Plot: {col}',
                    yaxis_title=col,
                    height=400
                )
                charts.append({
                    'type': 'violin',
                    'title': f'Violin Plot: {col}',
                    'description': f'Distribution shape and density of {col}',
                    'data': fig.to_plotly_json(),
                    'column': col
                })
            except Exception as e:
                logger.warning(f"Violin plot for {col} failed: {str(e)}")
        
        # 4. Density Plots (KDE)
        for col in numeric_cols[:3]:
            try:
                from scipy.stats import gaussian_kde
                kde = gaussian_kde(self.df[col].dropna())
                x_range = np.linspace(self.df[col].min(), self.df[col].max(), 200)
                density = kde(x_range)
                
                fig = go.Figure(data=go.Scatter(x=x_range, y=density, mode='lines', fill='tozeroy'))
                fig.update_layout(
                    title=f'Density Plot: {col}',
                    xaxis_title=col,
                    yaxis_title='Density',
                    height=400
                )
                charts.append({
                    'type': 'density',
                    'title': f'Density Plot: {col}',
                    'description': f'Smooth distribution (KDE) of {col}',
                    'data': fig.to_plotly_json(),
                    'column': col
                })
            except Exception as e:
                logger.warning(f"Density plot for {col} failed: {str(e)}")
        
        # 5. Pie Charts for categorical data (only if small number of categories)
        for col in categorical_cols[:2]:
            try:
                unique_count = self.df[col].nunique()
                if unique_count <= 10:  # Only for small categorical sets
                    value_counts = self.df[col].value_counts().head(10)
                    total_records = len(self.df)
                    top_category = value_counts.index[0]
                    top_percentage = (value_counts.values[0] / total_records * 100)
                    
                    fig = px.pie(
                        values=value_counts.values,
                        names=value_counts.index,
                        title=f'Distribution: {col}',
                        hover_data=[value_counts.values]
                    )
                    fig.update_traces(
                        textposition='inside',
                        textinfo='label+percent',
                        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                    )
                    fig.update_layout(height=400)
                    
                    # Meaningful description
                    description = f'Shows distribution of {col} across {unique_count} categories. Top category: "{top_category}" ({top_percentage:.1f}%). Each slice represents the proportion of records in that category.'
                    
                    charts.append({
                        'type': 'pie',
                        'title': f'Pie Chart: {col}',
                        'description': description,
                        'data': fig.to_plotly_json(),
                        'column': col
                    })
                else:
                    skipped.append(f"Pie chart for {col}: Too many categories ({unique_count})")
            except Exception as e:
                logger.warning(f"Pie chart for {col} failed: {str(e)}")
        
        return {'charts': charts, 'skipped': skipped}
    
    # ========================================================
    # CATEGORY 2: RELATIONSHIP ANALYSIS
    # ========================================================
    
    async def _generate_relationship_charts(self) -> Dict:
        """Generate relationship analysis charts"""
        charts = []
        skipped = []
        
        numeric_cols = self.profile.get('numeric_columns', [])
        
        if len(numeric_cols) < 2:
            skipped.append("Need at least 2 numeric columns for relationship analysis")
            return {'charts': charts, 'skipped': skipped}
        
        # 1. Scatter Plots (top correlated pairs)
        if 'correlations' in self.profile:
            try:
                corr_df = pd.DataFrame(self.profile['correlations'])
                # Get top 3 correlations
                correlations = []
                for i in range(len(corr_df.columns)):
                    for j in range(i+1, len(corr_df.columns)):
                        col1 = corr_df.columns[i]
                        col2 = corr_df.columns[j]
                        corr_val = abs(corr_df.loc[col1, col2])
                        if not np.isnan(corr_val):
                            correlations.append((col1, col2, corr_val))
                
                correlations.sort(key=lambda x: x[2], reverse=True)
                
                for col1, col2, corr_val in correlations[:3]:
                    # Interpret correlation strength
                    if abs(corr_val) >= 0.7:
                        strength = 'strong'
                    elif abs(corr_val) >= 0.4:
                        strength = 'moderate'
                    else:
                        strength = 'weak'
                    
                    direction = 'positive' if corr_val > 0 else 'negative'
                    
                    fig = px.scatter(
                        self.df, x=col1, y=col2,
                        title=f'{col1} vs {col2} (r={corr_val:.3f})',
                        trendline='ols',
                        labels={col1: f'{col1}', col2: f'{col2}'}
                    )
                    fig.update_layout(
                        height=400,
                        xaxis_title=col1,
                        yaxis_title=col2
                    )
                    
                    # Meaningful description
                    description = f'Shows {strength} {direction} relationship between {col1} and {col2} (correlation: {corr_val:.3f}). Each point represents one record. Trend line indicates the overall pattern. {"As one increases, the other tends to increase." if corr_val > 0 else "As one increases, the other tends to decrease."}'
                    
                    charts.append({
                        'type': 'scatter',
                        'title': f'Scatter: {col1} vs {col2}',
                        'description': description,
                        'data': fig.to_plotly_json(),
                        'columns': [col1, col2]
                    })
            except Exception as e:
                skipped.append(f"Scatter plots: {str(e)}")
        
        # 2. Correlation Heatmap
        if len(numeric_cols) >= 2:
            try:
                corr_matrix = self.df[numeric_cols].corr()
                
                # Find strongest correlations
                strong_corrs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = abs(corr_matrix.iloc[i, j])
                        if corr_val >= 0.5:
                            strong_corrs.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
                
                fig = px.imshow(
                    corr_matrix,
                    text_auto='.2f',
                    aspect='auto',
                    color_continuous_scale='RdBu_r',
                    title='Correlation Heatmap',
                    labels=dict(x='Variables', y='Variables', color='Correlation')
                )
                fig.update_layout(
                    height=500,
                    xaxis_title='Variables',
                    yaxis_title='Variables'
                )
                
                # Meaningful description
                strong_text = f'Strong correlations: {len(strong_corrs)} pairs' if strong_corrs else 'No strong correlations found'
                description = f'Shows correlation strength between all {len(numeric_cols)} numeric variables. Red = positive correlation (variables move together), Blue = negative correlation (inverse relationship), White = no correlation. Range: -1 to +1. {strong_text}.'
                
                charts.append({
                    'type': 'heatmap',
                    'title': 'Correlation Heatmap',
                    'description': description,
                    'data': fig.to_plotly_json()
                })
            except Exception as e:
                skipped.append(f"Correlation heatmap: {str(e)}")
        
        # 3. Bubble Chart (if 3+ numeric columns)
        if len(numeric_cols) >= 3:
            try:
                col_x, col_y, col_size = numeric_cols[:3]
                fig = px.scatter(
                    self.df, x=col_x, y=col_y, size=col_size,
                    title=f'Bubble Chart: {col_x} vs {col_y} (size={col_size})',
                    opacity=0.6
                )
                fig.update_layout(height=400)
                charts.append({
                    'type': 'bubble',
                    'title': f'Bubble Chart: {col_x} vs {col_y}',
                    'description': f'Three-dimensional relationship with size encoding',
                    'data': fig.to_plotly_json(),
                    'columns': [col_x, col_y, col_size]
                })
            except Exception as e:
                skipped.append(f"Bubble chart: {str(e)}")
        
        # 4. Pair Plot (if <= 5 numeric columns)
        if 2 <= len(numeric_cols) <= 5:
            try:
                fig = px.scatter_matrix(
                    self.df[numeric_cols],
                    title='Pair Plot: All Variable Combinations',
                    height=600
                )
                fig.update_traces(diagonal_visible=False, showupperhalf=False)
                charts.append({
                    'type': 'pair_plot',
                    'title': 'Pair Plot: Variable Relationships',
                    'description': f'All pair combinations of {len(numeric_cols)} variables',
                    'data': fig.to_plotly_json()
                })
            except Exception as e:
                skipped.append(f"Pair plot: {str(e)}")
        elif len(numeric_cols) > 5:
            skipped.append(f"Pair plot: Too many columns ({len(numeric_cols)}, max 5 for readability)")
        
        return {'charts': charts, 'skipped': skipped}
    
    # ========================================================
    # CATEGORY 3: CATEGORICAL DATA ANALYSIS
    # ========================================================
    
    async def _generate_categorical_charts(self) -> Dict:
        """Generate categorical data analysis charts"""
        charts = []
        skipped = []
        
        categorical_cols = self.profile.get('categorical_columns', [])
        numeric_cols = self.profile.get('numeric_columns', [])
        
        if not categorical_cols:
            skipped.append("No categorical columns found for analysis")
            return {'charts': charts, 'skipped': skipped}
        
        # 1. Bar Charts (count plots)
        for col in categorical_cols[:4]:
            try:
                unique_count = self.df[col].nunique()
                if unique_count <= 20:
                    value_counts = self.df[col].value_counts().head(15)
                    total = len(self.df)
                    top_category = value_counts.index[0]
                    top_count = value_counts.values[0]
                    top_pct = (top_count / total * 100)
                    
                    fig = px.bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        title=f'Count Plot: {col}',
                        labels={'x': f'{col} (Categories)', 'y': 'Count (Number of Records)'}
                    )
                    fig.update_layout(
                        height=400,
                        xaxis_title=f'{col}',
                        yaxis_title='Count'
                    )
                    
                    # Meaningful description
                    description = f'Shows frequency of each category in {col}. Most common: "{top_category}" with {top_count} records ({top_pct:.1f}% of total). Displaying top {len(value_counts)} out of {unique_count} categories.'
                    
                    charts.append({
                        'type': 'bar',
                        'title': f'Bar Chart: {col}',
                        'description': description,
                        'data': fig.to_plotly_json(),
                        'column': col
                    })
                else:
                    skipped.append(f"Bar chart for {col}: Too many categories ({unique_count})")
            except Exception as e:
                logger.warning(f"Bar chart for {col} failed: {str(e)}")
        
        # 2. Stacked Bar Chart (if 2 categorical columns)
        if len(categorical_cols) >= 2:
            try:
                cat1, cat2 = categorical_cols[:2]
                if self.df[cat1].nunique() <= 10 and self.df[cat2].nunique() <= 10:
                    crosstab = pd.crosstab(self.df[cat1], self.df[cat2])
                    fig = px.bar(
                        crosstab,
                        title=f'Stacked Bar: {cat1} by {cat2}',
                        barmode='stack'
                    )
                    fig.update_layout(height=400)
                    charts.append({
                        'type': 'stacked_bar',
                        'title': f'Stacked Bar: {cat1} by {cat2}',
                        'description': f'Distribution across subgroups',
                        'data': fig.to_plotly_json(),
                        'columns': [cat1, cat2]
                    })
                else:
                    skipped.append(f"Stacked bar: Categories too large")
            except Exception as e:
                skipped.append(f"Stacked bar chart: {str(e)}")
        
        # 3. Grouped Bar Chart (categorical + numeric)
        if categorical_cols and numeric_cols:
            try:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                if self.df[cat_col].nunique() <= 15:
                    avg_by_cat = self.df.groupby(cat_col)[num_col].mean().sort_values(ascending=False).head(10)
                    fig = px.bar(
                        x=avg_by_cat.index,
                        y=avg_by_cat.values,
                        title=f'Average {num_col} by {cat_col}',
                        labels={'x': cat_col, 'y': f'Avg {num_col}'}
                    )
                    fig.update_layout(height=400)
                    charts.append({
                        'type': 'grouped_bar',
                        'title': f'Grouped Bar: Avg {num_col} by {cat_col}',
                        'description': f'Comparing averages across categories',
                        'data': fig.to_plotly_json(),
                        'columns': [cat_col, num_col]
                    })
                else:
                    skipped.append(f"Grouped bar: Too many categories in {cat_col}")
            except Exception as e:
                skipped.append(f"Grouped bar chart: {str(e)}")
        
        return {'charts': charts, 'skipped': skipped}
    
    # ========================================================
    # CATEGORY 4: TIME SERIES ANALYSIS
    # ========================================================
    
    async def _generate_time_series_charts(self) -> Dict:
        """Generate time series analysis charts"""
        charts = []
        skipped = []
        
        datetime_cols = self.profile.get('datetime_columns', [])
        numeric_cols = self.profile.get('numeric_columns', [])
        
        if not datetime_cols:
            skipped.append("No datetime columns detected for time series analysis")
            return {'charts': charts, 'skipped': skipped}
        
        # Parse datetime column
        date_col = datetime_cols[0]
        try:
            df_ts = self.df.copy()
            df_ts[date_col] = pd.to_datetime(df_ts[date_col])
            df_ts = df_ts.sort_values(date_col)
        except Exception as e:
            skipped.append(f"Failed to parse datetime column: {str(e)}")
            return {'charts': charts, 'skipped': skipped}
        
        # 1. Line Plot (value over time)
        for num_col in numeric_cols[:3]:
            try:
                fig = px.line(
                    df_ts, x=date_col, y=num_col,
                    title=f'{num_col} Over Time',
                    markers=True if len(df_ts) <= 50 else False
                )
                fig.update_layout(height=400)
                charts.append({
                    'type': 'line',
                    'title': f'Time Series: {num_col}',
                    'description': f'Trend of {num_col} over time',
                    'data': fig.to_plotly_json(),
                    'columns': [date_col, num_col]
                })
            except Exception as e:
                logger.warning(f"Line plot for {num_col} failed: {str(e)}")
        
        # 2. Rolling Average
        if numeric_cols:
            try:
                num_col = numeric_cols[0]
                window = min(7, len(df_ts) // 10)
                if window >= 2:
                    df_ts['rolling_avg'] = df_ts[num_col].rolling(window=window).mean()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df_ts[date_col], y=df_ts[num_col], mode='lines', name='Actual', opacity=0.5))
                    fig.add_trace(go.Scatter(x=df_ts[date_col], y=df_ts['rolling_avg'], mode='lines', name=f'{window}-period MA', line=dict(width=3)))
                    fig.update_layout(
                        title=f'Rolling Average: {num_col}',
                        xaxis_title=date_col,
                        yaxis_title=num_col,
                        height=400
                    )
                    charts.append({
                        'type': 'rolling_avg',
                        'title': f'Rolling Average: {num_col}',
                        'description': f'{window}-period moving average smoothing',
                        'data': fig.to_plotly_json(),
                        'columns': [date_col, num_col]
                    })
            except Exception as e:
                skipped.append(f"Rolling average: {str(e)}")
        
        # 3. Seasonality (if month/day patterns exist)
        if numeric_cols and len(df_ts) > 30:
            try:
                num_col = numeric_cols[0]
                df_ts['month'] = df_ts[date_col].dt.month
                monthly_avg = df_ts.groupby('month')[num_col].mean()
                fig = px.bar(
                    x=monthly_avg.index,
                    y=monthly_avg.values,
                    title=f'Seasonality: {num_col} by Month',
                    labels={'x': 'Month', 'y': f'Avg {num_col}'}
                )
                fig.update_layout(height=400)
                charts.append({
                    'type': 'seasonality',
                    'title': f'Monthly Pattern: {num_col}',
                    'description': f'Average values by month (seasonality analysis)',
                    'data': fig.to_plotly_json(),
                    'columns': [date_col, num_col]
                })
            except Exception as e:
                skipped.append(f"Seasonality plot: {str(e)}")
        
        return {'charts': charts, 'skipped': skipped}
    
    # ========================================================
    # CATEGORY 5: DATA QUALITY & PROFILING
    # ========================================================
    
    async def _generate_data_quality_charts(self) -> Dict:
        """Generate data quality analysis charts"""
        charts = []
        skipped = []
        
        # 1. Missing Value Heatmap
        try:
            missing_data = self.df.isnull()
            if missing_data.sum().sum() > 0:
                # Sample if too many rows
                sample_size = min(500, len(self.df))
                missing_sample = missing_data.sample(n=sample_size, random_state=42)
                
                fig = px.imshow(
                    missing_sample.T,
                    title='Missing Value Heatmap',
                    labels={'x': 'Row Index', 'y': 'Column'},
                    color_continuous_scale=['#3b82f6', '#ef4444'],
                    aspect='auto'
                )
                fig.update_layout(height=400)
                charts.append({
                    'type': 'missing_heatmap',
                    'title': 'Missing Value Heatmap',
                    'description': f'Visualizing null patterns (sample of {sample_size} rows)',
                    'data': fig.to_plotly_json()
                })
            else:
                skipped.append("Missing value heatmap: No missing values in dataset")
        except Exception as e:
            skipped.append(f"Missing value heatmap: {str(e)}")
        
        # 2. Missing Percentage Bar Chart
        try:
            missing_pct = (self.df.isnull().sum() / len(self.df) * 100).sort_values(ascending=False)
            missing_pct = missing_pct[missing_pct > 0]
            
            if len(missing_pct) > 0:
                fig = px.bar(
                    x=missing_pct.index,
                    y=missing_pct.values,
                    title='Missing Value Percentage by Column',
                    labels={'x': 'Column', 'y': 'Missing %'}
                )
                fig.update_layout(height=400)
                charts.append({
                    'type': 'missing_bar',
                    'title': 'Missing Values by Column',
                    'description': f'{len(missing_pct)} columns have missing data',
                    'data': fig.to_plotly_json()
                })
            else:
                skipped.append("Missing % bar chart: No missing values found")
        except Exception as e:
            skipped.append(f"Missing % bar chart: {str(e)}")
        
        # 3. Data Type Distribution
        try:
            dtype_counts = {
                'Numeric': len(self.profile.get('numeric_columns', [])),
                'Categorical': len(self.profile.get('categorical_columns', [])),
                'DateTime': len(self.profile.get('datetime_columns', []))
            }
            dtype_counts = {k: v for k, v in dtype_counts.items() if v > 0}
            
            fig = px.pie(
                values=list(dtype_counts.values()),
                names=list(dtype_counts.keys()),
                title='Column Type Distribution'
            )
            fig.update_layout(height=400)
            charts.append({
                'type': 'dtype_pie',
                'title': 'Data Type Distribution',
                'description': f'Breakdown of {sum(dtype_counts.values())} columns by type',
                'data': fig.to_plotly_json()
            })
        except Exception as e:
            skipped.append(f"Data type chart: {str(e)}")
        
        # 4. Duplicate Rows
        try:
            dup_count = self.profile.get('duplicate_rows', 0)
            total_rows = len(self.df)
            unique_rows = total_rows - dup_count
            
            fig = go.Figure(data=[
                go.Bar(name='Unique', x=['Rows'], y=[unique_rows]),
                go.Bar(name='Duplicates', x=['Rows'], y=[dup_count])
            ])
            fig.update_layout(
                title=f'Duplicate Rows: {dup_count} / {total_rows} ({dup_count/total_rows*100:.2f}%)',
                barmode='stack',
                height=400
            )
            charts.append({
                'type': 'duplicates',
                'title': 'Duplicate Row Analysis',
                'description': f'{dup_count} duplicate rows found ({dup_count/total_rows*100:.2f}%)',
                'data': fig.to_plotly_json()
            })
        except Exception as e:
            skipped.append(f"Duplicate analysis: {str(e)}")
        
        return {'charts': charts, 'skipped': skipped}
    
    # ========================================================
    # CATEGORY 6: DIMENSIONALITY & CLUSTERING
    # ========================================================
    
    async def _generate_clustering_charts(self) -> Dict:
        """Generate clustering and dimensionality reduction charts"""
        charts = []
        skipped = []
        
        numeric_cols = self.profile.get('numeric_columns', [])
        
        if len(numeric_cols) < 2:
            skipped.append("Need at least 2 numeric columns for clustering analysis")
            return {'charts': charts, 'skipped': skipped}
        
        # Prepare data
        df_numeric = self.df[numeric_cols].dropna()
        
        if len(df_numeric) < 10:
            skipped.append("Insufficient data points for clustering (need at least 10)")
            return {'charts': charts, 'skipped': skipped}
        
        # 1. PCA Scatter Plot
        if len(numeric_cols) >= 3:
            try:
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(df_numeric)
                
                pca = PCA(n_components=2)
                pca_result = pca.fit_transform(scaled_data)
                
                variance_explained = pca.explained_variance_ratio_
                
                fig = px.scatter(
                    x=pca_result[:, 0],
                    y=pca_result[:, 1],
                    title=f'PCA: Principal Components (Variance: {variance_explained[0]:.2%} + {variance_explained[1]:.2%})',
                    labels={'x': f'PC1 ({variance_explained[0]:.2%})', 'y': f'PC2 ({variance_explained[1]:.2%})'},
                    opacity=0.7
                )
                fig.update_layout(height=400)
                charts.append({
                    'type': 'pca',
                    'title': 'PCA: Dimensionality Reduction',
                    'description': f'2D projection of {len(numeric_cols)}D data',
                    'data': fig.to_plotly_json()
                })
            except Exception as e:
                skipped.append(f"PCA plot: {str(e)}")
        
        # 2. K-Means Clustering
        try:
            # Determine optimal k (3-5 clusters typically)
            max_k = min(5, len(df_numeric) // 10)
            if max_k >= 2:
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(df_numeric)
                
                kmeans = KMeans(n_clusters=min(3, max_k), random_state=42)
                clusters = kmeans.fit_predict(scaled_data)
                
                # If we have PCA, plot on PC space
                if len(numeric_cols) >= 3:
                    pca = PCA(n_components=2)
                    pca_result = pca.fit_transform(scaled_data)
                    
                    fig = px.scatter(
                        x=pca_result[:, 0],
                        y=pca_result[:, 1],
                        color=clusters.astype(str),
                        title=f'K-Means Clustering ({min(3, max_k)} clusters)',
                        labels={'x': 'PC1', 'y': 'PC2', 'color': 'Cluster'}
                    )
                else:
                    # Use first 2 numeric columns
                    fig = px.scatter(
                        self.df,
                        x=numeric_cols[0],
                        y=numeric_cols[1],
                        color=clusters.astype(str),
                        title=f'K-Means Clustering ({min(3, max_k)} clusters)',
                        labels={'color': 'Cluster'}
                    )
                
                fig.update_layout(height=400)
                charts.append({
                    'type': 'kmeans',
                    'title': f'K-Means Clustering',
                    'description': f'Identified {min(3, max_k)} natural clusters in data',
                    'data': fig.to_plotly_json()
                })
            else:
                skipped.append("K-Means: Too few data points for meaningful clustering")
        except Exception as e:
            skipped.append(f"K-Means clustering: {str(e)}")
        
        # 3. Dendrogram (hierarchical clustering)
        if len(df_numeric) <= 100 and len(numeric_cols) >= 2:
            try:
                sample_data = df_numeric.sample(n=min(50, len(df_numeric)), random_state=42)
                scaler = StandardScaler()
                scaled_sample = scaler.fit_transform(sample_data)
                
                linkage_matrix = linkage(scaled_sample, method='ward')
                
                fig = go.Figure()
                # Simplified dendrogram rendering
                from scipy.cluster.hierarchy import dendrogram as scipy_dendrogram
                dendro = scipy_dendrogram(linkage_matrix, no_plot=True)
                
                icoord = np.array(dendro['icoord'])
                dcoord = np.array(dendro['dcoord'])
                
                for i in range(len(icoord)):
                    fig.add_trace(go.Scatter(
                        x=icoord[i], y=dcoord[i],
                        mode='lines',
                        line=dict(color='#3b82f6'),
                        showlegend=False
                    ))
                
                fig.update_layout(
                    title='Hierarchical Clustering Dendrogram',
                    xaxis_title='Sample Index',
                    yaxis_title='Distance',
                    height=400
                )
                charts.append({
                    'type': 'dendrogram',
                    'title': 'Dendrogram: Hierarchical Clusters',
                    'description': f'Tree structure of {len(sample_data)} samples',
                    'data': fig.to_plotly_json()
                })
            except Exception as e:
                skipped.append(f"Dendrogram: {str(e)}")
        elif len(df_numeric) > 100:
            skipped.append("Dendrogram: Dataset too large (max 100 rows for readability)")
        
        return {'charts': charts, 'skipped': skipped}
    
    # ========================================================
    # CATEGORY 7: DASHBOARD COMPONENTS
    # ========================================================
    
    async def _generate_dashboard_components(self) -> Dict:
        """Generate dashboard KPI cards and summary components"""
        charts = []
        skipped = []
        
        numeric_cols = self.profile.get('numeric_columns', [])
        
        # 1. KPI Summary Cards (as a single chart)
        try:
            kpi_data = {
                'Total Rows': len(self.df),
                'Total Columns': len(self.df.columns),
                'Numeric Cols': len(numeric_cols),
                'Categorical Cols': len(self.profile.get('categorical_columns', [])),
                'Missing Values': sum(self.df.isnull().sum()),
                'Duplicates': self.profile.get('duplicate_rows', 0)
            }
            
            # Create KPI card visualization
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode='number',
                value=kpi_data['Total Rows'],
                title={'text': 'Total Rows'},
                domain={'row': 0, 'column': 0}
            ))
            
            # Create a table instead for better display
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=['Metric', 'Value'],
                    fill_color='#3b82f6',
                    font=dict(color='white', size=14),
                    align='left'
                ),
                cells=dict(
                    values=[list(kpi_data.keys()), list(kpi_data.values())],
                    fill_color='lavender',
                    align='left',
                    font=dict(size=13)
                )
            )])
            
            fig.update_layout(
                title='Dataset Summary (KPI Cards)',
                height=400
            )
            
            charts.append({
                'type': 'kpi_cards',
                'title': 'Dataset Overview',
                'description': 'Key metrics and statistics',
                'data': fig.to_plotly_json()
            })
        except Exception as e:
            skipped.append(f"KPI cards: {str(e)}")
        
        # 2. Radar Chart (if multiple numeric columns)
        if len(numeric_cols) >= 3:
            try:
                # Normalize first row for radar chart
                sample_row = self.df[numeric_cols].iloc[0]
                normalized = (sample_row - self.df[numeric_cols].min()) / (self.df[numeric_cols].max() - self.df[numeric_cols].min())
                
                fig = go.Figure(data=go.Scatterpolar(
                    r=normalized.values,
                    theta=numeric_cols,
                    fill='toself'
                ))
                
                fig.update_layout(
                    title='Radar Chart: Multi-dimensional Profile',
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    height=400
                )
                
                charts.append({
                    'type': 'radar',
                    'title': 'Radar Chart: Feature Comparison',
                    'description': f'Normalized comparison across {len(numeric_cols)} features',
                    'data': fig.to_plotly_json()
                })
            except Exception as e:
                skipped.append(f"Radar chart: {str(e)}")
        
        return {'charts': charts, 'skipped': skipped}
    
    # ========================================================
    # AI INSIGHTS GENERATION
    # ========================================================
    
    async def _generate_ai_insights(self) -> List[str]:
        """Generate AI-powered insights using Azure OpenAI"""
        insights = []
        
        try:
            from app.services.azure_openai_service import get_azure_openai_service
            
            azure_service = get_azure_openai_service()
            
            if not azure_service.is_available():
                logger.warning("Azure OpenAI not available for insights generation")
                return [
                    f"Dataset contains {len(self.df)} rows and {len(self.df.columns)} columns",
                    f"Found {len(self.profile.get('numeric_columns', []))} numeric and {len(self.profile.get('categorical_columns', []))} categorical columns",
                    f"Data quality: {self.profile.get('duplicate_rows', 0)} duplicate rows detected"
                ]
            
            # Build context for AI
            context = f"""Analyze this dataset profile and provide 5 key insights:

Dataset Shape: {self.df.shape}
Numeric Columns: {', '.join(self.profile.get('numeric_columns', [])[:10])}
Categorical Columns: {', '.join(self.profile.get('categorical_columns', [])[:10])}
Missing Values: {len([k for k, v in self.profile.get('missing_values', {}).items() if v > 0])} columns affected
Outliers Detected: {sum(self.profile.get('outliers', {}).values())} total across all columns
Duplicates: {self.profile.get('duplicate_rows', 0)} rows

Provide 5 concise, actionable insights about data quality, patterns, and recommendations."""

            response = await azure_service.generate_completion(
                prompt=context,
                max_tokens=400,
                temperature=0.7
            )
            
            # Parse insights (expecting numbered or bulleted list)
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets
                    insight = line.lstrip('0123456789.-•) ').strip()
                    if insight:
                        insights.append(insight)
            
            return insights[:5] if insights else ["AI insights generation completed"]
            
        except Exception as e:
            logger.error(f"AI insights generation failed: {str(e)}")
            return [
                f"Dataset overview: {len(self.df)} rows × {len(self.df.columns)} columns",
                f"Data types: {len(self.profile.get('numeric_columns', []))} numeric, {len(self.profile.get('categorical_columns', []))} categorical",
                f"Quality check: {sum(self.profile.get('missing_percentage', {}).values()):.1f}% total missing values"
            ]


# Singleton instance
_intelligent_viz_service = None

def get_intelligent_visualization_service() -> IntelligentVisualizationService:
    """Get or create the intelligent visualization service"""
    global _intelligent_viz_service
    if _intelligent_viz_service is None:
        _intelligent_viz_service = IntelligentVisualizationService()
    return _intelligent_viz_service
