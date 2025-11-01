from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from io import BytesIO
import json
import cx_Oracle
import psycopg2
import pymysql
import pyodbc
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from statsmodels.tsa.arima.model import ARIMA
import xgboost as xgb
import plotly.graph_objects as go
import plotly.express as px
from emergentintegrations.llm.chat import LlmChat, UserMessage
import traceback

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# GridFS for large file storage
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
fs = AsyncIOMotorGridFSBucket(db)



# Helper function to get dataset data from GridFS or regular collection
async def get_dataset_dataframe(dataset_id: str):
    """Retrieve dataset as DataFrame from GridFS or regular collection"""
    # Get dataset metadata
    dataset = await db.datasets.find_one({"id": dataset_id}, {"_id": 0})
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    
    # Check storage method
    if dataset.get('storage_method') == 'gridfs':
        # Read from GridFS
        grid_out = await fs.open_download_stream_by_name(f"dataset_{dataset_id}")
        contents = await grid_out.read()
        
        # Parse based on file type
        if dataset['original_name'].endswith('.csv'):
            df = pd.read_csv(BytesIO(contents), low_memory=False)
        elif dataset['original_name'].endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(400, "Unsupported file format")
    else:
        # Read from regular collection
        data_doc = await db.dataset_data.find_one({"dataset_id": dataset_id}, {"_id": 0})
        if not data_doc:
            raise HTTPException(404, "Dataset data not found")
        df = pd.DataFrame(data_doc['data'])
    
    return df

# LLM Setup
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Increase max request size for large file uploads
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class LargeUploadMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Set a larger max body size (500MB)
        request._receive = request.receive
        return await call_next(request)

app.add_middleware(LargeUploadMiddleware)

api_router = APIRouter(prefix="/api")

# Models
class DataSourceConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: str  # 'file', 'oracle', 'postgresql', 'mongodb'
    name: str
    config: Dict[str, Any] = {}  # Connection details
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DataSourceTest(BaseModel):
    source_type: str
    config: Dict[str, Any]

class AnalysisRequest(BaseModel):
    dataset_id: str
    analysis_type: str = "holistic"  # 'profile', 'clean', 'predict', 'insights', 'holistic'
    options: Dict[str, Any] = {}

class HolisticRequest(BaseModel):
    dataset_id: str

class DatasetInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    source_type: str
    row_count: int
    column_count: int
    columns: List[str]
    data_preview: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Helper Functions
def test_oracle_connection(config: dict) -> dict:
    """Test Oracle database connection"""
    try:
        dsn = cx_Oracle.makedsn(
            config.get('host'),
            config.get('port', 1521),
            service_name=config.get('service_name')
        )
        conn = cx_Oracle.connect(
            user=config.get('username'),
            password=config.get('password'),
            dsn=dsn
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        cursor.close()
        conn.close()
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def test_postgresql_connection(config: dict) -> dict:
    """Test PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host=config.get('host'),
            port=config.get('port', 5432),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_oracle_tables(config: dict) -> List[str]:
    """List tables from Oracle database"""
    try:
        dsn = cx_Oracle.makedsn(
            config.get('host'),
            config.get('port', 1521),
            service_name=config.get('service_name')
        )
        conn = cx_Oracle.connect(
            user=config.get('username'),
            password=config.get('password'),
            dsn=dsn
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name FROM user_tables 
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise Exception(f"Failed to list tables: {str(e)}")

def get_postgresql_tables(config: dict) -> List[str]:
    """List tables from PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=config.get('host'),
            port=config.get('port', 5432),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise Exception(f"Failed to list tables: {str(e)}")

async def get_mongodb_collections() -> List[str]:
    """List collections from MongoDB"""
    try:
        collections = await db.list_collection_names()
        return [c for c in collections if not c.startswith('system.')]
    except Exception as e:
        raise Exception(f"Failed to list collections: {str(e)}")

def test_mysql_connection(config: dict) -> dict:
    """Test MySQL database connection"""
    try:
        conn = pymysql.connect(
            host=config.get('host'),
            port=int(config.get('port', 3306)),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_mysql_tables(config: dict) -> List[str]:
    """List tables from MySQL database"""
    try:
        conn = pymysql.connect(
            host=config.get('host'),
            port=int(config.get('port', 3306)),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise Exception(f"Failed to list tables: {str(e)}")

def test_sqlserver_connection(config: dict) -> dict:
    """Test SQL Server database connection"""
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config.get('host')},{config.get('port', 1433)};"
            f"DATABASE={config.get('database')};"
            f"UID={config.get('username')};"
            f"PWD={config.get('password')}"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_sqlserver_tables(config: dict) -> List[str]:
    """List tables from SQL Server database"""
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config.get('host')},{config.get('port', 1433)};"
            f"DATABASE={config.get('database')};"
            f"UID={config.get('username')};"
            f"PWD={config.get('password')}"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise Exception(f"Failed to list tables: {str(e)}")

def load_table_data(source_type: str, config: dict, table_name: str) -> pd.DataFrame:
    """Load data from database table"""
    if source_type == 'oracle':
        dsn = cx_Oracle.makedsn(
            config.get('host'),
            config.get('port', 1521),
            service_name=config.get('service_name')
        )
        conn = cx_Oracle.connect(
            user=config.get('username'),
            password=config.get('password'),
            dsn=dsn
        )
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    elif source_type == 'postgresql':
        conn = psycopg2.connect(
            host=config.get('host'),
            port=config.get('port', 5432),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    elif source_type == 'mysql':
        conn = pymysql.connect(
            host=config.get('host'),
            port=int(config.get('port', 3306)),
            database=config.get('database'),
            user=config.get('username'),
            password=config.get('password')
        )
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    elif source_type == 'sqlserver':
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config.get('host')},{config.get('port', 1433)};"
            f"DATABASE={config.get('database')};"
            f"UID={config.get('username')};"
            f"PWD={config.get('password')}"
        )
        conn = pyodbc.connect(conn_str)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

def profile_data(df: pd.DataFrame) -> dict:
    """Generate data profiling report"""
    profile = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": [],
        "missing_values_total": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }
    
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "missing_count": int(df[col].isnull().sum()),
            "missing_percentage": float(df[col].isnull().sum() / len(df) * 100),
            "unique_count": int(df[col].nunique())
        }
        
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["stats"] = {
                "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                "median": float(df[col].median()) if not df[col].isnull().all() else None,
                "std": float(df[col].std()) if not df[col].isnull().all() else None,
                "min": float(df[col].min()) if not df[col].isnull().all() else None,
                "max": float(df[col].max()) if not df[col].isnull().all() else None
            }
        
        profile["columns"].append(col_info)
    
    return profile

def clean_data(df: pd.DataFrame) -> tuple:
    """Auto-clean data"""
    cleaning_report = []
    
    # Remove duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        df = df.drop_duplicates()
        cleaning_report.append(f"Removed {dup_count} duplicate rows")
    
    # Handle missing values
    for col in df.columns:
        missing = df[col].isnull().sum()
        if missing > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].median(), inplace=True)
                cleaning_report.append(f"Filled {missing} missing values in '{col}' with median")
            else:
                df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown', inplace=True)
                cleaning_report.append(f"Filled {missing} missing values in '{col}' with mode")
    
    # Detect and handle outliers for numeric columns
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        if outliers > 0:
            df[col] = df[col].clip(lower_bound, upper_bound)
            cleaning_report.append(f"Clipped {outliers} outliers in '{col}'")
    
    return df, cleaning_report

async def generate_ai_insights(df: pd.DataFrame, profile: dict) -> str:
    """Generate AI insights using LLM"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"analysis_{uuid.uuid4()}",
            system_message="You are a data analysis expert. Provide clear, actionable insights about datasets."
        ).with_model("openai", "gpt-4o-mini")
        
        # Prepare data summary
        summary = f"""Dataset Analysis:
- Rows: {profile['row_count']}
- Columns: {profile['column_count']}
- Missing Values: {profile['missing_values_total']}
- Duplicate Rows: {profile['duplicate_rows']}

