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
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from statsmodels.tsa.arima.model import ARIMA
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

# LLM Setup
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI()
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
    analysis_type: str  # 'profile', 'clean', 'predict', 'insights'
    options: Dict[str, Any] = {}

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
    """Recommend charts based on data types"""
    charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Correlation heatmap
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        fig = px.imshow(corr_matrix, 
                       text_auto=True,
                       title="Correlation Heatmap",
                       color_continuous_scale='RdBu')
        charts.append({
            "type": "heatmap",
            "title": "Correlation Heatmap",
            "data": json.loads(fig.to_json()),
            "description": f"Shows correlations between {len(numeric_cols)} numeric variables. Strong positive (red) or negative (blue) correlations indicate related features."
        })
    
    # Distribution plots for numeric columns
    for col in numeric_cols[:3]:  # Limit to 3
        fig = px.histogram(df, x=col, title=f"Distribution of {col}", nbins=30)
        charts.append({
            "type": "histogram",
            "title": f"Distribution of {col}",
            "data": json.loads(fig.to_json()),
            "description": f"Distribution histogram for {col} showing data spread and frequency patterns across value ranges."
        })
    
    # Bar chart for categorical
    if categorical_cols:
        col = categorical_cols[0]
        value_counts = df[col].value_counts().head(10)
        fig = px.bar(x=value_counts.index, y=value_counts.values,
                    title=f"Top 10 {col}",
                    labels={'x': col, 'y': 'Count'})
        charts.append({
            "type": "bar",
            "title": f"Top 10 {col}",
            "data": json.loads(fig.to_json()),
            "description": f"Bar chart showing the top 10 most frequent values in {col}, useful for identifying dominant categories."
        })
    
    # Box plot for outlier detection
    if len(numeric_cols) >= 1:
        col = numeric_cols[0]
        fig = px.box(df, y=col, title=f"Outlier Detection - {col}")
        charts.append({
            "type": "box",
            "title": f"Outlier Detection - {col}",
            "data": json.loads(fig.to_json()),
            "description": f"Box plot revealing outliers and quartile distribution for {col}, helping identify anomalous data points."
        })
    
    # Scatter plot for relationships
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                        title=f"{numeric_cols[0]} vs {numeric_cols[1]}")
        charts.append({
            "type": "scatter",
            "title": f"{numeric_cols[0]} vs {numeric_cols[1]}",
            "data": json.loads(fig.to_json()),
            "description": f"Scatter plot showing relationship between {numeric_cols[0]} and {numeric_cols[1]}, revealing potential correlations or patterns."
        })
    
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
    """Upload and preview data file"""
    try:
        contents = await file.read()
        
        # Detect file type and read
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(400, "Unsupported file format. Use CSV or Excel")
        
        # Store dataset info
        dataset_id = str(uuid.uuid4())
        dataset_info = {
            "id": dataset_id,
            "name": file.filename,
            "source_type": "file",
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "data_preview": df.head(10).to_dict('records'),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in MongoDB
        await db.datasets.insert_one(dataset_info)
        
        # Store actual data
        data_records = df.to_dict('records')
        await db.dataset_data.insert_one({
            "dataset_id": dataset_id,
            "data": data_records
        })
        
        return dataset_info
    except Exception as e:
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

@api_router.post("/analysis/run")
async def run_analysis(request: AnalysisRequest):
    """Run analysis on dataset"""
    try:
        # Retrieve dataset
        dataset = await db.datasets.find_one({"id": request.dataset_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Load data
        data_doc = await db.dataset_data.find_one({"dataset_id": request.dataset_id}, {"_id": 0})
        df = pd.DataFrame(data_doc['data'])
        
        result = {}
        
        if request.analysis_type == 'profile':
            result = profile_data(df)
        
        elif request.analysis_type == 'clean':
            cleaned_df, report = clean_data(df)
            # Update stored data
            await db.dataset_data.update_one(
                {"dataset_id": request.dataset_id},
                {"$set": {"data": cleaned_df.to_dict('records')}}
            )
            result = {
                "cleaning_report": report,
                "new_row_count": len(cleaned_df)
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
            charts = generate_chart_recommendations(df)
            result = {"charts": charts}
        
        else:
            raise HTTPException(400, f"Unknown analysis type: {request.analysis_type}")
        
        return result
    except Exception as e:
        logging.error(f"Analysis error: {traceback.format_exc()}")
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@api_router.get("/datasets")
async def list_datasets():
    """List all datasets"""
    datasets = await db.datasets.find({}, {"_id": 0}).to_list(100)
    return {"datasets": datasets}

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

@api_router.post("/analysis/chat")
async def analysis_chat(request: ChatRequest):
    """Chat with AI about the dataset for custom analysis"""
    try:
        # Retrieve dataset
        dataset = await db.datasets.find_one({"id": request.dataset_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Load data
        data_doc = await db.dataset_data.find_one({"dataset_id": request.dataset_id}, {"_id": 0})
        df = pd.DataFrame(data_doc['data'])
        
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
        logging.error(f"Chat error: {traceback.format_exc()}")
        raise HTTPException(500, f"Chat failed: {str(e)}")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()