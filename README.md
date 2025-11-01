# PROMISE AI - Intelligent Data Analysis & Prediction Platform

![Version](https://img.shields.io/badge/version-2.0-blue) ![Status](https://img.shields.io/badge/status-production--ready-green) ![License](https://img.shields.io/badge/license-MIT-blue)

## 🎯 Overview

**PROMISE AI** is a full-stack AI/ML-powered data analysis platform that transforms raw data into actionable insights through automated machine learning, intelligent visualizations, and natural language interactions.

### Key Features

🚀 **Multi-Source Data Integration**
- CSV/Excel file uploads with drag & drop
- 5 database types: PostgreSQL, MySQL, Oracle, SQL Server, MongoDB
- GridFS for large files (up to 16TB)
- Connection string parsing

🤖 **Automated Machine Learning**
- 6 ML models: Linear Regression, Random Forest, XGBoost, Decision Tree, LightGBM, LSTM
- Automatic target column selection
- Feature importance analysis
- Model performance comparison

📊 **Intelligent Visualizations**
- 15+ auto-generated charts
- Interactive Plotly visualizations
- AI-powered chart descriptions
- Correlation heatmaps

💬 **Natural Language Chat**
- Create custom charts via chat
- Dynamic analysis requests
- Chart removal commands
- Conversation history persistence

🔬 **Data Quality Analysis**
- Comprehensive profiling
- Missing values detection with detailed insights
- Automatic data cleaning
- Outlier detection

📈 **Training Metadata Tracking**
- Dataset-level performance tracking
- Workspace management
- Model improvement trends
- PDF report generation

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (Python 3.9+)
- MongoDB with GridFS
- Pandas, NumPy, scikit-learn
- XGBoost, LightGBM, TensorFlow
- Emergent LLM Integration

**Frontend:**
- React 18
- Tailwind CSS + Shadcn UI
- Plotly.js
- Axios

**Infrastructure:**
- Docker + Kubernetes
- Nginx reverse proxy
- Supervisor for process management

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB
- Docker (optional)

### Installation

#### Using Docker (Recommended)
```bash
docker-compose up -d
```

#### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python server.py
```

**Frontend:**
```bash
cd frontend
yarn install
yarn start
```

### Environment Configuration

**Backend** (`backend/.env`):
```env
MONGO_URL=mongodb://localhost:27017/promise_ai
EMERGENT_LLM_KEY=your_key_here
```

**Frontend** (`frontend/.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 📚 Documentation

- **[Master Documentation](MASTER_DOCUMENTATION.md)** - Complete system documentation
- **[Technical Documentation](TECHNICAL_DOCUMENTATION.md)** - API reference and architecture
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Feature implementation details
- **[Testing Guide](test_result.md)** - Testing protocols and results
- **[Database Testing Guide](DATABASE_TESTING_GUIDE.md)** - Multi-database setup
- **[MCP Server README](mcp_server/README.md)** - AI agent integration

---

## 🎮 Usage

### 1. Upload Data
- Navigate to Dashboard
- Upload CSV/Excel file or connect to database
- Preview data and column information

### 2. Data Profiling
- View summary statistics
- Analyze missing values (with detailed 2-liner descriptions)
- Check for duplicates
- Auto-clean data with one click

### 3. Predictive Analysis
- Run holistic analysis
- Compare 6 ML models
- View 15+ auto-generated charts
- Explore key correlations
- Get AI-powered insights

### 4. Interactive Chat
- "Show correlation analysis"
- "Create scatter plot of age vs salary"
- "Add pie chart for categories"
- "Remove correlation heatmap"

### 5. Workspace Management
- Save analysis states
- Load previous workspaces
- Track training history
- Download PDF reports

---

## 🔧 Recent Updates

### Version 2.0 (Current)

**Major Refactoring:**
- ✅ Modular backend architecture
- ✅ Separated routes, services, and models
- ✅ Improved code maintainability

**New Features:**
- ✅ Missing Values Details with explanatory descriptions
- ✅ Training Metadata redesign with multi-select
- ✅ PDF report generation
- ✅ Chart overflow permanent fix
- ✅ Model description tooltips
- ✅ Recent datasets multi-select delete

**Bug Fixes:**
- ✅ Fixed chart rendering issues
- ✅ Resolved correlation display
- ✅ Fixed Training Metadata page crashes
- ✅ Improved AI insights display

---

## 🧪 Testing

**Backend Tests:**
```bash
cd backend
pytest tests/test_backend_comprehensive.py -v
```

**Frontend Tests:**
```bash
cd frontend
yarn test
```

---

## 📊 Performance

- **File Upload:** Handles files up to 16TB via GridFS
- **Analysis Speed:** Processes 100K+ rows in seconds
- **ML Training:** Trains 6 models concurrently
- **Responsive UI:** Hot reload enabled for development

---

## 🛠️ Service Management

```bash
# Restart all services
sudo supervisorctl restart all

# Check status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.out.log
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 📧 Support

For issues, questions, or feature requests:
- Check documentation first
- Review `test_result.md` for recent changes
- Check logs for errors
- Open an issue on GitHub

---

## 🎯 Roadmap

### Short Term
- [ ] User authentication system
- [ ] Real-time collaboration
- [ ] Advanced model tuning
- [ ] Email report scheduling

### Long Term
- [ ] Custom model upload
- [ ] Data versioning
- [ ] Multi-language support
- [ ] Mobile app

---

**Built with ❤️ by the PROMISE AI Team**

*Last Updated: November 2025*
