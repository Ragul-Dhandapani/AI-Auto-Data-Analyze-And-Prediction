# PROMISE AI - Frontend Documentation

## 🎨 Frontend Architecture Overview

PROMISE AI's frontend is built with React 18, providing an intuitive and responsive interface for data analysis, ML model training, and AI-powered insights.

---

## 📦 Technology Stack

- **Framework**: React 18.2+ with Hooks
- **Build Tool**: Vite (Fast HMR & optimized builds)
- **UI Library**: shadcn/ui components
- **Styling**: TailwindCSS (utility-first)
- **Routing**: React Router v6
- **Charts**: Plotly.js (interactive visualizations)
- **HTTP Client**: Axios
- **State Management**: React Hooks + localStorage
- **Icons**: Lucide React

---

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AnalysisTabs.jsx           # Main analysis navigation
│   │   ├── CompactDatabaseToggle.jsx  # Oracle/MongoDB switcher
│   │   ├── DataProfiler.jsx           # Dataset profiling
│   │   ├── DataSourceSelector.jsx     # Data upload/connection
│   │   ├── DatabaseSwitcher.jsx       # Database toggle modal
│   │   ├── FeedbackPanel.jsx          # User feedback for predictions
│   │   ├── HyperparameterTuning.jsx   # Model tuning interface
│   │   ├── ModelSelector.jsx          # ML model selection (35+ models)
│   │   ├── PlotlyChart.jsx            # Reusable Plotly wrapper
│   │   ├── PredictiveAnalysis.jsx     # ML training & results
│   │   ├── TimeSeriesAnalysis.jsx     # Forecasting interface
│   │   ├── TrainingMetadataDashboard.jsx  # Training history
│   │   ├── VariableSelectionModal.jsx # Target/feature selection
│   │   ├── VisualizationPanel.jsx     # Chart generation & AI chat
│   │   └── ui/                        # shadcn/ui components
│   ├── pages/
│   │   ├── DashboardPage.jsx          # Main dashboard
│   │   ├── DocumentationPage.jsx      # Documentation UI
│   │   ├── HomePage.jsx               # Landing page
│   │   └── TrainingMetadataPage.jsx   # Training history page
│   ├── App.js                         # Root component
│   ├── index.css                      # Global styles
│   └── main.jsx                       # Entry point
├── .env                               # Environment variables
├── package.json                       # Dependencies
├── vite.config.js                     # Vite configuration
└── tailwind.config.js                 # Tailwind configuration
```

---

## 🧩 Core Components

### 1. **App.js** - Root Component

**Location**: `src/App.js`

**Purpose**: Main application router with navigation and layout.

**Routes**:
- `/` - HomePage (Landing)
- `/dashboard` - DashboardPage (Main app)
- `/training-metadata` - TrainingMetadataPage
- `/documentation` - DocumentationPage

**Key Features**:
- React Router setup
- Navigation with active state
- Responsive layout

**Code Example**:
```jsx
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/training-metadata" element={<TrainingMetadataPage />} />
        <Route path="/documentation" element={<DocumentationPage />} />
      </Routes>
    </Router>
  );
}
```

---

### 2. **DashboardPage.jsx** - Main Dashboard

**Location**: `src/pages/DashboardPage.jsx`

**Purpose**: Primary interface for data upload, analysis, and model training.

**Key Features**:
- Dataset upload (CSV files)
- Database connection (Oracle, MongoDB, PostgreSQL, etc.)
- Dataset list with search/filter
- Analysis tabs integration
- Compact database toggle (Oracle ⟷ MongoDB)

**State Management**:
```jsx
const [datasets, setDatasets] = useState([]);
const [selectedDataset, setSelectedDataset] = useState(null);
const [loading, setLoading] = useState(false);
```

**API Calls**:
```jsx
// Fetch datasets
const fetchDatasets = async () => {
  const response = await axios.get(`${BACKEND_URL}/api/datasource/recent`);
  setDatasets(response.data.datasets);
};