Column Details:
"""
        for col in profile['columns'][:10]:  # Limit to first 10 columns
            summary += f"\n- {col['name']} ({col['dtype']}): {col['unique_count']} unique, {col['missing_percentage']:.1f}% missing"
            if 'stats' in col:
                summary += f" | Mean: {col['stats']['mean']:.2f}" if col['stats']['mean'] else ""
        
        message = UserMessage(
            text=f"Analyze this dataset and provide 3-5 key insights, trends, or recommendations:\n{summary}"
        )
        
        insights = await chat.send_message(message)
        return insights
    except Exception as e:
        return f"AI insights generation failed: {str(e)}"

def predict_with_ml(df: pd.DataFrame, target_column: str, model_type: str = "random_forest") -> dict:
    """Run predictive analysis with multiple model options"""
    try:
        # Prepare data
        if target_column not in df.columns:
            return {"error": f"Target column '{target_column}' not found"}
        
        # Select numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_column not in numeric_cols:
            return {"error": "Target column must be numeric"}
        
        feature_cols = [col for col in numeric_cols if col != target_column]
        if not feature_cols:
            return {"error": "No numeric features available for prediction"}
        
        X = df[feature_cols].fillna(df[feature_cols].median())
        y = df[target_column].fillna(df[target_column].median())
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Select and train model
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.linear_model import LinearRegression
        from sklearn.tree import DecisionTreeRegressor
        
        if model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model_name = "Random Forest Regression"
        elif model_type == "gradient_boosting":
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model_name = "Gradient Boosting Regression"
        elif model_type == "linear_regression":
            model = LinearRegression()
            model_name = "Linear Regression"
        elif model_type == "decision_tree":
            model = DecisionTreeRegressor(random_state=42)
            model_name = "Decision Tree Regression"
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model_name = "Random Forest Regression"
        
        model.fit(X_train, y_train)
        
        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        # Feature importance (if available)
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
            feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        elif hasattr(model, 'coef_'):
            # For linear models, use absolute coefficients
            feature_importance = dict(zip(feature_cols, [abs(c) for c in model.coef_]))
            # Normalize
            total = sum(feature_importance.values())
            feature_importance = {k: v/total for k, v in feature_importance.items()}
            feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        # Make predictions
        predictions = model.predict(X_test).tolist()
        actuals = y_test.tolist()
        
        return {
            "model_type": model_name,
            "model_key": model_type,
            "train_score": float(train_score),
            "test_score": float(test_score),
            "feature_importance": feature_importance,
            "predictions": predictions[:50],  # Limit to 50
            "actuals": actuals[:50]
        }
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

async def generate_chart_description(chart_data: dict, df: pd.DataFrame) -> str:
    """Generate AI description for a chart"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"chart_desc_{uuid.uuid4()}",
            system_message="You are a data visualization expert. Provide concise 1-2 sentence descriptions of charts explaining what they show and why they're useful."
        ).with_model("openai", "gpt-4o-mini")
        
        chart_type = chart_data.get("type", "unknown")
        title = chart_data.get("title", "Chart")
        
        # Get data context
        context = f"Chart Type: {chart_type}\\nTitle: {title}\\nDataset size: {len(df)} rows, {len(df.columns)} columns"
        
        message = UserMessage(
            text=f"Generate a brief 1-2 sentence description explaining what this chart shows and why it's useful for analysis:\\n{context}"
        )
        
        description = await chat.send_message(message)
        return description
    except Exception as e:
        return f"This {chart_type} visualization helps identify patterns in the data."

