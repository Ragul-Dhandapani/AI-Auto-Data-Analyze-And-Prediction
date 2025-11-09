# PROMISE AI Platform - Deployment Guide

Production deployment guide for PROMISE AI platform.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Deployment](#database-deployment)
4. [Application Deployment](#application-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Domain & SSL Configuration](#domain--ssl-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Performance Tuning](#performance-tuning)
10. [Security Hardening](#security-hardening)

---

## Prerequisites

### Required Services
- **Cloud Provider**: AWS, Azure, or GCP
- **Container Orchestration**: Kubernetes or Docker
- **Database**: Oracle RDS 19c or MongoDB Atlas
- **Domain**: Registered domain name
- **SSL Certificate**: Let's Encrypt or purchased SSL

### Required Tools
- Docker
- kubectl (for Kubernetes)
- Supervisor (for process management)
- Nginx (reverse proxy)

---

## Environment Setup

### Production Environment Variables

**Backend `.env` (Production)**:
```bash
# Database Configuration
DB_TYPE="oracle"

# Oracle RDS Configuration
ORACLE_USER="prod_user"
ORACLE_PASSWORD="<strong-password>"
ORACLE_DSN="prod-oracle.region.rds.amazonaws.com:1521/ORCL"
ORACLE_HOST="prod-oracle.region.rds.amazonaws.com"
ORACLE_PORT="1521"
ORACLE_SERVICE_NAME="ORCL"
ORACLE_POOL_SIZE="20"  # Increased for production

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY="<production-key>"
AZURE_OPENAI_ENDPOINT="https://prod-resource.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"

# Application Configuration
ENVIRONMENT="production"
DEBUG="false"
ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

**Frontend `.env` (Production)**:
```bash
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

---

## Database Deployment

### Oracle RDS Setup (AWS)

```bash
# Create Oracle RDS instance
aws rds create-db-instance \
  --db-instance-identifier promise-ai-oracle \
  --db-instance-class db.t3.medium \
  --engine oracle-se2 \
  --engine-version 19.0.0.0 \
  --master-username admin \
  --master-user-password <strong-password> \
  --allocated-storage 100 \
  --storage-type gp2 \
  --backup-retention-period 7 \
  --publicly-accessible false \
  --vpc-security-group-ids sg-xxxxx \
  --db-subnet-group-name promise-ai-subnet
```

**Security Group Configuration**:
```bash
# Allow inbound Oracle traffic from application servers only
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 1521 \
  --source-group sg-yyyyy  # Application server security group
```

**Initialize Schema**:
```bash
# Connect to RDS
sqlplus admin/<password>@prod-oracle.region.rds.amazonaws.com:1521/ORCL

# Run schema creation
@backend/app/database/oracle_schema.sql

# Verify tables
SELECT table_name FROM user_tables;
```

### MongoDB Atlas Setup

1. Create production cluster (M10 or higher)
2. Enable backup with point-in-time recovery
3. Configure IP whitelist (application server IPs only)
4. Create database user with strong password
5. Enable encryption at rest
6. Configure connection string with retry writes

---

## Application Deployment

### Option 1: Docker Deployment

**Build Docker Images**:

```bash
# Backend
cd backend
docker build -t promise-ai-backend:latest .

# Frontend
cd ../frontend
docker build -t promise-ai-frontend:latest .
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  backend:
    image: promise-ai-backend:latest
    container_name: promise-ai-backend
    restart: always
    ports:
      - "8001:8001"
    environment:
      - DB_TYPE=${DB_TYPE}
      - ORACLE_USER=${ORACLE_USER}
      - ORACLE_PASSWORD=${ORACLE_PASSWORD}
      - ORACLE_DSN=${ORACLE_DSN}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
    volumes:
      - ./backend/logs:/app/logs
    depends_on:
      - oracle
    networks:
      - promise-ai-network

  frontend:
    image: promise-ai-frontend:latest
    container_name: promise-ai-frontend
    restart: always
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_BACKEND_URL=https://api.yourdomain.com
    networks:
      - promise-ai-network

  nginx:
    image: nginx:alpine
    container_name: promise-ai-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - promise-ai-network

networks:
  promise-ai-network:
    driver: bridge
```

**Deploy**:
```bash
docker-compose up -d
docker-compose logs -f
```

---

## Kubernetes Deployment

### Kubernetes Manifests

**Namespace**:
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: promise-ai
```

**ConfigMap**:
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promise-ai-config
  namespace: promise-ai
data:
  DB_TYPE: "oracle"
  ORACLE_HOST: "prod-oracle.region.rds.amazonaws.com"
  ORACLE_PORT: "1521"
  ORACLE_SERVICE_NAME: "ORCL"
  AZURE_OPENAI_ENDPOINT: "https://prod-resource.openai.azure.com/"
```

**Secrets**:
```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: promise-ai-secrets
  namespace: promise-ai
type: Opaque
stringData:
  ORACLE_USER: "prod_user"
  ORACLE_PASSWORD: "<strong-password>"
  AZURE_OPENAI_API_KEY: "<api-key>"
```

**Backend Deployment**:
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: promise-ai-backend
  namespace: promise-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: promise-ai-backend
  template:
    metadata:
      labels:
        app: promise-ai-backend
    spec:
      containers:
      - name: backend
        image: promise-ai-backend:latest
        ports:
        - containerPort: 8001
        envFrom:
        - configMapRef:
            name: promise-ai-config
        - secretRef:
            name: promise-ai-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Backend Service**:
```yaml
# backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: promise-ai-backend-service
  namespace: promise-ai
spec:
  selector:
    app: promise-ai-backend
  ports:
  - protocol: TCP
    port: 8001
    targetPort: 8001
  type: ClusterIP
```

**Frontend Deployment & Service** (similar structure)

**Ingress**:
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: promise-ai-ingress
  namespace: promise-ai
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - yourdomain.com
    - api.yourdomain.com
    secretName: promise-ai-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: promise-ai-frontend-service
            port:
              number: 3000
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: promise-ai-backend-service
            port:
              number: 8001
```

**Deploy to Kubernetes**:
```bash
# Apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
kubectl apply -f ingress.yaml

# Verify deployment
kubectl get pods -n promise-ai
kubectl get services -n promise-ai
kubectl logs -f deployment/promise-ai-backend -n promise-ai
```

---

## Domain & SSL Configuration

### DNS Configuration

**A Records**:
```
yourdomain.com          → Load Balancer IP
www.yourdomain.com      → Load Balancer IP
api.yourdomain.com      → Load Balancer IP
```

### SSL Certificate (Let's Encrypt)

**Using cert-manager (Kubernetes)**:
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

**Using Certbot (Traditional)**:
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Nginx Configuration

**Production nginx.conf**:
```nginx
events {
    worker_connections 4096;
}

http {
    upstream backend {
        server backend:8001;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        client_max_body_size 100M;

        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 600s;
            proxy_send_timeout 600s;
            proxy_read_timeout 600s;
        }

        location /api/datasource/upload {
            limit_req zone=upload_limit burst=5 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            client_max_body_size 500M;
            
            proxy_connect_timeout 1200s;
            proxy_send_timeout 1200s;
            proxy_read_timeout 1200s;
        }
    }
}
```

---

## Monitoring & Logging

### Application Logs

**Centralized Logging (ELK Stack)**:
```yaml
# filebeat.yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/supervisor/backend*.log
    - /var/log/supervisor/frontend*.log
  fields:
    app: promise-ai

output.elasticsearch:
  hosts: ["elasticsearch:9200"]

setup.kibana:
  host: "kibana:5601"
```

### Monitoring (Prometheus + Grafana)

**Prometheus Configuration**:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'promise-ai-backend'
    static_configs:
      - targets: ['backend:8001']
    metrics_path: '/metrics'
```

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/api/

# Frontend health
curl https://yourdomain.com/

# Database connection
curl https://api.yourdomain.com/api/health
```

---

## Backup & Recovery

### Database Backups

**Oracle RDS Automated Backups**:
- Retention period: 7-30 days
- Daily snapshots
- Point-in-time recovery enabled

**Manual Backup**:
```bash
# Export schema
expdp admin/<password>@prod-oracle/ORCL \
  schemas=promise_ai \
  directory=DATA_PUMP_DIR \
  dumpfile=promise_ai_backup.dmp \
  logfile=promise_ai_backup.log
```

**MongoDB Atlas Backups**:
- Continuous backups enabled
- Snapshot retention: 30 days
- Point-in-time recovery within 24 hours

### Application Backups

```bash
# Backup environment files
tar -czf promise-ai-config-backup.tar.gz \
  backend/.env \
  frontend/.env \
  nginx.conf

# Backup logs
tar -czf promise-ai-logs-$(date +%Y%m%d).tar.gz \
  /var/log/supervisor/
```

### Disaster Recovery

1. **Database Restore**:
   ```bash
   # Oracle
   impdp admin/<password>@prod-oracle/ORCL \
     schemas=promise_ai \
     directory=DATA_PUMP_DIR \
     dumpfile=promise_ai_backup.dmp
   
   # MongoDB
   mongorestore --uri="mongodb+srv://..." --archive=backup.archive
   ```

2. **Application Restore**:
   ```bash
   # Restore from backup
   docker-compose down
   tar -xzf promise-ai-config-backup.tar.gz
   docker-compose up -d
   ```

---

## Performance Tuning

### Backend Optimization

**Increase Workers**:
```bash
# For high traffic
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8001 \
  --workers 4 \
  --loop uvloop \
  --http httptools
```

**Database Connection Pooling**:
```python
# backend/.env
ORACLE_POOL_SIZE="30"  # Adjust based on load
```

### Frontend Optimization

**Build for Production**:
```bash
cd frontend
yarn build
# Outputs to dist/ folder
```

**Enable Caching**:
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Database Optimization

**Oracle**:
- Enable automatic statistics gathering
- Create proper indexes on frequently queried columns
- Use table partitioning for large tables

**MongoDB**:
- Create compound indexes
- Enable sharding for large collections
- Use connection pooling

---

## Security Hardening

### Application Security

1. **Environment Variables**: Never commit to git
2. **API Rate Limiting**: Implemented in nginx
3. **Input Validation**: All user inputs sanitized
4. **CORS**: Restricted to allowed origins only
5. **SQL Injection**: Parameterized queries used

### Network Security

```bash
# Firewall rules (iptables)
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
sudo iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
```

### SSL/TLS Security

- Use TLS 1.2 or higher
- Disable weak ciphers
- Enable HSTS
- Configure OCSP stapling

---

## Scaling Strategy

### Horizontal Scaling

**Kubernetes Autoscaling**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: promise-ai-backend-hpa
  namespace: promise-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: promise-ai-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Database Scaling

**Oracle RDS**:
- Vertical scaling: Increase instance size
- Read replicas for read-heavy workloads

**MongoDB Atlas**:
- Vertical scaling: Increase cluster tier
- Horizontal scaling: Enable sharding

---

## Maintenance

### Zero-Downtime Deployment

```bash
# Rolling update (Kubernetes)
kubectl set image deployment/promise-ai-backend \
  backend=promise-ai-backend:v2.0.0 \
  -n promise-ai

# Watch rollout
kubectl rollout status deployment/promise-ai-backend -n promise-ai

# Rollback if needed
kubectl rollout undo deployment/promise-ai-backend -n promise-ai
```

### Database Maintenance

```sql
-- Oracle: Gather statistics
EXEC DBMS_STATS.GATHER_SCHEMA_STATS('PROMISE_AI');

-- Check tablespace usage
SELECT tablespace_name, 
       ROUND(used_space * 8192/1024/1024/1024, 2) AS used_gb,
       ROUND(tablespace_size * 8192/1024/1024/1024, 2) AS total_gb
FROM dba_tablespace_usage_metrics;
```

---

## Post-Deployment Checklist

- [ ] SSL certificate installed and auto-renewal configured
- [ ] DNS records pointing to correct IPs
- [ ] Database backups scheduled and tested
- [ ] Monitoring and alerting configured
- [ ] Application logs centralized
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Health checks passing
- [ ] Performance benchmarks met
- [ ] Disaster recovery plan documented
- [ ] Team notified of production URLs and credentials

---

For local development, see [LOCAL_SETUP.md](LOCAL_SETUP.md)

For architecture details, see [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)