// Upload CSV
const handleUpload = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  await axios.post(`${BACKEND_URL}/api/datasource/upload`, formData);
};
```

---

### 3. **AnalysisTabs.jsx** - Analysis Navigation

**Location**: `src/components/AnalysisTabs.jsx`

**Purpose**: Tabbed interface for different analysis types.

**Tabs**:
1. **Data Profiler** - Dataset statistics and distributions
2. **Predictive Analysis** - ML model training (35+ models)
3. **Visualization** - AI-powered chart generation
4. **Time Series** - Forecasting and anomaly detection
5. **Hyperparameter Tuning** - Model optimization

**Props**:
```jsx
<AnalysisTabs 
  dataset={selectedDataset} 
  onAnalysisComplete={(results) => console.log(results)}
/>
```

---

### 4. **PredictiveAnalysis.jsx** - ML Training Interface

**Location**: `src/components/PredictiveAnalysis.jsx`

**Purpose**: Orchestrates ML model training with variable selection and results display.

**Key Features**:
- **ModelSelector** integration (always visible)
- **VariableSelectionModal** for target/feature selection
- ML Model Comparison table (35+ models)
- Results persistence using `localStorage`
- "New Analysis" button to clear state

**State Management**:
```jsx
const [analysisResults, setAnalysisResults] = useState(null);
const [selectedModels, setSelectedModels] = useState([]);
const [loading, setLoading] = useState(false);

// Persist results to localStorage
useEffect(() => {
  if (analysisResults) {
    localStorage.setItem(
      `analysis_${dataset.id}`,
      JSON.stringify(analysisResults)
    );
  }
}, [analysisResults, dataset.id]);

// Load from localStorage on mount
useEffect(() => {
  const cached = localStorage.getItem(`analysis_${dataset.id}`);
  if (cached) {
    setAnalysisResults(JSON.parse(cached));
  }
}, [dataset.id]);
```

**API Call**:
```jsx
const runAnalysis = async () => {
  const response = await axios.post(
    `${BACKEND_URL}/api/analysis/holistic`,
    {
      dataset_id: dataset.id,
      target_variables: selectedTargets,
      feature_variables: selectedFeatures,
      problem_type: problemType,
      selected_models: selectedModels
    }
  );
  setAnalysisResults(response.data);
};
```

**ML Model Comparison UI**:
- Displays all trained models with metrics (R², RMSE, Accuracy, F1-Score)
- Best model highlighted with 🏆 trophy icon
- Models sorted by performance
- "N/A" displayed for missing confidence scores
- Handles "auto" problem type by converting to "classification"

---

### 5. **ModelSelector.jsx** - Model Selection Component

**Location**: `src/components/ModelSelector.jsx`

**Purpose**: UI for selecting ML models (35+ models) and AI recommendation.

**Key Features**:
- Fetches available models from backend based on problem type
- Manual model selection (checkboxes)
- AI-powered model recommendation
- Loading states for better UX
- Error handling with clear messages

**Props**:
```jsx
<ModelSelector
  problemType="regression" // or "classification", "auto"
  onModelsSelected={(models) => setSelectedModels(models)}
  selectedModels={selectedModels}
/>
```

**API Calls**:
```jsx
// Fetch available models
const fetchModels = async () => {
  const response = await axios.get(
    `${BACKEND_URL}/api/models/available`,
    { params: { problem_type: problemType } }
  );
  setAvailableModels(response.data.models);
};

// Get AI recommendations
const getRecommendations = async () => {
  const response = await axios.post(
    `${BACKEND_URL}/api/models/recommend`,
    {
      dataset_id: dataset.id,
      problem_type: problemType
    }
  );
  setSelectedModels(response.data.recommended_models);
};
```

**Model Categories**:
- **Regression**: Linear Regression, Ridge, Lasso, ElasticNet, SVR, Decision Tree, Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost, AdaBoost, Extra Trees, KNN, etc.
- **Classification**: Logistic Regression, SVC, Decision Tree, Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost, Naive Bayes, KNN, etc.
- **Advanced**: Neural Networks, AutoML, Ensemble methods

---

### 6. **VariableSelectionModal.jsx** - Variable Selection

**Location**: `src/components/VariableSelectionModal.jsx`

**Purpose**: Modal for selecting target variables, features, and problem type.

**Key Features**:
- **Selection Modes**:
  - Manual: User selects variables
  - AI-Suggested: AI recommends optimal variables
  - Hybrid: AI suggests + user refines
  - Skip: Auto-detection

- **Problem Types**:
  - Regression
  - Classification (Binary/Multi-class)
  - Time Series
  - Clustering
  - Dimensionality Reduction
  - Anomaly Detection
  - Auto-Detect

**Props**:
```jsx
<VariableSelectionModal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  dataset={dataset}
  onVariablesSelected={(config) => handleSelection(config)}