def generate_chart_recommendations(df: pd.DataFrame) -> List[dict]:
    """Generate comprehensive data visualizations with detailed insights"""
    charts = []
    skipped_charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # 1. Distributions for all numeric columns
    for col in numeric_cols[:5]:  # Up to 5 numeric distributions
        try:
            clean_data = df[col].dropna()
            if clean_data.empty or len(clean_data) < 2:
                skipped_charts.append(f"Distribution of {col}: Insufficient data (need at least 2 values)")
                continue
            
            # Check if all values are the same
            if clean_data.nunique() == 1:
                skipped_charts.append(f"Distribution of {col}: All values are identical")
                continue
                
            mean_val = clean_data.mean()
            std_val = clean_data.std()
            median_val = clean_data.median()
            
            fig = px.histogram(df, x=col, nbins=min(30, clean_data.nunique()), title=f"Distribution of {col}")
            fig.update_layout(showlegend=False, height=400)
            
            plotly_json = json.loads(fig.to_json())
            if plotly_json.get('data') and len(plotly_json['data']) > 0 and plotly_json['data'][0].get('x'):
                charts.append({
                    "type": "histogram",
                    "title": f"Distribution of {col}",
                    "data": plotly_json,
                    "description": f"Shows frequency distribution of {col}. Mean: {mean_val:.2f}, Median: {median_val:.2f}, Std: {std_val:.2f}. {'Right-skewed' if mean_val > median_val else 'Left-skewed' if mean_val < median_val else 'Symmetric'} distribution pattern."
                })
            else:
                skipped_charts.append(f"Distribution of {col}: Failed to generate valid chart")
        except Exception as e:
            skipped_charts.append(f"Distribution of {col}: {str(e)[:50]}")
    
    # 2. Categorical frequency charts
    for col in categorical_cols[:4]:  # Up to 4 categorical charts
        try:
            value_counts = df[col].value_counts().head(10)
            if value_counts.empty:
                skipped_charts.append(f"Frequency of {col}: No categories found")
                continue
                
            total = len(df)
            top_category = value_counts.index[0]
            top_pct = (value_counts.values[0] / total) * 100
            
            fig = px.bar(x=value_counts.index, y=value_counts.values,
                        title=f"Frequency of {col}",
                        labels={'x': col, 'y': 'Count'})
            fig.update_layout(showlegend=False, height=400)
            
            plotly_json = json.loads(fig.to_json())
            if plotly_json.get('data') and len(plotly_json['data']) > 0:
                charts.append({
                    "type": "bar",
                    "title": f"Frequency of {col}",
                    "data": plotly_json,
                    "description": f"Top 10 categories in {col}. '{top_category}' is most frequent ({value_counts.values[0]} records, {top_pct:.1f}% of data). Shows distribution of {len(value_counts)} unique categories."
                })
            else:
                skipped_charts.append(f"Frequency of {col}: Empty chart data")
        except Exception as e:
            skipped_charts.append(f"Frequency of {col}: {str(e)[:50]}")
    
    # 3. Correlation heatmap
    if len(numeric_cols) >= 2:
        try:
            corr_matrix = df[numeric_cols].corr()
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 10}
            ))
            fig.update_layout(title="Correlation Heatmap", height=500)
            
            # Find strongest correlations
            strong_corrs = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    if abs(corr_matrix.iloc[i, j]) > 0.5:
                        strong_corrs.append(f"{numeric_cols[i]}↔{numeric_cols[j]}")
            
            corr_desc = f"Strong correlations detected: {', '.join(strong_corrs[:3])}" if strong_corrs else "No strong correlations found"
            
            plotly_json = json.loads(fig.to_json())
            if plotly_json.get('data') and len(plotly_json['data']) > 0:
                charts.append({
                    "type": "heatmap",
                    "title": "Correlation Heatmap",
                    "data": plotly_json,
                    "description": f"Shows relationships between {len(numeric_cols)} numeric variables. Red indicates positive correlation, blue negative. {corr_desc}."
                })
            else:
                skipped_charts.append("Correlation Heatmap: Empty chart data")
        except Exception as e:
            skipped_charts.append(f"Correlation Heatmap: {str(e)[:50]}")
    else:
        skipped_charts.append("Correlation Heatmap: Need at least 2 numeric columns")
    
    # 4. Box plots for outlier detection (top 3 numeric columns)
    for col in numeric_cols[:3]:
        try:
            if df[col].dropna().empty:
                skipped_charts.append(f"Box Plot - {col}: No valid data")
                continue
                
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)][col]
            outlier_pct = (len(outliers) / len(df)) * 100
            
            fig = px.box(df, y=col, title=f"Box Plot - {col}")
            fig.update_layout(showlegend=False, height=400)
            
            plotly_json = json.loads(fig.to_json())
            if plotly_json.get('data') and len(plotly_json['data']) > 0:
                charts.append({
                    "type": "box",
                    "title": f"Box Plot - {col}",
                    "data": plotly_json,
                    "description": f"Outlier analysis for {col}. IQR: {iqr:.2f}, {len(outliers)} outliers detected ({outlier_pct:.1f}% of data). Box shows quartiles Q1={q1:.2f}, Q2={df[col].median():.2f}, Q3={q3:.2f}."
                })
            else:
                skipped_charts.append(f"Box Plot - {col}: Empty chart data")
        except Exception as e:
            skipped_charts.append(f"Box Plot - {col}: {str(e)[:50]}")
    
    # 5. Scatter plots for relationships (top 3 pairs)
    if len(numeric_cols) >= 2:
        pairs_added = 0
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                if pairs_added >= 3: break
                try:
                    corr = df[numeric_cols[i]].corr(df[numeric_cols[j]])
                    if abs(corr) > 0.3:  # Only significant correlations
                        fig = px.scatter(df, x=numeric_cols[i], y=numeric_cols[j],
                                       title=f"{numeric_cols[i]} vs {numeric_cols[j]}",
                                       trendline="ols")
                        fig.update_layout(height=400)
                        
                        strength = "Strong" if abs(corr) > 0.7 else "Moderate"
                        direction = "positive" if corr > 0 else "negative"
                        
                        plotly_json = json.loads(fig.to_json())
                        if plotly_json.get('data') and len(plotly_json['data']) > 0:
                            charts.append({
                                "type": "scatter",
                                "title": f"{numeric_cols[i]} vs {numeric_cols[j]}",
                                "data": plotly_json,
                                "description": f"{strength} {direction} correlation (r={corr:.3f}). As {numeric_cols[i]} {'increases' if corr > 0 else 'decreases'}, {numeric_cols[j]} tends to {'increase' if corr > 0 else 'decrease'}. Trendline shows overall pattern."
                            })
                            pairs_added += 1
                        else:
                            skipped_charts.append(f"Scatter {numeric_cols[i]} vs {numeric_cols[j]}: Empty chart data")
                except Exception as e:
                    skipped_charts.append(f"Scatter {numeric_cols[i] if i < len(numeric_cols) else 'N/A'} vs {numeric_cols[j] if j < len(numeric_cols) else 'N/A'}: {str(e)[:50]}")
    else:
        skipped_charts.append("Scatter plots: Need at least 2 numeric columns")
    
    # 6. Pie charts for categorical distributions (top 2)
    for col in categorical_cols[:2]:
        try:
            value_counts = df[col].value_counts().head(8)
            if value_counts.empty:
                skipped_charts.append(f"Pie Chart - {col}: No categories")
                continue
                
            total = value_counts.sum()
            
            fig = go.Figure(data=[go.Pie(
                labels=value_counts.index,
                values=value_counts.values,
                hole=0.3
            )])
            fig.update_layout(title=f"Proportion of {col}", height=400)
            
            top_3 = ', '.join([f"{idx} ({val/total*100:.1f}%)" for idx, val in list(value_counts.items())[:3]])
            
            plotly_json = json.loads(fig.to_json())
            if plotly_json.get('data') and len(plotly_json['data']) > 0:
                charts.append({
                    "type": "pie",
                    "title": f"Proportion of {col}",
                    "data": plotly_json,
                    "description": f"Proportional breakdown of {col} categories. Top 3: {top_3}. Shows relative distribution across {len(value_counts)} categories representing {total} total records."
                })
            else:
                skipped_charts.append(f"Pie Chart - {col}: Empty chart data")
        except Exception as e:
            skipped_charts.append(f"Pie Chart - {col}: {str(e)[:50]}")
    
    # 7. Time series if applicable
    time_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['time', 'date', 'day', 'hour'])]
    if time_cols and numeric_cols:
        try:
            time_col = time_cols[0]
            num_col = numeric_cols[0]
            temp_df = df[[time_col, num_col]].dropna().sort_values(time_col).head(1000)
            
            if not temp_df.empty:
                fig = go.Figure(data=[go.Scatter(
                    x=temp_df[time_col],
                    y=temp_df[num_col],
                    mode='lines+markers',
                    name=num_col
                )])
                fig.update_layout(title=f"Trend of {num_col} Over {time_col}", height=400)
                
                trend_direction = "increasing" if temp_df[num_col].iloc[-1] > temp_df[num_col].iloc[0] else "decreasing"
                
                plotly_json = json.loads(fig.to_json())
                if plotly_json.get('data') and len(plotly_json['data']) > 0:
                    charts.append({
                        "type": "line",
                        "title": f"Trend of {num_col} Over {time_col}",
                        "data": plotly_json,
                        "description": f"Time series showing {num_col} over {time_col}. Overall trend is {trend_direction}. Peak: {temp_df[num_col].max():.2f}, Low: {temp_df[num_col].min():.2f}, displaying patterns and temporal variations."
                    })
                else:
                    skipped_charts.append(f"Time Series: Empty chart data")
            else:
                skipped_charts.append(f"Time Series: No valid time series data")
        except Exception as e:
            skipped_charts.append(f"Time Series: {str(e)[:50]}")
    
    # 8. Grouped bar chart (categorical vs categorical)
    if len(categorical_cols) >= 2:
        try:
            cat1, cat2 = categorical_cols[0], categorical_cols[1]
            # Limit to top categories for readability
            top_cat1 = df[cat1].value_counts().head(5).index
            top_cat2 = df[cat2].value_counts().head(5).index
            filtered_df = df[df[cat1].isin(top_cat1) & df[cat2].isin(top_cat2)]
            
            if not filtered_df.empty:
                crosstab = pd.crosstab(filtered_df[cat1], filtered_df[cat2])
                
                fig = go.Figure()
                for col in crosstab.columns:
                    fig.add_trace(go.Bar(name=str(col), x=crosstab.index, y=crosstab[col]))
                
                fig.update_layout(
                    title=f"{cat1} by {cat2}",
                    barmode='group',
                    height=400,
                    xaxis_title=cat1,
                    yaxis_title="Count"
                )
                
                plotly_json = json.loads(fig.to_json())
                if plotly_json.get('data') and len(plotly_json['data']) > 0:
                    charts.append({
                        "type": "grouped_bar",
                        "title": f"{cat1} by {cat2}",
                        "data": plotly_json,
                        "description": f"Cross-tabulation showing how {cat1} categories are distributed across {cat2} values. Reveals interaction patterns between these two categorical variables."
                    })
                else:
                    skipped_charts.append(f"Grouped Bar: Empty chart data")
            else:
                skipped_charts.append(f"Grouped Bar: No data after filtering")
        except Exception as e:
            skipped_charts.append(f"Grouped Bar: {str(e)[:50]}")
    else:
        skipped_charts.append("Grouped Bar: Need at least 2 categorical columns")
    
    return {"charts": charts, "skipped": skipped_charts}
    """Generate comprehensive data visualizations with detailed insights"""
    charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # 1. Distributions for all numeric columns
    for col in numeric_cols[:5]:  # Up to 5 numeric distributions
        try:
            mean_val = df[col].mean()
            std_val = df[col].std()
            median_val = df[col].median()
            
            fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}")
            fig.update_layout(showlegend=False, height=400)
            
            charts.append({
                "type": "histogram",
                "title": f"Distribution of {col}",
                "data": json.loads(fig.to_json()),
                "description": f"Shows frequency distribution of {col}. Mean: {mean_val:.2f}, Median: {median_val:.2f}, Std: {std_val:.2f}. {'Right-skewed' if mean_val > median_val else 'Left-skewed' if mean_val < median_val else 'Symmetric'} distribution pattern."
            })
        except: pass
    
    # 2. Categorical frequency charts
    for col in categorical_cols[:4]:  # Up to 4 categorical charts
        try:
            value_counts = df[col].value_counts().head(10)
            total = len(df)
            top_category = value_counts.index[0]
            top_pct = (value_counts.values[0] / total) * 100
            
            fig = px.bar(x=value_counts.index, y=value_counts.values,
                        title=f"Frequency of {col}",
                        labels={'x': col, 'y': 'Count'})
            fig.update_layout(showlegend=False, height=400)
            
            charts.append({
                "type": "bar",
                "title": f"Frequency of {col}",
                "data": json.loads(fig.to_json()),
                "description": f"Top 10 categories in {col}. '{top_category}' is most frequent ({value_counts.values[0]} records, {top_pct:.1f}% of data). Shows distribution of {len(value_counts)} unique categories."
            })
        except: pass
    
    # 3. Correlation heatmap
    if len(numeric_cols) >= 2:
        try:
            corr_matrix = df[numeric_cols].corr()
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 10}
            ))
            fig.update_layout(title="Correlation Heatmap", height=500)
            
            # Find strongest correlations
            strong_corrs = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    if abs(corr_matrix.iloc[i, j]) > 0.5:
                        strong_corrs.append(f"{numeric_cols[i]}↔{numeric_cols[j]}")
            
            corr_desc = f"Strong correlations detected: {', '.join(strong_corrs[:3])}" if strong_corrs else "No strong correlations found"
            
            charts.append({
                "type": "heatmap",
                "title": "Correlation Heatmap",
                "data": json.loads(fig.to_json()),
                "description": f"Shows relationships between {len(numeric_cols)} numeric variables. Red indicates positive correlation, blue negative. {corr_desc}."
            })
        except: pass
    
    # 4. Box plots for outlier detection (top 3 numeric columns)
    for col in numeric_cols[:3]:
        try:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)][col]
            outlier_pct = (len(outliers) / len(df)) * 100
            
            fig = px.box(df, y=col, title=f"Box Plot - {col}")
            fig.update_layout(showlegend=False, height=400)
            
            charts.append({
                "type": "box",
                "title": f"Box Plot - {col}",
                "data": json.loads(fig.to_json()),
                "description": f"Outlier analysis for {col}. IQR: {iqr:.2f}, {len(outliers)} outliers detected ({outlier_pct:.1f}% of data). Box shows quartiles Q1={q1:.2f}, Q2={df[col].median():.2f}, Q3={q3:.2f}."
            })
        except: pass
    
    # 5. Scatter plots for relationships (top 3 pairs)
    if len(numeric_cols) >= 2:
        pairs_added = 0
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                if pairs_added >= 3: break
                try:
                    corr = df[numeric_cols[i]].corr(df[numeric_cols[j]])
                    if abs(corr) > 0.3:  # Only significant correlations
                        fig = px.scatter(df, x=numeric_cols[i], y=numeric_cols[j],
                                       title=f"{numeric_cols[i]} vs {numeric_cols[j]}",
                                       trendline="ols")
                        fig.update_layout(height=400)
                        
                        strength = "Strong" if abs(corr) > 0.7 else "Moderate"
                        direction = "positive" if corr > 0 else "negative"
                        
                        charts.append({
                            "type": "scatter",
                            "title": f"{numeric_cols[i]} vs {numeric_cols[j]}",
                            "data": json.loads(fig.to_json()),
                            "description": f"{strength} {direction} correlation (r={corr:.3f}). As {numeric_cols[i]} {'increases' if corr > 0 else 'decreases'}, {numeric_cols[j]} tends to {'increase' if corr > 0 else 'decrease'}. Trendline shows overall pattern."
                        })
                        pairs_added += 1
                except: pass
    
    # 6. Pie charts for categorical distributions (top 2)
    for col in categorical_cols[:2]:
        try:
            value_counts = df[col].value_counts().head(8)
            total = value_counts.sum()
            
            fig = go.Figure(data=[go.Pie(
                labels=value_counts.index,
                values=value_counts.values,
                hole=0.3
            )])
            fig.update_layout(title=f"Proportion of {col}", height=400)
            
            top_3 = ', '.join([f"{idx} ({val/total*100:.1f}%)" for idx, val in list(value_counts.items())[:3]])
            
            charts.append({
                "type": "pie",
                "title": f"Proportion of {col}",
                "data": json.loads(fig.to_json()),
                "description": f"Proportional breakdown of {col} categories. Top 3: {top_3}. Shows relative distribution across {len(value_counts)} categories representing {total} total records."
            })
        except: pass
    
    # 7. Time series if applicable
    time_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['time', 'date', 'day', 'hour'])]
    if time_cols and numeric_cols:
        try:
            time_col = time_cols[0]
            num_col = numeric_cols[0]
            temp_df = df[[time_col, num_col]].dropna().sort_values(time_col).head(1000)
            
            fig = go.Figure(data=[go.Scatter(
                x=temp_df[time_col],
                y=temp_df[num_col],
                mode='lines+markers',
                name=num_col
            )])
            fig.update_layout(title=f"Trend of {num_col} Over {time_col}", height=400)
            
            trend_direction = "increasing" if temp_df[num_col].iloc[-1] > temp_df[num_col].iloc[0] else "decreasing"
            
            charts.append({
                "type": "line",
                "title": f"Trend of {num_col} Over {time_col}",
                "data": json.loads(fig.to_json()),
                "description": f"Time series showing {num_col} over {time_col}. Overall trend is {trend_direction}. Peak: {temp_df[num_col].max():.2f}, Low: {temp_df[num_col].min():.2f}, displaying patterns and temporal variations."
            })
        except: pass
    
    # 8. Grouped bar chart (categorical vs categorical)
    if len(categorical_cols) >= 2:
        try:
            cat1, cat2 = categorical_cols[0], categorical_cols[1]
            # Limit to top categories for readability
            top_cat1 = df[cat1].value_counts().head(5).index
            top_cat2 = df[cat2].value_counts().head(5).index
            filtered_df = df[df[cat1].isin(top_cat1) & df[cat2].isin(top_cat2)]
            
            crosstab = pd.crosstab(filtered_df[cat1], filtered_df[cat2])
            
            fig = go.Figure()
            for col in crosstab.columns:
                fig.add_trace(go.Bar(name=str(col), x=crosstab.index, y=crosstab[col]))
            
            fig.update_layout(
                title=f"{cat1} by {cat2}",
                barmode='group',
                height=400,
                xaxis_title=cat1,
                yaxis_title="Count"
            )
            
            charts.append({
                "type": "grouped_bar",
                "title": f"{cat1} by {cat2}",
                "data": json.loads(fig.to_json()),
                "description": f"Cross-tabulation showing how {cat1} categories are distributed across {cat2} values. Reveals interaction patterns between these two categorical variables."
            })
        except: pass
    
    return charts

