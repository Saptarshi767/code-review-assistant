# Deployment Guide

This guide covers different deployment options for the Code Review Assistant.

## Quick Start with Docker Compose

### Development Environment

1. **Clone and setup**:
```bash
git clone <repository-url>
cd code-review-assistant
cp .env.example .env
```

2. **Configure environment**:
Edit `.env` with your LLM API keys and settings.

3. **Start services**:
```bash
docker-compose up -d
```

4. **Access the application**:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

### Production Environment

1. **Prepare production environment**:
```bash
cp .env.example .env.production
# Edit .env.production with production settings
```

2. **Deploy with production compose**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM service to use | `gemini` or `openai` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `JWT_SECRET_KEY` | JWT signing secret | `your-secret-key` |
| `API_KEY_SALT` | API key generation salt | `your-salt` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `DEBUG` | `true` | Enable debug mode |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload size |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `10` | API rate limit |
| `CORS_ENABLED` | `true` | Enable CORS |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |

### Security Variables (Production)

| Variable | Description |
|----------|-------------|
| `TLS_CERT_FILE` | Path to TLS certificate |
| `TLS_KEY_FILE` | Path to TLS private key |
| `TLS_CA_FILE` | Path to CA bundle |

## Docker Deployment Options

### Option 1: Single Container

```bash
# Build image
docker build -t code-review-assistant .

# Run container
docker run -d \
  --name code-review-assistant \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/logs:/app/logs \
  code-review-assistant
```

### Option 2: Docker Compose (Recommended)

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# With monitoring
docker-compose --profile monitoring up -d

# With reverse proxy
docker-compose --profile production up -d
```

### Option 3: Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml code-review

# Scale services
docker service scale code-review_code-review-assistant=3
```

## Cloud Deployment

### AWS ECS

1. **Create task definition**:
```json
{
  "family": "code-review-assistant",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "code-review-assistant",
      "image": "your-account.dkr.ecr.region.amazonaws.com/code-review-assistant:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LLM_PROVIDER",
          "value": "gemini"
        }
      ],
      "secrets": [
        {
          "name": "GEMINI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:gemini-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/code-review-assistant",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

2. **Create ECS service**:
```bash
aws ecs create-service \
  --cluster your-cluster \
  --service-name code-review-assistant \
  --task-definition code-review-assistant:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Run

1. **Build and push image**:
```bash
# Build for Cloud Run
docker build -t gcr.io/your-project/code-review-assistant .

# Push to Container Registry
docker push gcr.io/your-project/code-review-assistant
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy code-review-assistant \
  --image gcr.io/your-project/code-review-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars LLM_PROVIDER=gemini \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --memory 1Gi \
  --cpu 1 \
  --timeout 600 \
  --max-instances 10
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name code-review-assistant \
  --image your-registry.azurecr.io/code-review-assistant:latest \
  --cpu 1 \
  --memory 1 \
  --ports 8000 \
  --environment-variables LLM_PROVIDER=gemini \
  --secure-environment-variables GEMINI_API_KEY=your-api-key \
  --dns-name-label code-review-assistant
```

## Kubernetes Deployment

### Basic Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-review-assistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: code-review-assistant
  template:
    metadata:
      labels:
        app: code-review-assistant
    spec:
      containers:
      - name: code-review-assistant
        image: code-review-assistant:latest
        ports:
        - containerPort: 8000
        env:
        - name: LLM_PROVIDER
          value: "gemini"
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: gemini-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: code-review-assistant-service
spec:
  selector:
    app: code-review-assistant
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic llm-secrets \
  --from-literal=gemini-api-key=your-api-key

# Apply deployment
kubectl apply -f deployment.yaml

# Check status
kubectl get pods
kubectl get services
```

## Monitoring and Logging

### Prometheus Metrics

The application exposes metrics at `/api/metrics`. Configure Prometheus:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'code-review-assistant'
    static_configs:
      - targets: ['code-review-assistant:8000']
    metrics_path: '/api/metrics'
    scrape_interval: 30s
```

### Log Aggregation

For centralized logging, configure log forwarding:

```yaml
# fluentd configuration
<source>
  @type tail
  path /var/log/app/*.log
  pos_file /var/log/fluentd/app.log.pos
  tag app.logs
  format json
</source>

<match app.logs>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name code-review-logs
</match>
```

## Security Considerations

### Production Checklist

- [ ] Use HTTPS/TLS in production
- [ ] Set strong JWT secrets and API key salts
- [ ] Configure proper CORS origins
- [ ] Enable rate limiting
- [ ] Use secrets management (AWS Secrets Manager, etc.)
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Use non-root container user
- [ ] Scan images for vulnerabilities
- [ ] Set resource limits

### Network Security

```bash
# Create isolated network
docker network create --driver bridge code-review-network

# Run with network isolation
docker-compose up -d
```

### Secrets Management

```bash
# Using Docker secrets
echo "your-api-key" | docker secret create gemini_api_key -

# Reference in compose file
secrets:
  - gemini_api_key
```

## Scaling and Performance

### Horizontal Scaling

```bash
# Scale with Docker Compose
docker-compose up -d --scale code-review-assistant=3

# Scale with Kubernetes
kubectl scale deployment code-review-assistant --replicas=5
```

### Load Balancing

Configure nginx for load balancing:

```nginx
upstream code_review_backend {
    server code-review-assistant-1:8000;
    server code-review-assistant-2:8000;
    server code-review-assistant-3:8000;
}
```

### Performance Tuning

1. **Adjust worker processes**:
```bash
# In Dockerfile or docker-compose
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

2. **Configure resource limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

## Troubleshooting

### Common Issues

1. **Container won't start**:
```bash
# Check logs
docker logs code-review-assistant

# Check health
docker exec code-review-assistant curl -f http://localhost:8000/api/health
```

2. **API key issues**:
```bash
# Verify environment variables
docker exec code-review-assistant env | grep API_KEY
```

3. **File upload issues**:
```bash
# Check volume mounts
docker inspect code-review-assistant | grep Mounts -A 10
```

4. **Performance issues**:
```bash
# Monitor resource usage
docker stats code-review-assistant
```

### Health Checks

The application provides comprehensive health checks:

```bash
# Basic health check
curl http://localhost:8000/api/health

# Detailed health with metrics
curl http://localhost:8000/api/health?include_metrics=true

# Service status
curl http://localhost:8000/api/status
```

## Backup and Recovery

### Data Backup

```bash
# Backup reports and uploads
docker run --rm -v code-review-assistant_app-reports:/data -v $(pwd):/backup alpine tar czf /backup/reports-backup.tar.gz /data

# Backup configuration
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup
```

### Disaster Recovery

1. **Restore from backup**:
```bash
# Restore reports
docker run --rm -v code-review-assistant_app-reports:/data -v $(pwd):/backup alpine tar xzf /backup/reports-backup.tar.gz -C /

# Restore configuration
cp .env.backup .env
```

2. **Redeploy services**:
```bash
docker-compose down
docker-compose up -d
```

This deployment guide provides comprehensive options for running the Code Review Assistant in various environments, from local development to production cloud deployments.