/>
```

**Return Value**:
```javascript
{
  target_variables: ['target_column'],
  feature_variables: ['feature1', 'feature2', ...],
  problem_type: 'regression' // or 'classification', 'timeseries', etc.
}
```

---

### 7. **VisualizationPanel.jsx** - Chart Generation & AI Chat

**Location**: `src/components/VisualizationPanel.jsx`

**Purpose**: AI-powered chart generation and interactive chat.

**Key Features**:
- Natural language chart requests
- Azure OpenAI-powered chat
- Chart types: scatter, line, bar, histogram, heatmap, box plot
- "Generate Visualizations" button for initial chart generation
- Chat history with context

**State Management**:
```jsx
const [chatMessages, setChatMessages] = useState([]);
const [visualizations, setVisualizations] = useState([]);
```

**API Call**:
```jsx
const sendChatMessage = async (message) => {
  const response = await axios.post(
    `${BACKEND_URL}/api/analysis/chat`,
    {
      dataset_id: dataset.id,
      message: message,
      conversation_history: chatMessages
    }
  );
  
  if (response.data.action === 'chart') {
    setVisualizations([...visualizations, response.data.chart_data]);
  }
  setChatMessages([...chatMessages, response.data]);
};
```

**Example Chat Prompts**:
- "Show me a scatter plot of price vs sales"
- "Create a histogram of customer age distribution"
- "Generate a correlation heatmap"
- "What insights can you provide about this data?"

---

### 8. **TimeSeriesAnalysis.jsx** - Forecasting

**Location**: `src/components/TimeSeriesAnalysis.jsx`

**Purpose**: Time series forecasting and anomaly detection.

**Key Features**:
- Date column selection
- Target variable selection
- Forecast periods (days/weeks/months ahead)
- Forecasting methods: Prophet, LSTM, or Both
- Anomaly detection with Isolation Forest & LOF
- Interactive Plotly charts

**API Call**:
```jsx
const runForecast = async () => {
  const response = await axios.post(
    `${BACKEND_URL}/api/analysis/timeseries`,
    {
      dataset_id: dataset.id,
      date_column: selectedDateColumn,
      target_column: selectedTargetColumn,
      forecast_periods: periods,
      method: 'both' // or 'prophet', 'lstm'
    }
  );
  setForecastResults(response.data);
};
```

**Output**:
- Forecast chart with confidence intervals
- Trend decomposition (trend, seasonality, residuals)
- Anomaly points highlighted
- Metrics: MAPE, RMSE, MAE

---

### 9. **HyperparameterTuning.jsx** - Model Optimization

**Location**: `src/components/HyperparameterTuning.jsx`

**Purpose**: Optimize model hyperparameters using Grid Search or Random Search.

**Key Features**:
- Model selection
- Parameter grid configuration
- Search strategy: Grid Search or Random Search
- Cross-validation folds
- Best parameters display
- Performance comparison

**API Call**:
```jsx
const runTuning = async () => {
  const response = await axios.post(
    `${BACKEND_URL}/api/analysis/hyperparameter-tuning`,
    {
      dataset_id: dataset.id,
      model_name: selectedModel,
      param_grid: parameterGrid,
      search_type: 'grid', // or 'random'
      cv_folds: 5
    }
  );
  setBestParams(response.data.best_params);
};
```

---

### 10. **TrainingMetadataDashboard.jsx** - Training History

**Location**: `src/components/TrainingMetadataDashboard.jsx`

**Purpose**: View all ML training sessions with metrics and timestamps.

**Key Features**:
- Training history table
- Sortable columns (date, accuracy, model type)
- Search/filter by dataset or model
- Training count and last trained date
- Detailed metrics view (R², RMSE, F1-Score, etc.)

**API Call**:
```jsx
const fetchTrainingMetadata = async () => {
  const response = await axios.get(
    `${BACKEND_URL}/api/training/metadata`,
    { params: { dataset_id: dataset.id } }
  );
  setTrainingHistory(response.data.metadata);
};
```

**Displayed Information**:
- Dataset name
- Problem type (regression/classification)
- Target variable
- Model type
- Metrics (R², Accuracy, etc.)
- Training duration
- Created at timestamp

---

### 11. **CompactDatabaseToggle.jsx** - Database Switcher

**Location**: `src/components/CompactDatabaseToggle.jsx`

**Purpose**: Toggle between Oracle and MongoDB databases.

**Key Features**:
- Compact UI in header
- Visual indicators for current database
- Switch confirmation
- Auto-reload after switch

**API Call**:
```jsx
const switchDatabase = async (dbType) => {
  await axios.post(`${BACKEND_URL}/api/config/switch-db`, {
    db_type: dbType // 'oracle' or 'mongodb'
  });
  window.location.reload(); // Reload to refresh connection
};
```

---

## 🔄 State Management Strategy

### 1. Component State (useState)

Used for local component state:
```jsx
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
const [data, setData] = useState([]);
```

### 2. Persistent State (localStorage)

Used for analysis results to survive page refreshes:
```jsx
// Save to localStorage
const saveResults = (results) => {
  localStorage.setItem(
    `analysis_${datasetId}`,
    JSON.stringify(results)
  );
};