# API Routes
@api_router.get("/")
async def root():
    return {"message": "AutoPredict API", "version": "1.0"}

@api_router.post("/datasource/test-connection")
async def test_connection(request: DataSourceTest):
    """Test database connection"""
    try:
        if request.source_type == 'oracle':
            result = test_oracle_connection(request.config)
        elif request.source_type == 'postgresql':
            result = test_postgresql_connection(request.config)
        elif request.source_type == 'mongodb':
            # Test MongoDB connection
            await db.command('ping')
            result = {"success": True, "message": "Connection successful"}
        else:
            result = {"success": False, "message": "Unsupported database type"}
        
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}

@api_router.post("/datasource/list-tables")
async def list_tables(request: DataSourceTest):
    """List available tables/collections"""
    try:
        if request.source_type == 'oracle':
            tables = get_oracle_tables(request.config)
        elif request.source_type == 'postgresql':
            tables = get_postgresql_tables(request.config)
        elif request.source_type == 'mongodb':
            tables = await get_mongodb_collections()
        else:
            raise HTTPException(400, "Unsupported database type")
        
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(500, str(e))

@api_router.post("/datasource/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload and preview data file using GridFS for large files"""
    try:
        import time
        start_time = time.time()
        
        # Read file
        contents = await file.read()
        file_size = len(contents)
        
        # Detect file type and read for metadata
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents), low_memory=False)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(400, "Unsupported file format. Use CSV or Excel")
        
        # Check for duplicate names and generate unique name
        base_name = file.filename.rsplit('.', 1)[0]
        extension = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'csv'
        unique_name = file.filename
        
        existing = await db.datasets.find_one({"name": unique_name}, {"_id": 0})
        counter = 1
        while existing:
            unique_name = f"{base_name}_{counter}.{extension}"
            existing = await db.datasets.find_one({"name": unique_name}, {"_id": 0})
            counter += 1
        
        # Store dataset info
        dataset_id = str(uuid.uuid4())
        
        # For large datasets, only store sample data in preview
        preview_size = min(len(df), 100)
        
        # Sanitize preview data (replace NaN, inf with None)
        import math
        preview_df = df.head(preview_size).replace([np.nan, np.inf, -np.inf], None)
        
        upload_time = time.time() - start_time
        
        dataset_info = {
            "id": dataset_id,
            "name": unique_name,
            "original_name": file.filename,
            "source_type": "file",
            "file_size": file_size,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "data_preview": preview_df.to_dict('records'),
            "upload_time": upload_time,
            "storage_method": "gridfs" if file_size > 5_000_000 else "document",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in MongoDB
        await db.datasets.insert_one(dataset_info)
        
        # Store actual data using GridFS for large files
        if file_size > 5_000_000:  # 5MB threshold
            # Store raw file in GridFS
            file_id = await fs.upload_from_stream(
                f"dataset_{dataset_id}",
                contents,
                metadata={"dataset_id": dataset_id, "filename": unique_name}
            )
            logging.info(f"Stored large file in GridFS with ID: {file_id}")
        else:
            # Store as regular document for smaller files
            data_records = df.to_dict('records')
            await db.dataset_data.insert_one({
                "dataset_id": dataset_id,
                "data": data_records
            })
        
        # Return without MongoDB ObjectId
        return {k: v for k, v in dataset_info.items() if k != '_id'}
    except Exception as e:
        logging.error(f"Upload error: {traceback.format_exc()}")
        raise HTTPException(500, f"File upload failed: {str(e)}")

@api_router.post("/datasource/load-table")
async def load_table(source_type: str = Form(...), 
                    config: str = Form(...),
                    table_name: str = Form(...)):
    """Load data from database table"""
    try:
        config_dict = json.loads(config)
        
        if source_type == 'mongodb':
            # Load from MongoDB
            collection = db[table_name]
            data = await collection.find({}, {"_id": 0}).to_list(1000)
            df = pd.DataFrame(data)
        else:
            df = load_table_data(source_type, config_dict, table_name)
        
        # Store dataset
        dataset_id = str(uuid.uuid4())
        dataset_info = {
            "id": dataset_id,
            "name": table_name,
            "source_type": source_type,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "data_preview": df.head(10).to_dict('records'),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.datasets.insert_one(dataset_info)
        
        # Store data
        data_records = df.to_dict('records')
        await db.dataset_data.insert_one({
            "dataset_id": dataset_id,
            "data": data_records
        })
        
        return dataset_info
    except Exception as e:
        raise HTTPException(500, f"Table load failed: {str(e)}")


def train_ml_models(df, target_col, feature_cols):
    """Train multiple ML models and return results"""
    models_results = []
    
    try:
        # Prepare data
        X = df[feature_cols].fillna(df[feature_cols].median())
        y = df[target_col].fillna(df[target_col].median())
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Define models to train
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10),
            "Decision Tree": DecisionTreeRegressor(random_state=42, max_depth=10),
            "XGBoost": xgb.XGBRegressor(n_estimators=50, random_state=42, max_depth=5, verbosity=0)
        }
        
        for model_name, model in models.items():
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                # Feature importance (if available)
                feature_importance = {}
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    feature_importance = {feature_cols[i]: float(importances[i]) for i in range(len(feature_cols))}
                    feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
                
                # Calculate confidence
                confidence = "High" if r2 > 0.7 else "Medium" if r2 > 0.5 else "Low"
                
                models_results.append({
                    "model_name": model_name,
                    "target_column": target_col,
                    "r2_score": float(r2),
                    "rmse": float(rmse),
                    "mse": float(mse),
                    "confidence": confidence,
                    "feature_importance": feature_importance,
                    "predictions_sample": {
                        "actual": y_test.head(10).tolist(),
                        "predicted": y_pred[:10].tolist()
                    }
                })
            except Exception as e:
                logging.error(f"Error training {model_name}: {str(e)}")
                continue
        
        # Train LSTM model (Neural Network)
        try:
            from tensorflow import keras
            from tensorflow.keras import layers
            import warnings
            warnings.filterwarnings('ignore')
            
            # Prepare data for LSTM
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Reshape for LSTM (samples, timesteps, features)
            X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
            X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
            
            # Build LSTM model
            model = keras.Sequential([
                layers.LSTM(50, activation='relu', input_shape=(1, X_train_scaled.shape[1])),
                layers.Dense(25, activation='relu'),
                layers.Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            
            # Train with reduced epochs for speed
            model.fit(X_train_lstm, y_train, epochs=20, batch_size=32, verbose=0, validation_split=0.1)
            
            # Predictions
            y_pred_lstm = model.predict(X_test_lstm, verbose=0).flatten()
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred_lstm)
            r2 = r2_score(y_test, y_pred_lstm)
            rmse = np.sqrt(mse)
            confidence = "High" if r2 > 0.7 else "Medium" if r2 > 0.5 else "Low"
            
            models_results.append({
                "model_name": "LSTM Neural Network",
                "target_column": target_col,
                "r2_score": float(r2),
                "rmse": float(rmse),
                "mse": float(mse),
                "confidence": confidence,
                "feature_importance": {},
                "predictions_sample": {
                    "actual": y_test.head(10).tolist(),
                    "predicted": y_pred_lstm[:10].tolist()
                }
            })
        except Exception as e:
            logging.error(f"Error training LSTM: {str(e)}")
    except Exception as e:
        logging.error(f"ML training error: {str(e)}")
    
    return models_results
            
            # Calculate metrics


def generate_auto_charts(df, max_charts=15):
    """Generate up to 15 intelligent charts based on data analysis"""
    import plotly.graph_objects as go
    import plotly.express as px
    
    charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # 1-3: Distribution charts for top 3 numeric columns
    for col in numeric_cols[:3]:
        try:
            fig = go.Figure(data=[go.Histogram(x=df[col].dropna(), nbinsx=30, name=col)])
            fig.update_layout(title=f"Distribution of {col}", xaxis_title=col, yaxis_title="Frequency", width=700, height=400)
            charts.append({
                "type": "histogram",
                "title": f"Distribution of {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Shows frequency distribution of {col}. Mean: {df[col].mean():.2f}, Std: {df[col].std():.2f}"
            })
        except: pass
    
    # 4-6: Box plots for numeric columns (detect outliers)
    for col in numeric_cols[:3]:
        try:
            fig = go.Figure(data=[go.Box(y=df[col].dropna(), name=col)])
            fig.update_layout(title=f"Box Plot: {col}", yaxis_title=col, width=700, height=400)
            charts.append({
                "type": "box",
                "title": f"Box Plot: {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Identifies outliers and spread in {col}. Median: {df[col].median():.2f}"
            })
        except: pass
    
    # 7-9: Categorical distribution (top 3 categorical columns)
    for col in categorical_cols[:3]:
        try:
            value_counts = df[col].value_counts().head(10)
            fig = go.Figure(data=[go.Bar(x=value_counts.index, y=value_counts.values)])
            fig.update_layout(title=f"Top Categories in {col}", xaxis_title=col, yaxis_title="Count", width=700, height=400)
            charts.append({
                "type": "bar",
                "title": f"Top Categories in {col}",
                "plotly_data": json.loads(fig.to_json()),
                "description": f"Top {len(value_counts)} categories in {col}. Most common: {value_counts.index[0]} ({value_counts.values[0]} occurrences)"
            })
        except: pass
    
    # 10-12: Time series trends (if datetime columns exist)
    if datetime_cols:
        for dt_col in datetime_cols[:1]:
            for num_col in numeric_cols[:2]:
                try:
                    temp_df = df[[dt_col, num_col]].dropna().sort_values(dt_col)
                    fig = go.Figure(data=[go.Scatter(x=temp_df[dt_col], y=temp_df[num_col], mode='lines+markers', name=num_col)])
                    fig.update_layout(title=f"{num_col} Over Time", xaxis_title=dt_col, yaxis_title=num_col, width=700, height=400)
                    charts.append({
                        "type": "timeseries",
                        "title": f"{num_col} Over Time",
                        "plotly_data": json.loads(fig.to_json()),
                        "description": f"Time series showing {num_col} trends. Peak: {temp_df[num_col].max():.2f}, Low: {temp_df[num_col].min():.2f}"
                    })
                except: pass
    
    # 13-15: Scatter plots for correlation (top 3 pairs)
    if len(numeric_cols) >= 2:
        pairs_added = 0
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                if pairs_added >= 3: break
                try:
                    corr = df[numeric_cols[i]].corr(df[numeric_cols[j]])
                    if abs(corr) > 0.3:  # Only significant correlations
                        fig = px.scatter(df, x=numeric_cols[i], y=numeric_cols[j], trendline="ols")
                        fig.update_layout(title=f"{numeric_cols[i]} vs {numeric_cols[j]}", width=700, height=400)
                        charts.append({
                            "type": "scatter",
                            "title": f"{numeric_cols[i]} vs {numeric_cols[j]}",
                            "plotly_data": json.loads(fig.to_json()),
                            "description": f"Correlation: {corr:.2f}. {'Strong' if abs(corr) > 0.7 else 'Moderate'} {'positive' if corr > 0 else 'negative'} relationship."
                        })
                        pairs_added += 1
                except: pass
    
    return charts[:max_charts]


@api_router.post("/analysis/holistic")
async def holistic_analysis(request: HolisticRequest):
    """Run comprehensive holistic analysis on entire dataset"""
    try:
        # Retrieve dataset
        dataset = await db.datasets.find_one({"id": request.dataset_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Update training counter
        training_count = dataset.get("training_count", 0) + 1
        await db.datasets.update_one(
            {"id": request.dataset_id},
            {
                "$set": {
                    "training_count": training_count,
                    "last_trained_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Load data using helper function
        df = await get_dataset_dataframe(request.dataset_id)
        
        # Initialize results
        results = {
            "volume_analysis": {"by_dimensions": []},
            "trend_analysis": {"trends": []},
            "correlations": [],
            "predictions": [],
            "ml_models": [],
            "ai_summary": ""
        }
        
        # Identify key dimensions (categorical columns that might represent groups)
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Try to identify time columns
        time_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['time', 'date', 'day', 'hour', 'timestamp'])]
        
        # Volume Analysis by Dimensions
        for cat_col in categorical_cols[:3]:  # Analyze top 3 categorical columns
            try:
                value_counts = df[cat_col].value_counts().head(10)
                insights = f"Top categories in {cat_col}: {', '.join([f'{k} ({v} records)' for k, v in value_counts.head(3).items()])}"
                
                results["volume_analysis"]["by_dimensions"].append({
                    "dimension": f"Volume by {cat_col}",
                    "insights": insights,
                    "data": value_counts.to_dict()
                })
            except Exception as e:
                logging.error(f"Volume analysis error for {cat_col}: {str(e)}")
        
        # Trend Analysis
        if len(numeric_cols) > 0:
            for num_col in numeric_cols[:3]:
                try:
                    trend = "increasing" if df[num_col].corr(pd.Series(range(len(df)))) > 0 else "decreasing"
                    mean_val = df[num_col].mean()
                    std_val = df[num_col].std()
                    
                    results["trend_analysis"]["trends"].append({
                        "category": num_col,
                        "insight": f"Average: {mean_val:.2f}, Std Dev: {std_val:.2f}",
                        "direction": trend,
                        "mean": float(mean_val),
                        "std": float(std_val)
                    })
                except Exception as e:
                    logging.error(f"Trend analysis error for {num_col}: {str(e)}")
        
        # Correlation Analysis
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            for i in range(len(numeric_cols)):
                for j in range(i+1, min(i+4, len(numeric_cols))):  # Top correlations
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.3:  # Only significant correlations
                        strength = "Strong" if abs(corr_val) > 0.7 else "Moderate" if abs(corr_val) > 0.5 else "Weak"
                        interpretation = f"{'Positive' if corr_val > 0 else 'Negative'} relationship"
                        
                        results["correlations"].append({
                            "feature1": numeric_cols[i],
                            "feature2": numeric_cols[j],
                            "value": float(corr_val),
                            "strength": strength,
                            "interpretation": interpretation
                        })
        
        # ML Models - Train multiple models on key numeric columns
        for target_col in numeric_cols[:2]:  # Train on top 2 numeric columns
            try:
                feature_cols = [col for col in numeric_cols if col != target_col]
                if not feature_cols or len(feature_cols) < 1:
                    continue
                    
                models_results = train_ml_models(df, target_col, feature_cols)
                results["ml_models"].extend(models_results)
            except Exception as e:
                logging.error(f"ML training error for {target_col}: {str(e)}")
        
        # Predictive Insights - Summary from best model
        best_score = 0
        if results["ml_models"]:
            best_model = max(results["ml_models"], key=lambda x: x["r2_score"])
            best_score = best_model["r2_score"]
            results["predictions"].append({
                "title": f"Best Model Prediction for {best_model['target_column']}",
                "description": f"{best_model['model_name']} achieved R² score of {best_model['r2_score']:.3f}",
                "accuracy": float(best_model["r2_score"]),
                "confidence": best_model["confidence"],
                "risk_level": "Low" if best_model["r2_score"] > 0.7 else "Medium" if best_model["r2_score"] > 0.5 else "High",
                "model_used": best_model["model_name"]
            })
            
            # Update dataset with best model score
            await db.datasets.update_one(
                {"id": request.dataset_id},
                {
                    "$set": {
                        "best_model_score": float(best_score),
                        "best_model_name": best_model["model_name"]
                    }
                }
            )
            
            # Store training history for this session
            training_history_entry = {
                "dataset_id": request.dataset_id,
                "dataset_name": dataset.get("name", "Unknown"),
                "training_number": training_count,
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "models": [
                    {
                        "model_name": model.get("model_name"),
                        "target_column": model.get("target_column"),
                        "r2_score": float(model.get("r2_score", 0)),
                        "rmse": float(model.get("rmse", 0)) if model.get("rmse") else None,
                        "confidence": model.get("confidence", "Unknown")
                    }
                    for model in results["ml_models"]
                ],
                "best_model": best_model["model_name"],
                "best_score": float(best_score)
            }
            
            # Insert training history
            await db.training_history.insert_one(training_history_entry)
        
        # Generate AI Summary
        try:
            # Generate auto charts
            auto_charts = generate_auto_charts(df, max_charts=15)
            results["auto_charts"] = auto_charts
            
            summary_context = f"""Dataset Analysis Summary:
- Total Records: {len(df)}
- Columns: {len(df.columns)}
- Key Dimensions: {', '.join(categorical_cols[:3]) if categorical_cols else 'None identified'}
- Numeric Features: {', '.join(numeric_cols[:5]) if numeric_cols else 'None'}
- Correlations Found: {len(results['correlations'])}
- Predictions Generated: {len(results['predictions'])}

Key Findings:
{chr(10).join([f"- {item['insights']}" for item in results['volume_analysis']['by_dimensions'][:3]])}
"""
            
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"holistic_{request.dataset_id}",
                system_message="You are a data analyst. Provide concise, actionable 3-4 sentence summary of key findings."
            ).with_model("openai", "gpt-4o-mini")
            
            message = UserMessage(text=f"Provide a brief executive summary of this dataset analysis:\\n{summary_context}")
            ai_summary = await chat.send_message(message)
            results["ai_summary"] = ai_summary
        except Exception as e:
            results["ai_summary"] = "AI summary generation failed. Please review the detailed analysis above."
            logging.error(f"AI summary error: {str(e)}")
        
        # Add training metadata
        results["training_metadata"] = {
            "training_count": training_count,
            "last_trained_at": datetime.now(timezone.utc).isoformat(),
            "dataset_size": len(df)
        }
        
        return results
        
    except Exception as e:
        logging.error(f"Holistic analysis error: {traceback.format_exc()}")
        raise HTTPException(500, f"Holistic analysis failed: {str(e)}")

@api_router.post("/analysis/run")
async def run_analysis(request: AnalysisRequest):
    """Run analysis on dataset"""
    try:
        # Retrieve dataset
        dataset = await db.datasets.find_one({"id": request.dataset_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Load data using helper function
        df = await get_dataset_dataframe(request.dataset_id)
        
        result = {}
        
        if request.analysis_type == 'profile':
            result = profile_data(df)
        
        elif request.analysis_type == 'clean':
            cleaned_df, report = clean_data(df)
            # Don't store cleaned data (can be too large), just mark as cleaned
            await db.datasets.update_one(
                {"id": request.dataset_id},
                {"$set": {"cleaned": True, "last_cleaned": datetime.now(timezone.utc).isoformat()}}
            )
            result = {
                "cleaning_report": report,
                "new_row_count": len(cleaned_df),
                "cleaned_data_available": True
            }
        
        elif request.analysis_type == 'insights':
            profile = profile_data(df)
            insights = await generate_ai_insights(df, profile)
            result = {"insights": insights}
        
        elif request.analysis_type == 'predict':
            target_col = request.options.get('target_column')
            model_type = request.options.get('model_type', 'random_forest')
            if not target_col:
                raise HTTPException(400, "target_column required for prediction")
            result = predict_with_ml(df, target_col, model_type)
        
        elif request.analysis_type == 'visualize':
            result = generate_chart_recommendations(df)
            # result is now {"charts": [...], "skipped": [...]}
        
        else:
            raise HTTPException(400, f"Unknown analysis type: {request.analysis_type}")
        
        return result
    except Exception as e:
        logging.error(f"Analysis error: {traceback.format_exc()}")
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@api_router.get("/datasets")
async def list_datasets():
    """List all datasets"""
    import math
    datasets = await db.datasets.find({}, {"_id": 0}).to_list(100)
    
    # Clean up any invalid values
    def sanitize_value(value):
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None
            return value
        elif isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(v) for v in value]
        return value
    
    sanitized_datasets = [sanitize_value(dataset) for dataset in datasets]
    return {"datasets": sanitized_datasets}

@api_router.get("/datasets/{dataset_id}/download")
async def download_dataset(dataset_id: str):
    """Download cleaned dataset as CSV"""
    try:
        # Load original data and clean it on-the-fly
        df = await get_dataset_dataframe(dataset_id)
        
        # Clean the data
        cleaned_df, _ = clean_data(df)
        
        # Convert to CSV
        csv_buffer = BytesIO()
        cleaned_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Get dataset name
        dataset = await db.datasets.find_one({"id": dataset_id}, {"_id": 0})
        filename = f"{dataset['name'].rsplit('.', 1)[0]}_cleaned.csv" if dataset else "cleaned_data.csv"
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            csv_buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(500, f"Download failed: {str(e)}")

@api_router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset"""
    await db.datasets.delete_one({"id": dataset_id})
    await db.dataset_data.delete_one({"dataset_id": dataset_id})
    return {"message": "Dataset deleted"}

class ChatRequest(BaseModel):
    dataset_id: str
    message: str
    conversation_history: List[Dict[str, str]] = []

class SaveStateRequest(BaseModel):
    dataset_id: str
    state_name: str
    analysis_data: Dict[str, Any]
    chat_history: List[Dict[str, str]] = []
    
class LoadStateRequest(BaseModel):
    state_id: str

@api_router.post("/analysis/chat-action")
async def analysis_chat_action(request: ChatRequest):
    """Chat with AI that can execute actions on the analysis"""
    try:
        # Retrieve dataset
        dataset = await db.datasets.find_one({"id": request.dataset_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Load data using helper function
        df = await get_dataset_dataframe(request.dataset_id)
        
        user_message = request.message.lower()
        
        # Get current analysis if available
        current_analysis = request.conversation_history
        
        # Detect removal request
        if 'remove' in user_message or 'delete' in user_message:
            # Extract what to remove
            if 'correlation' in user_message:
                return {
                    "action": "remove_section",
                    "message": "I'll remove the correlation analysis section.",
                    "section_to_remove": "correlations"
                }
            elif 'pie chart' in user_message or 'pie' in user_message:
                return {
                    "action": "remove_section",
                    "message": "I'll remove the pie chart.",
                    "section_to_remove": "custom_chart"
                }
            elif 'bar chart' in user_message or 'bar' in user_message:
                return {
                    "action": "remove_section",
                    "message": "I'll remove the bar chart.",
                    "section_to_remove": "custom_chart"
                }
            elif 'line chart' in user_message or 'line' in user_message:
                return {
                    "action": "remove_section",
                    "message": "I'll remove the line chart.",
                    "section_to_remove": "custom_chart"
                }
            elif 'chart' in user_message:
                return {
                    "action": "remove_section",
                    "message": "I'll remove the last custom chart.",
                    "section_to_remove": "custom_chart"
                }
            else:
                return {"response": "Please specify what you'd like to remove (e.g., 'remove correlation' or 'remove pie chart')"}
        
        # Detect correlation request
        if 'correlation' in user_message or 'correlate' in user_message:
            # Calculate actual correlations
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()
                
                # Create correlation pairs
                correlations = []
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        corr_val = corr_matrix.iloc[i, j]
                        if not np.isnan(corr_val) and abs(corr_val) > 0.1:  # Only significant
                            strength = "Strong" if abs(corr_val) > 0.7 else "Moderate" if abs(corr_val) > 0.5 else "Weak"
                            interpretation = f"{'Positive' if corr_val > 0 else 'Negative'} relationship"
                            
                            correlations.append({
                                "feature1": numeric_cols[i],
                                "feature2": numeric_cols[j],
                                "value": float(corr_val),
                                "strength": strength,
                                "interpretation": interpretation
                            })
                
                # Sort by absolute value
                correlations.sort(key=lambda x: abs(x['value']), reverse=True)
                
                # Create heatmap data for Plotly
                import plotly.graph_objects as go
                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=numeric_cols,
                    y=numeric_cols,
                    colorscale='RdBu',
                    zmid=0,
                    text=corr_matrix.values.round(2),
                    texttemplate='%{text}',
                    textfont={"size": 10},
                    colorbar=dict(title="Correlation")
                ))
                fig.update_layout(
                    title="Correlation Matrix Heatmap",
                    xaxis_title="Variables",
                    yaxis_title="Variables",
                    width=800,
                    height=600
                )
                
                return {
                    "action": "add_chart",
                    "message": f"I've calculated correlations for {len(numeric_cols)} numeric variables. Found {len(correlations)} significant correlations.",
                    "chart_data": {
                        "type": "correlation",
                        "correlations": correlations[:20],  # Top 20
                        "heatmap": json.loads(fig.to_json())
                    }
                }
            else:
                return {"response": "Not enough numeric columns for correlation analysis. Need at least 2 numeric columns."}
        
        # Detect pie chart request
        if 'pie' in user_message and 'chart' in user_message:
            # Find categorical columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if categorical_cols:
                import plotly.graph_objects as go
                
                # Use first categorical column or the one mentioned
                target_col = categorical_cols[0]
                for col in categorical_cols:
                    if col.lower() in user_message:
                        target_col = col
                        break
                
                # Get value counts
                value_counts = df[target_col].value_counts().head(10)  # Top 10
                
                fig = go.Figure(data=[go.Pie(
                    labels=value_counts.index.tolist(),
                    values=value_counts.values.tolist(),
                    hole=0.3
                )])
                fig.update_layout(
                    title=f"Distribution of {target_col}",
                    width=600,
                    height=500
                )
                
                return {
                    "action": "add_chart",
                    "message": f"I've created a pie chart showing the distribution of {target_col}.",
                    "chart_data": {
                        "type": "pie",
                        "title": f"Distribution of {target_col}",
                        "column": target_col,
                        "plotly_data": json.loads(fig.to_json()),
                        "description": f"This pie chart shows the distribution of {target_col}. The top {len(value_counts)} categories are displayed."
                    }
                }
            else:
                return {"response": "No categorical columns found for pie chart. Need at least one text/category column."}
        
        # Detect bar chart request
        if 'bar' in user_message and 'chart' in user_message:
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if categorical_cols and numeric_cols:
                import plotly.graph_objects as go
                
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                
                # Check if specific columns mentioned
                for col in categorical_cols:
                    if col.lower() in user_message:
                        cat_col = col
                        break
                for col in numeric_cols:
                    if col.lower() in user_message:
                        num_col = col
                        break
                
                grouped = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False).head(10)
                
                fig = go.Figure(data=[go.Bar(
                    x=grouped.index.tolist(),
                    y=grouped.values.tolist(),
                    marker_color='rgb(99, 110, 250)'
                )])
                fig.update_layout(
                    title=f"{num_col} by {cat_col}",
                    xaxis_title=cat_col,
                    yaxis_title=num_col,
                    width=800,
                    height=500
                )
                
                return {
                    "action": "add_chart",
                    "message": f"I've created a bar chart showing {num_col} by {cat_col}.",
                    "chart_data": {
                        "type": "bar",
                        "title": f"{num_col} by {cat_col}",
                        "x_column": cat_col,
                        "y_column": num_col,
                        "plotly_data": json.loads(fig.to_json()),
                        "description": f"This bar chart displays {num_col} grouped by {cat_col}. Shows the top {len(grouped)} categories."
                    }
                }
            else:
                return {"response": "Need both categorical and numeric columns for bar chart."}
        
        # Detect line chart / trend request
        if ('line' in user_message or 'trend' in user_message) and 'chart' in user_message:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 1:
                import plotly.graph_objects as go
                
                # Use first numeric column or mentioned one
                target_col = numeric_cols[0]
                for col in numeric_cols:
                    if col.lower() in user_message:
                        target_col = col
                        break
                
                fig = go.Figure(data=[go.Scatter(
                    y=df[target_col].values.tolist(),
                    mode='lines+markers',
                    name=target_col,
                    line=dict(color='rgb(99, 110, 250)', width=2),
                    marker=dict(size=6)
                )])
                fig.update_layout(
                    title=f"Trend of {target_col}",
                    xaxis_title="Index",
                    yaxis_title=target_col,
                    width=800,
                    height=500
                )
                
                return {
                    "action": "add_chart",
                    "message": f"I've created a line chart showing the trend of {target_col}.",
                    "chart_data": {
                        "type": "line",
                        "title": f"Trend of {target_col}",
                        "column": target_col,
                        "plotly_data": json.loads(fig.to_json()),
                        "description": f"This line chart shows the trend of {target_col} over the dataset records."
                    }
                }
            else:
                return {"response": "Need at least one numeric column for line chart."}
        
        # Detect scatter plot request
        if 'scatter' in user_message and 'chart' in user_message or 'scatter plot' in user_message:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 2:
                import plotly.graph_objects as go
                
                # Try to find mentioned columns
                x_col = None
                y_col = None
                
                # Search for mentioned column names
                for col in numeric_cols:
                    if col.lower() in user_message:
                        if x_col is None:
                            x_col = col
                        elif y_col is None:
                            y_col = col
                            break
                
                # If not enough columns mentioned, use first two
                if x_col is None or y_col is None:
                    x_col = numeric_cols[0] if x_col is None else x_col
                    y_col = numeric_cols[1] if y_col is None else y_col
                
                fig = go.Figure(data=[go.Scatter(
                    x=df[x_col].values.tolist(),
                    y=df[y_col].values.tolist(),
                    mode='markers',
                    marker=dict(
                        size=8,
                        color='rgb(99, 110, 250)',
                        opacity=0.6
                    ),
                    name=f'{x_col} vs {y_col}'
                )])
                fig.update_layout(
                    title=f"Scatter Plot: {x_col} vs {y_col}",
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    width=800,
                    height=500
                )
                
                # Calculate correlation
                corr = df[x_col].corr(df[y_col])
                corr_text = f"Correlation: {corr:.3f}"
                
                return {
                    "action": "add_chart",
                    "message": f"I've created a scatter plot showing {x_col} vs {y_col}. {corr_text}",
                    "chart_data": {
                        "type": "scatter",
                        "title": f"Scatter Plot: {x_col} vs {y_col}",
                        "x_column": x_col,
                        "y_column": y_col,
                        "plotly_data": json.loads(fig.to_json()),
                        "description": f"This scatter plot shows the relationship between {x_col} and {y_col}. {corr_text}"
                    }
                }
            else:
                return {"response": "Need at least two numeric columns for scatter plot."}

        # Detect histogram request
        if 'histogram' in user_message and ('chart' in user_message or 'distribution' in user_message):
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 1:
                import plotly.graph_objects as go
                
                # Use first numeric column or mentioned one
                target_col = numeric_cols[0]
                for col in numeric_cols:
                    if col.lower() in user_message:
                        target_col = col
                        break
                
                fig = go.Figure(data=[go.Histogram(
                    x=df[target_col].dropna().values,
                    nbinsx=30,
                    name=target_col,
                    marker_color='rgb(99, 110, 250)'
                )])
                fig.update_layout(
                    title=f"Distribution of {target_col}",
                    xaxis_title=target_col,
                    yaxis_title="Frequency",
                    width=800,
                    height=500,
                    showlegend=False
                )
                
                return {
                    "action": "add_chart",
                    "message": f"I've created a histogram showing the distribution of {target_col}.",
                    "chart_data": {
                        "type": "histogram",
                        "title": f"Distribution of {target_col}",
                        "column": target_col,
                        "plotly_data": json.loads(fig.to_json()),
                        "description": f"This histogram shows the frequency distribution of {target_col} values across {len(df[target_col].dropna())} records."
                    }
                }
            else:
                return {"response": "Need at least one numeric column for histogram."}
        

        # Default: use AI for general responses
        context = f"""Dataset: {dataset['name']}
Rows: {dataset['row_count']}, Columns: {dataset['column_count']}
Available columns: {', '.join(dataset['columns'])}

User request: {request.message}

Provide a helpful response about their data."""
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"chat_{request.dataset_id}",
            system_message="You are a helpful data analysis assistant."
        ).with_model("openai", "gpt-4o-mini")
        
        message = UserMessage(text=context)
        response = await chat.send_message(message)
        
        return {"response": response}
    except Exception as e:
        logging.error(f"Chat action error: {traceback.format_exc()}")
        raise HTTPException(500, f"Chat failed: {str(e)}")

@api_router.post("/analysis/chat")
async def analysis_chat(request: ChatRequest):
    """Chat with AI about the dataset for custom analysis"""
    try:
        # Retrieve dataset
        dataset = await db.datasets.find_one({"id": request.dataset_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Load data using helper function
        df = await get_dataset_dataframe(request.dataset_id)
        
        # Build context
        context = f"""Dataset Information:
- Name: {dataset['name']}
- Rows: {dataset['row_count']}
- Columns: {dataset['column_count']}
- Column names: {', '.join(dataset['columns'])}

Available analysis options:
1. Run specific ML models (random_forest, gradient_boosting, linear_regression, decision_tree)
2. Generate specific visualizations
3. Analyze specific columns or relationships
4. Custom statistical analysis

User question: {request.message}
"""
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"chat_{request.dataset_id}",
            system_message="You are a data analysis assistant. Help users analyze their data by suggesting specific analyses, explaining results, and guiding them through the process. Keep responses concise and actionable."
        ).with_model("openai", "gpt-4o-mini")
        
        message = UserMessage(text=context)
        response = await chat.send_message(message)
        
        return {"response": response}
    except Exception as e:
        logging.error(f"Chat action error: {traceback.format_exc()}")
        raise HTTPException(500, f"Chat failed: {str(e)}")

# Save/Load Analysis States
@api_router.post("/analysis/save-state")
async def save_analysis_state(request: SaveStateRequest):
    """Save analysis state with custom name"""
    try:
        state_id = str(uuid.uuid4())
        state_doc = {
            "id": state_id,
            "dataset_id": request.dataset_id,
            "state_name": request.state_name,
            "analysis_data": request.analysis_data,
            "chat_history": request.chat_history,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.analysis_states.insert_one(state_doc)
        return {"state_id": state_id, "message": f"Analysis state '{request.state_name}' saved successfully"}
    except Exception as e:
        logging.error(f"Save state error: {traceback.format_exc()}")
        raise HTTPException(500, f"Failed to save state: {str(e)}")

@api_router.get("/analysis/load-state/{state_id}")
async def load_analysis_state(state_id: str):
    """Load a saved analysis state"""
    try:
        state = await db.analysis_states.find_one({"id": state_id}, {"_id": 0})
        if not state:
            raise HTTPException(404, "Analysis state not found")
        return state
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Load state error: {traceback.format_exc()}")
        raise HTTPException(500, f"Failed to load state: {str(e)}")

@api_router.get("/analysis/saved-states/{dataset_id}")
async def get_saved_states(dataset_id: str):
    """Get all saved states for a dataset"""
    try:
        states = await db.analysis_states.find(
            {"dataset_id": dataset_id}, 
            {"_id": 0, "id": 1, "state_name": 1, "created_at": 1, "updated_at": 1}
        ).to_list(length=None)
        return {"states": states}
    except Exception as e:
        logging.error(f"Get saved states error: {traceback.format_exc()}")
        raise HTTPException(500, f"Failed to get saved states: {str(e)}")

@api_router.delete("/analysis/delete-state/{state_id}")
async def delete_analysis_state(state_id: str):
    """Delete a saved analysis state"""
    try:
        result = await db.analysis_states.delete_one({"id": state_id})
        if result.deleted_count == 0:
            raise HTTPException(404, "Analysis state not found")
        return {"message": "Analysis state deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Delete state error: {traceback.format_exc()}")
        raise HTTPException(500, f"Failed to delete state: {str(e)}")

@api_router.get("/training-metadata")
async def get_training_metadata():
    """Get comprehensive training metadata for all datasets"""
    try:
        # Get all datasets
        datasets_cursor = db.datasets.find({}, {"_id": 0})
        datasets = await datasets_cursor.to_list(length=None)
        
        # Get all saved states
        states_cursor = db.saved_states.find({}, {"_id": 0})
        saved_states = await states_cursor.to_list(length=None)
        
        # Get all training history
        history_cursor = db.training_history.find({}, {"_id": 0}).sort("trained_at", -1)
        training_history = await history_cursor.to_list(length=None)
        
        # Organize data by dataset
        metadata = []
        
        for dataset in datasets:
            dataset_id = dataset["id"]
            
            # Get workspaces for this dataset
            dataset_states = [s for s in saved_states if s.get("dataset_id") == dataset_id]
            
            # Get training history for this dataset
            dataset_history = [h for h in training_history if h.get("dataset_id") == dataset_id]
            
            # Calculate improvements
            initial_score = None
            current_score = None
            improvement = None
            
            if len(dataset_history) > 0:
                # Initial score (first training)
                initial_score = dataset_history[-1].get("best_score", 0) if len(dataset_history) > 0 else None
                # Current score (latest training)
                current_score = dataset_history[0].get("best_score", 0) if len(dataset_history) > 0 else None
                
                if initial_score is not None and current_score is not None and initial_score > 0:
                    improvement = ((current_score - initial_score) / initial_score) * 100
            
            # Model-wise scores (latest training)
            model_scores = {}
            if len(dataset_history) > 0:
                latest_training = dataset_history[0]
                for model in latest_training.get("models", []):
                    model_scores[model["model_name"]] = {
                        "current_score": model["r2_score"],
                        "confidence": model.get("confidence", "Unknown")
                    }
                
                # Get initial scores for each model
                if len(dataset_history) > 1:
                    initial_training = dataset_history[-1]
                    for model in initial_training.get("models", []):
                        model_name = model["model_name"]
                        if model_name in model_scores:
                            model_scores[model_name]["initial_score"] = model["r2_score"]
                            initial = model["r2_score"]
                            current = model_scores[model_name]["current_score"]
                            if initial > 0:
                                model_scores[model_name]["improvement_pct"] = ((current - initial) / initial) * 100
            
            metadata.append({
                "dataset_id": dataset_id,
                "dataset_name": dataset.get("name", "Unknown"),
                "training_count": dataset.get("training_count", 0),
                "last_trained_at": dataset.get("last_trained_at"),
                "initial_score": initial_score,
                "current_score": current_score,
                "improvement_percentage": improvement,
                "best_model_name": dataset.get("best_model_name"),
                "workspaces": [
                    {
                        "workspace_name": state.get("state_name"),
                        "saved_at": state.get("saved_at"),
                        "workspace_id": state.get("state_id")
                    }
                    for state in dataset_states
                ],
                "model_scores": model_scores,
                "training_history": [
                    {
                        "training_number": h.get("training_number"),
                        "trained_at": h.get("trained_at"),
                        "best_score": h.get("best_score"),
                        "best_model": h.get("best_model"),
                        "models": h.get("models", [])
                    }
                    for h in dataset_history
                ]
            })
        
        return {"metadata": metadata}
    
    except Exception as e:
        logging.error(f"Training metadata error: {traceback.format_exc()}")
        raise HTTPException(500, f"Failed to fetch training metadata: {str(e)}")

app.include_router(api_router)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()