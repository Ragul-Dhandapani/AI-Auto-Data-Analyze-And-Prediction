# PROMISE AI - Predictive Real-time Operational Monitoring & Intelligence System

![PROMISE AI](https://img.shields.io/badge/AI-Powered-blue) ![ML](https://img.shields.io/badge/ML-Enterprise-green) ![React](https://img.shields.io/badge/React-18-61dafb) ![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688)

**PROMISE AI** is an enterprise-grade machine learning platform that automates the entire ML workflow from data ingestion to model deployment and continuous improvement.

## 🌟 Key Features

- **Multi-Source Data Connectivity**: CSV, PostgreSQL, MySQL, SQL Server, Oracle, MongoDB (with Kerberos)
- **Classification & Regression**: Binary, multi-class classification and numeric prediction with 6+ ML algorithms
- **Time Series Forecasting**: Prophet and LSTM forecasting with anomaly detection
- **Hyperparameter Tuning**: Grid and random search optimization strategies
- **AI-Powered Insights**: Business recommendations and model explainability with SHAP
- **Active Learning Loop**: User feedback and continuous model improvement
- **NLP & Multi-Table Support**: Text feature extraction, relational data joins, metadata tracking
- **Enterprise Security**: Kerberos authentication with fast analysis

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Features](#features)
- [Documentation](#documentation)
- [Contributing](#contributing)

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **npm/yarn**: Latest version (yarn recommended)
- **MongoDB**: 5.0 or higher
- **pip**: 23.0 or higher

### One-Command Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd promise-ai

# Run setup script
./setup.sh
```

## 🛠 Technology Stack

### Frontend
- **React 18**: Modern UI framework
- **Vite**: Lightning-fast build tool
- **Shadcn/UI**: Beautiful component library
- **TailwindCSS**: Utility-first CSS
- **Plotly.js**: Interactive data visualization
- **Axios**: HTTP client
- **React Router**: Client-side routing

### Backend
- **FastAPI**: High-performance async Python framework
- **Python 3.11+**: Core language
- **MongoDB**: NoSQL database
- **Motor**: Async MongoDB driver
- **scikit-learn**: ML library
- **XGBoost & LightGBM**: Gradient boosting
- **TensorFlow/Keras**: Deep learning (LSTM)
- **Prophet**: Time series forecasting
- **SHAP & LIME**: Model explainability

### Database Connectors
- PostgreSQL (psycopg2)
- MySQL (pymysql)
- SQL Server (pyodbc)
- Oracle (cx_Oracle)
- MongoDB (motor)
- Kerberos (GSSAPI authentication)

## 📁 Project Structure

```
promise-ai/
├── backend/
│   ├── app/
│   │   ├── database/          # Database connections
│   │   ├── models/            # Pydantic models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt       # Python dependencies
│   ├── server.py              # Server entry point
│   ├── create_indexes.py      # MongoDB indexes
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   └── App.js             # Main app component
│   ├── package.json           # Node dependencies
│   └── .env                   # Frontend config
├── mcp_server.py              # MCP Server for AI assistants
├── README.md                  # This file
├── SETUP_GUIDE.md             # Detailed setup instructions
├── API_DOCUMENTATION.md       # API reference
├── DATABASE_SCHEMA.md         # MongoDB schema
└── MCP_SERVER.md              # MCP server documentation
```

## 💻 Installation

For detailed installation instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Create MongoDB indexes
python create_indexes.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install  # or npm install

# Create .env file
cp .env.example .env
# Edit .env with your backend URL
```

## ⚙️ Configuration

### Backend Environment Variables (.env)

```env
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=autopredict_db

# LLM Configuration (Optional)
EMERGENT_LLM_KEY=your_llm_key_here

# Server Configuration
PORT=8001
```

### Frontend Environment Variables (.env)

```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🏃 Running the Application

### Development Mode

**Backend:**
```bash
cd backend
source venv/bin/activate
python server.py
# Backend runs on http://localhost:8001
```

**Frontend:**
```bash
cd frontend
yarn dev  # or npm run dev
# Frontend runs on http://localhost:3000
```

### Production Mode

```bash
# Backend
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8001

# Frontend
cd frontend
yarn build
yarn preview
```

## 📖 Features

### 1. Data Upload & Connection
- Upload CSV/Excel files (up to 100MB)
- Connect to multiple database types
- Custom SQL query execution
- Kerberos authentication for enterprise databases

### 2. Predictive Analysis
- Auto-detect problem type (regression/classification/time series)
- Train 6+ ML algorithms simultaneously
- Model comparison with performance metrics
- Variable selection (Manual/AI-Suggested/Hybrid)
- Multi-target prediction support

### 3. Time Series Forecasting
- Prophet forecasting with trend decomposition
- LSTM neural network forecasting
- Anomaly detection (Isolation Forest, LOF)
- Confidence interval visualization

### 4. Hyperparameter Tuning
- Grid search (exhaustive)
- Random search (faster)
- Cross-validation with multiple folds
- Custom parameter configuration

### 5. AI-Powered Insights
- Statistical insights generation
- Anomaly detection insights
- Business recommendations
- Model explainability (SHAP values)

### 6. Active Learning
- Submit prediction feedback
- Track model accuracy over time
- Retrain models with feedback data
- Continuous improvement loop

### 7. Training Metadata
- Track all training sessions
- Compare model performance
- Audit trail for compliance
- Export metadata reports (PDF)

## 📚 Documentation

- **[Setup Guide](SETUP_GUIDE.md)**: Detailed installation and setup instructions
- **[API Documentation](API_DOCUMENTATION.md)**: Complete API reference
- **[Database Schema](DATABASE_SCHEMA.md)**: MongoDB collection structure
- **[MCP Server](MCP_SERVER.md)**: Model Context Protocol server setup

## 🔧 Advanced Configuration

### MongoDB Optimization

```bash
# Create indexes for better performance
python backend/create_indexes.py
```

### Environment-Specific Settings

```bash
# Development
export ENV=development

# Production
export ENV=production
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
yarn test
```

## 📊 Performance

- **Analysis Speed**: 8-15 seconds for 10MB datasets
- **Workspace Save**: 2-5 seconds (with compression)
- **Large Dataset Support**: Optimized for 100MB+ files
- **Concurrent Users**: Supports multiple simultaneous analyses

## 🔒 Security

- Kerberos authentication support
- Secure database connections
- Environment variable configuration
- No hardcoded credentials

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary and confidential.

## 🆘 Support

For issues and questions:
- Check [API Documentation](API_DOCUMENTATION.md)
- Review [Setup Guide](SETUP_GUIDE.md)
- Open an issue in the repository

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Real-time streaming data analysis
- [ ] Advanced NLP capabilities
- [ ] Custom model deployment
- [ ] Automated report scheduling

## ⚡ Quick Commands

```bash
# Backend
cd backend && python server.py

# Frontend
cd frontend && yarn dev

# Create indexes
cd backend && python create_indexes.py

# MCP Server
python mcp_server.py
```

---

**Built with ❤️ for Enterprise Machine Learning**