// Load from localStorage
const loadResults = () => {
  const cached = localStorage.getItem(`analysis_${datasetId}`);
  return cached ? JSON.parse(cached) : null;
};

// Clear on "New Analysis"
const clearResults = () => {
  localStorage.removeItem(`analysis_${datasetId}`);
  setAnalysisResults(null);
};
```

**localStorage Keys**:
- `analysis_${dataset.id}` - Predictive analysis results
- `visualizations_${dataset.id}` - Generated charts
- `chat_history_${dataset.id}` - Chat messages

---

## 🌐 API Integration

### Environment Variables

**File**: `frontend/.env`

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Usage in Code**:
```jsx
const BACKEND_URL = import.meta.env.REACT_APP_BACKEND_URL || 
                    process.env.REACT_APP_BACKEND_URL;
```

### Axios Configuration

```jsx
import axios from 'axios';

const api = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor (add auth token if needed)
api.interceptors.request.use((config) => {
  // Add token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (error handling)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
```

### Key API Endpoints

```javascript
// Datasource
GET    /api/datasource/recent                 // Get recent datasets
POST   /api/datasource/upload                 // Upload CSV file
POST   /api/datasource/connect                // Connect to database
GET    /api/datasource/:id                    // Get dataset details

// Analysis
POST   /api/analysis/holistic                 // Run ML analysis
POST   /api/analysis/chat                     // AI chat for insights
POST   /api/analysis/timeseries               // Time series forecasting
POST   /api/analysis/hyperparameter-tuning    // Hyperparameter tuning

// Models
GET    /api/models/available                  // Get available models
POST   /api/models/recommend                  // Get AI recommendations

// Training
GET    /api/training/metadata                 // Get training history
POST   /api/training/feedback                 // Submit prediction feedback

// Config
POST   /api/config/switch-db                  // Switch database
GET    /api/config/current-db                 // Get current database
```

---

## 🎨 Styling with TailwindCSS

### Configuration

**File**: `tailwind.config.js`

```javascript
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b'
      }
    }
  },
  plugins: [require('tailwindcss-animate')]
};
```

### Common Patterns

```jsx
// Card with shadow
<div className="bg-white rounded-lg shadow-md p-6">
  Content
</div>

// Button (primary)
<button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
  Click Me
</button>

// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => <Card key={item.id} />)}
</div>

// Flex container
<div className="flex items-center justify-between">
  <span>Left</span>
  <span>Right</span>
</div>
```

---

## 📊 Plotly.js Charts

### PlotlyChart Component

**Location**: `src/components/PlotlyChart.jsx`

**Usage**:
```jsx
import PlotlyChart from './PlotlyChart';

