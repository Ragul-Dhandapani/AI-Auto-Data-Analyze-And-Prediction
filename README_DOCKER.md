# PROMISE AI - Docker & Kubernetes Ready

## 🚀 Quick Start

### Using Docker Compose (Recommended for Development)
```bash
# Set your API key
export EMERGENT_LLM_KEY=your_key_here

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8001/api
```

### Using Kubernetes (Production)
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check status
kubectl get all -n promise-ai
```

## 📁 Project Structure

```
promise-ai/
├── backend/                 # FastAPI Backend
│   ├── server.py           # Main application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container image
│   └── .dockerignore       
├── frontend/                # React Frontend
│   ├── src/                # Source code
│   ├── public/             # Static assets
│   ├── package.json        # Node dependencies
│   ├── Dockerfile          # Frontend container image
│   ├── nginx.conf          # Nginx configuration
│   └── .dockerignore       
├── k8s/                     # Kubernetes Manifests
│   ├── namespace.yaml      # Namespace definition
│   ├── configmap.yaml      # Configuration
│   ├── mongodb.yaml        # Database deployment
│   ├── backend.yaml        # Backend deployment
│   ├── frontend.yaml       # Frontend deployment
│   └── ingress.yaml        # Ingress rules
├── docker-compose.yml       # Docker Compose configuration
├── DEPLOYMENT.md            # Detailed deployment guide
└── README.md               # This file
```

## 🔧 Technology Stack

- **Frontend**: React 18, Tailwind CSS, Plotly.js
- **Backend**: FastAPI (Python 3.11), Motor (MongoDB async)
- **Database**: MongoDB 7.0
- **AI/ML**: scikit-learn, TensorFlow, XGBoost
- **LLM**: Emergent Integrations (OpenAI GPT-4o-mini)
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes

## 📦 Deployment Options

### 1. Local Development (Docker Compose)
Best for: Development, testing, local demos
- Single command deployment
- Hot reload enabled
- Integrated logging

### 2. Kubernetes Cluster
Best for: Production, staging, high availability
- Auto-scaling
- Health checks
- Load balancing
- Rolling updates

### 3. Cloud Platforms
- **AWS**: EKS + RDS + S3
- **GCP**: GKE + Cloud SQL + GCS
- **Azure**: AKS + Cosmos DB + Blob Storage

## 🔐 Environment Variables

### Required Variables
```bash
# Backend
MONGO_URL=mongodb://mongodb:27017/autopredict
EMERGENT_LLM_KEY=your_emergent_llm_key

# Frontend
REACT_APP_BACKEND_URL=http://backend:8001
```

## 🛠️ Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Development
```bash
cd frontend
yarn install
yarn start
```

## 📊 Features

- ✅ **Data Upload**: CSV/Excel file support with large file handling (GridFS)
- ✅ **Data Profiling**: Automatic data quality analysis
- ✅ **Visualizations**: 15+ auto-generated charts with AI insights
- ✅ **Predictive Analysis**: Multiple ML models (XGBoost, LSTM, Random Forest)
- ✅ **Chat Interface**: Natural language chart generation
- ✅ **Workspace Management**: Save/load analysis states
- ✅ **Self-Training Models**: Incremental learning with training counters

## 📈 Scaling

### Docker Compose
```bash
docker-compose up -d --scale backend=3
```

### Kubernetes
```bash
kubectl scale deployment backend --replicas=5 -n promise-ai
```

## 🔍 Monitoring

### Docker
```bash
docker-compose logs -f
docker stats
```

### Kubernetes
```bash
kubectl logs -f deployment/backend -n promise-ai
kubectl top pods -n promise-ai
```

## 🐛 Troubleshooting

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting guide.

### Quick Checks
```bash
# Check service health
curl http://localhost:8001/api/
curl http://localhost:3000/

# View logs
docker-compose logs backend
kubectl logs -n promise-ai deployment/backend
```

## 📝 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📧 Support

For support, email support@promise-ai.com or open an issue on GitHub.
