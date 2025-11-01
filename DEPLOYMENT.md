# PROMISE AI - Deployment Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Environment Variables](#environment-variables)
5. [Monitoring & Scaling](#monitoring--scaling)

## Architecture Overview

PROMISE AI consists of three main components:
- **Frontend**: React application (Port 3000)
- **Backend**: FastAPI application (Port 8001)
- **Database**: MongoDB (Port 27017)

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend   │─────▶│   MongoDB   │
│  (React)    │      │  (FastAPI)  │      │             │
│   :3000     │      │    :8001    │      │   :27017    │
└─────────────┘      └─────────────┘      └─────────────┘
```

---

## Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourorg/promise-ai.git
cd promise-ai
```

2. **Set environment variables**
```bash
# Create .env file
echo "EMERGENT_LLM_KEY=your_key_here" > .env
```

3. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

4. **Verify services are running**
```bash
docker-compose ps
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/api
- MongoDB: mongodb://localhost:27017

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Rebuild images
docker-compose build --no-cache

# Scale backend
docker-compose up -d --scale backend=3
```

### Individual Service Builds

**Build Backend:**
```bash
cd backend
docker build -t promise-ai-backend:latest .
```

**Build Frontend:**
```bash
cd frontend
docker build -t promise-ai-frontend:latest .
```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster 1.24+
- kubectl configured
- Helm 3.0+ (optional)
- 8GB RAM minimum across nodes
- 50GB disk space

### Deployment Steps

1. **Create namespace**
```bash
kubectl apply -f k8s/namespace.yaml
```

2. **Set up secrets**
```bash
# Edit k8s/configmap.yaml with your values
kubectl apply -f k8s/configmap.yaml
```

3. **Deploy MongoDB**
```bash
kubectl apply -f k8s/mongodb.yaml

# Wait for MongoDB to be ready
kubectl wait --for=condition=ready pod -l app=mongodb -n promise-ai --timeout=300s
```

4. **Deploy Backend**
```bash
kubectl apply -f k8s/backend.yaml

# Wait for backend to be ready
kubectl wait --for=condition=ready pod -l app=backend -n promise-ai --timeout=300s
```

5. **Deploy Frontend**
```bash
kubectl apply -f k8s/frontend.yaml
```

6. **Set up Ingress (optional)**
```bash
# Update k8s/ingress.yaml with your domain
kubectl apply -f k8s/ingress.yaml
```

### Kubernetes Commands

```bash
# View all resources
kubectl get all -n promise-ai

# View logs
kubectl logs -f deployment/backend -n promise-ai
kubectl logs -f deployment/frontend -n promise-ai

# Scale deployments
kubectl scale deployment backend --replicas=5 -n promise-ai

# Port forwarding for local access
kubectl port-forward svc/frontend-service 3000:3000 -n promise-ai
kubectl port-forward svc/backend-service 8001:8001 -n promise-ai

# Restart deployments
kubectl rollout restart deployment/backend -n promise-ai

# View events
kubectl get events -n promise-ai --sort-by='.lastTimestamp'
```

### Health Checks

**Check service health:**
```bash
# Backend health
curl http://localhost:8001/api/

# Frontend health
curl http://localhost:3000/
```

---

## Environment Variables

### Backend (.env or ConfigMap)
```bash
MONGO_URL=mongodb://mongodb:27017/autopredict
EMERGENT_LLM_KEY=your_emergent_llm_key
PYTHONUNBUFFERED=1
```

### Frontend (.env or ConfigMap)
```bash
REACT_APP_BACKEND_URL=http://backend-service:8001
```

### Updating Secrets in Kubernetes
```bash
# Create secret from literal
kubectl create secret generic promise-ai-secrets \
  --from-literal=EMERGENT_LLM_KEY=your_key \
  --from-literal=MONGO_URL=mongodb://mongodb-service:27017/autopredict \
  -n promise-ai

# Update existing secret
kubectl delete secret promise-ai-secrets -n promise-ai
kubectl create secret generic promise-ai-secrets \
  --from-literal=EMERGENT_LLM_KEY=new_key \
  -n promise-ai
```

---

## Monitoring & Scaling

### Resource Monitoring

**Docker:**
```bash
docker stats
```

**Kubernetes:**
```bash
kubectl top nodes
kubectl top pods -n promise-ai
```

### Horizontal Scaling

**Docker Compose:**
```bash
docker-compose up -d --scale backend=3
```

**Kubernetes:**
```bash
# Manual scaling
kubectl scale deployment backend --replicas=5 -n promise-ai

# Auto-scaling (HPA)
kubectl autoscale deployment backend \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n promise-ai
```

### Backup & Recovery

**MongoDB Backup:**
```bash
# Docker
docker exec promise-ai-mongodb mongodump --out /backup

# Kubernetes
kubectl exec -n promise-ai mongodb-0 -- mongodump --out /backup
```

**Restore:**
```bash
# Docker
docker exec promise-ai-mongodb mongorestore /backup

# Kubernetes
kubectl exec -n promise-ai mongodb-0 -- mongorestore /backup
```

---

## Troubleshooting

### Common Issues

1. **Backend cannot connect to MongoDB**
```bash
# Check MongoDB status
docker-compose ps mongodb
kubectl get pods -n promise-ai | grep mongodb

# Check logs
docker-compose logs mongodb
kubectl logs -n promise-ai mongodb-0
```

2. **Frontend cannot reach backend**
```bash
# Verify backend is running
curl http://localhost:8001/api/

# Check network connectivity
docker network ls
kubectl get svc -n promise-ai
```

3. **Out of memory errors**
```bash
# Increase container limits in docker-compose.yml or k8s/*.yaml
# Restart services
```

### View Logs

**Docker:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Kubernetes:**
```bash
kubectl logs -f deployment/backend -n promise-ai
kubectl logs -f deployment/frontend -n promise-ai
```

---

## Production Considerations

1. **Use environment-specific configs**
2. **Enable HTTPS/TLS**
3. **Set up monitoring (Prometheus/Grafana)**
4. **Configure backup strategies**
5. **Implement CI/CD pipelines**
6. **Use managed databases for production**
7. **Set resource limits appropriately**
8. **Enable logging aggregation**

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourorg/promise-ai/issues
- Documentation: https://docs.promise-ai.com