<PlotlyChart
  data={[
    {
      x: [1, 2, 3, 4],
      y: [10, 15, 13, 17],
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Series 1'
    }
  ]}
  layout={{
    title: 'Sample Chart',
    xaxis: { title: 'X Axis' },
    yaxis: { title: 'Y Axis' }
  }}
/>
```

### Chart Types Supported

- **Scatter Plot**: `type: 'scatter'`
- **Line Chart**: `type: 'scatter', mode: 'lines'`
- **Bar Chart**: `type: 'bar'`
- **Histogram**: `type: 'histogram'`
- **Heatmap**: `type: 'heatmap'`
- **Box Plot**: `type: 'box'`
- **3D Scatter**: `type: 'scatter3d'`

---

## 🚀 Build & Deployment

### Development

```bash
cd frontend
yarn install
yarn dev
```

**Dev Server**: `http://localhost:3000`  
**Hot Reload**: Enabled by default

### Production Build

```bash
yarn build
```

**Output**: `frontend/dist/`

### Deployment Options

1. **Static Hosting** (Vercel, Netlify)
   ```bash
   yarn build
   # Upload dist/ folder
   ```

2. **Docker**
   ```dockerfile
   FROM node:18-alpine
   WORKDIR /app
   COPY package.json yarn.lock ./
   RUN yarn install --frozen-lockfile
   COPY . .
   RUN yarn build
   CMD ["yarn", "preview"]
   ```

3. **Kubernetes**
   - Build Docker image
   - Deploy with ingress for routing
   - Use CDN for static assets

---

## 🐛 Error Handling

### API Error Handling

```jsx
const fetchData = async () => {
  setLoading(true);
  setError(null);
  
  try {
    const response = await axios.get(`${BACKEND_URL}/api/data`);
    setData(response.data);
  } catch (err) {
    setError(err.response?.data?.message || 'Failed to fetch data');
    console.error('API Error:', err);
  } finally {
    setLoading(false);
  }
};
```

### Error Display

```jsx
{error && (
  <div className="bg-red-50 border border-red-400 text-red-700 p-4 rounded">
    <strong>Error:</strong> {error}
  </div>
)}
```

---

## 🧪 Testing Best Practices

### Manual Testing Checklist

- ✅ Upload CSV file and verify dataset list
- ✅ Run predictive analysis with different models
- ✅ Test AI chat and chart generation
- ✅ Switch between Oracle and MongoDB
- ✅ Check Training Metadata page
- ✅ Verify localStorage persistence (refresh page)
- ✅ Test responsive design (mobile, tablet, desktop)
- ✅ Check error handling (invalid file, network error)

---

## 📝 Common UI Patterns

### Loading State

```jsx
{loading ? (
  <div className="flex items-center justify-center py-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    <span className="ml-3">Loading...</span>
  </div>
) : (
  <Content />
)}
```

### Empty State

```jsx
{data.length === 0 && (
  <div className="text-center py-12">
    <p className="text-gray-500 text-lg mb-4">No data available</p>
    <button onClick={fetchData}>Load Data</button>
  </div>
)}
```

### Modal Pattern

```jsx
import { Dialog, DialogContent } from '@/components/ui/dialog';

<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent>
    <h2>Modal Title</h2>
    <p>Modal content</p>
  </DialogContent>
</Dialog>
```

---

## 🔧 Configuration Files

### vite.config.js

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true
      }
    }
  }
});
```

### package.json (Key Dependencies)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "plotly.js": "^2.27.0",
    "react-plotly.js": "^2.6.0",
    "lucide-react": "^0.300.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

---

## 📚 Additional Resources

- **React Documentation**: https://react.dev
- **Vite Guide**: https://vitejs.dev
- **TailwindCSS**: https://tailwindcss.com
- **shadcn/ui**: https://ui.shadcn.com
- **Plotly.js**: https://plotly.com/javascript
- **React Router**: https://reactrouter.com

---

## 🎯 Next Steps

1. Explore the **DashboardPage** to upload your first dataset
2. Review **PredictiveAnalysis** component for ML workflow
3. Experiment with **VisualizationPanel** for AI-powered charts
4. Check **TrainingMetadataDashboard** for training history
5. Customize UI components in `src/components/ui/`

For backend documentation, see `BACKEND.md`  
For database schema, see `DATABASE.md`
