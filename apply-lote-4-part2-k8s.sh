#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 4 - PARTE 2
# PRONAS/PCD System - Kubernetes Manifests
# Execute após aplicar a Parte 1

set -e

echo "🚀 LOTE 4 PARTE 2: Kubernetes Manifests"
echo "======================================="

if [ ! -d "infra/docker/nginx" ]; then
    echo "❌ Execute a Parte 1 primeiro."
    exit 1
fi

echo "📝 Criando Kubernetes Manifests..."

# Kubernetes namespace
mkdir -p infra/k8s/base
cat > infra/k8s/base/namespace.yaml << 'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: pronas-pcd
  labels:
    name: pronas-pcd
    app.kubernetes.io/name: pronas-pcd
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: system
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: pronas-pcd-quota
  namespace: pronas-pcd
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    persistentvolumeclaims: "10"
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pronas-pcd-network-policy
  namespace: pronas-pcd
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: pronas-pcd
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: pronas-pcd
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 443
EOF

# ConfigMaps
cat > infra/k8s/base/configmaps.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
  namespace: pronas-pcd
data:
  ENVIRONMENT: "production"
  API_DEBUG: "false"
  API_RELOAD: "false"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  POSTGRES_HOST: "postgres-service"
  POSTGRES_PORT: "5432"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  MINIO_ENDPOINT: "minio-service:9000"
  MINIO_BUCKET_NAME: "pronas-pcd-documents"
  MINIO_SECURE: "false"
  PROMETHEUS_ENABLED: "true"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
  namespace: pronas-pcd
data:
  NODE_ENV: "production"
  NEXT_PUBLIC_API_URL: "https://pronas-pcd.gov.br"
  NEXT_PUBLIC_APP_URL: "https://pronas-pcd.gov.br"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: pronas-pcd
data:
  nginx.conf: |
    events {
        worker_connections 1024;
    }
    http {
        include /etc/nginx/mime.types;
        default_type application/octet-stream;
        
        log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
        
        access_log /var/log/nginx/access.log main;
        error_log /var/log/nginx/error.log warn;
        
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        client_max_body_size 100M;
        
        gzip on;
        gzip_vary on;
        gzip_proxied any;
        gzip_comp_level 6;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
        
        upstream backend {
            server backend-service:8000;
        }
        
        upstream frontend {
            server frontend-service:3000;
        }
        
        server {
            listen 80;
            server_name _;
            
            location / {
                proxy_pass http://frontend;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
            
            location /api/ {
                proxy_pass http://backend;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
            
            location /health {
                proxy_pass http://backend/health;
                access_log off;
            }
        }
    }
EOF

# Secrets template
cat > infra/k8s/base/secrets.yaml << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
  namespace: pronas-pcd
type: Opaque
data:
  # Base64 encoded values - UPDATE THESE
  POSTGRES_DB: cHJvbmFzX3BjZF9wcm9k  # pronas_pcd_prod
  POSTGRES_USER: cHJvbmFzX3VzZXI=  # pronas_user
  POSTGRES_PASSWORD: Q0hBTkdFX01FX1BBU1NXT1JE  # CHANGE_ME_PASSWORD
---
apiVersion: v1
kind: Secret
metadata:
  name: redis-secret
  namespace: pronas-pcd
type: Opaque
data:
  REDIS_PASSWORD: Q0hBTkdFX01FX1JFRElTX1BBU1NXT1JE  # CHANGE_ME_REDIS_PASSWORD
---
apiVersion: v1
kind: Secret
metadata:
  name: jwt-secret
  namespace: pronas-pcd
type: Opaque
data:
  JWT_SECRET_KEY: Q0hBTkdFX01FX0pXVF9TRUNSRVRfS0VZ  # CHANGE_ME_JWT_SECRET_KEY
  JWT_REFRESH_SECRET_KEY: Q0hBTkdFX01FX0pXVF9SRUZSRVNIX1NFQ1JFVF9LRVk=  # CHANGE_ME_JWT_REFRESH_SECRET_KEY
---
apiVersion: v1
kind: Secret
metadata:
  name: minio-secret
  namespace: pronas-pcd
type: Opaque
data:
  MINIO_ACCESS_KEY: Q0hBTkdFX01FX01JTklPX0FDQ0VTUw==  # CHANGE_ME_MINIO_ACCESS
  MINIO_SECRET_KEY: Q0hBTkdFX01FX01JTklPX1NFQ1JFVA==  # CHANGE_ME_MINIO_SECRET
EOF

echo "✅ ConfigMaps e Secrets criados!"

echo "📝 Criando Persistent Volumes..."

# Persistent Volumes
cat > infra/k8s/base/persistent-volumes.yaml << 'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
  labels:
    app: postgres
spec:
  capacity:
    storage: 20Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  hostPath:
    path: /data/pronas-pcd/postgres
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: pronas-pcd
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: local-storage
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: redis-pv
  labels:
    app: redis
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  hostPath:
    path: /data/pronas-pcd/redis
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: pronas-pcd
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: local-storage
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: minio-pv
  labels:
    app: minio
spec:
  capacity:
    storage: 50Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  hostPath:
    path: /data/pronas-pcd/minio
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-pvc
  namespace: pronas-pcd
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: local-storage
EOF

echo "✅ Persistent Volumes criados!"

echo "📝 Criando Deployments..."

# Database Deployment
mkdir -p infra/k8s/apps
cat > infra/k8s/apps/postgres.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: pronas-pcd
  labels:
    app: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        envFrom:
        - secretRef:
            name: database-secret
        env:
        - name: POSTGRES_INITDB_ARGS
          value: "--auth-host=scram-sha-256"
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        ports:
        - containerPort: 5432
          name: postgres
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - $(POSTGRES_USER)
            - -d
            - $(POSTGRES_DB)
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - $(POSTGRES_USER)
            - -d
            - $(POSTGRES_DB)
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: pronas-pcd
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
EOF

# Redis Deployment
cat > infra/k8s/apps/redis.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: pronas-pcd
  labels:
    app: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - --requirepass
        - $(REDIS_PASSWORD)
        - --maxmemory
        - 512mb
        - --maxmemory-policy
        - allkeys-lru
        envFrom:
        - secretRef:
            name: redis-secret
        ports:
        - containerPort: 6379
          name: redis
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: pronas-pcd
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
EOF

# MinIO Deployment
cat > infra/k8s/apps/minio.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
  namespace: pronas-pcd
  labels:
    app: minio
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
      - name: minio
        image: minio/minio:latest
        command:
        - minio
        - server
        - /data
        - --console-address
        - ":9001"
        envFrom:
        - secretRef:
            name: minio-secret
        env:
        - name: MINIO_ROOT_USER
          valueFrom:
            secretKeyRef:
              name: minio-secret
              key: MINIO_ACCESS_KEY
        - name: MINIO_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: minio-secret
              key: MINIO_SECRET_KEY
        ports:
        - containerPort: 9000
          name: api
        - containerPort: 9001
          name: console
        volumeMounts:
        - name: minio-storage
          mountPath: /data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /minio/health/live
            port: 9000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /minio/health/ready
            port: 9000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: minio-storage
        persistentVolumeClaim:
          claimName: minio-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: minio-service
  namespace: pronas-pcd
spec:
  selector:
    app: minio
  ports:
  - name: api
    port: 9000
    targetPort: 9000
  - name: console
    port: 9001
    targetPort: 9001
  type: ClusterIP
EOF

# Backend Deployment
cat > infra/k8s/apps/backend.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: pronas-pcd
  labels:
    app: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: pronas-pcd-backend:latest
        imagePullPolicy: Never  # For local development
        envFrom:
        - configMapRef:
            name: backend-config
        - secretRef:
            name: database-secret
        - secretRef:
            name: redis-secret
        - secretRef:
            name: jwt-secret
        - secretRef:
            name: minio-secret
        ports:
        - containerPort: 8000
          name: http
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: pronas-pcd
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
EOF

# Frontend Deployment
cat > infra/k8s/apps/frontend.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: pronas-pcd
  labels:
    app: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: pronas-pcd-frontend:latest
        imagePullPolicy: Never  # For local development
        envFrom:
        - configMapRef:
            name: frontend-config
        ports:
        - containerPort: 3000
          name: http
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: pronas-pcd
spec:
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
EOF

# Nginx Deployment
cat > infra/k8s/apps/nginx.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: pronas-pcd
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25-alpine
        ports:
        - containerPort: 80
          name: http
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-config
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: pronas-pcd
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
EOF

echo "✅ Deployments criados!"

echo "📝 Criando Ingress..."

# Ingress
mkdir -p infra/k8s/ingress
cat > infra/k8s/ingress/ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pronas-pcd-ingress
  namespace: pronas-pcd
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/rate-limit: "10"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - pronas-pcd.gov.br
    secretName: pronas-pcd-tls
  rules:
  - host: pronas-pcd.gov.br
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
EOF

echo "✅ Ingress criado!"

echo "📝 Criando scripts de deploy Kubernetes..."

# Kubernetes deployment script
cat > scripts/deploy-k8s.sh << 'EOF'
#!/bin/bash

set -e

echo "🚀 Deploying PRONAS/PCD to Kubernetes"
echo "====================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${2}${1}${NC}"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_status "❌ kubectl is not installed" $RED
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    print_status "❌ Cannot connect to Kubernetes cluster" $RED
    exit 1
fi

print_status "✅ Kubernetes cluster is accessible" $GREEN

# Apply namespace first
print_status "📝 Creating namespace..." $YELLOW
kubectl apply -f infra/k8s/base/namespace.yaml

# Apply persistent volumes
print_status "💾 Creating persistent volumes..." $YELLOW
kubectl apply -f infra/k8s/base/persistent-volumes.yaml

# Apply configmaps and secrets
print_status "🔧 Applying configurations..." $YELLOW
kubectl apply -f infra/k8s/base/configmaps.yaml

print_status "⚠️ Please update secrets before applying:" $YELLOW
print_status "Edit infra/k8s/base/secrets.yaml with real base64 encoded values" $YELLOW
read -p "Press enter when secrets are updated..."

kubectl apply -f infra/k8s/base/secrets.yaml

# Deploy database first
print_status "🗄️ Deploying PostgreSQL..." $YELLOW
kubectl apply -f infra/k8s/apps/postgres.yaml

# Wait for database to be ready
print_status "⏳ Waiting for PostgreSQL to be ready..." $YELLOW
kubectl wait --for=condition=available --timeout=300s deployment/postgres -n pronas-pcd

# Deploy Redis
print_status "🔴 Deploying Redis..." $YELLOW
kubectl apply -f infra/k8s/apps/redis.yaml

# Wait for Redis to be ready
print_status "⏳ Waiting for Redis to be ready..." $YELLOW
kubectl wait --for=condition=available --timeout=300s deployment/redis -n pronas-pcd

# Deploy MinIO
print_status "🪣 Deploying MinIO..." $YELLOW
kubectl apply -f infra/k8s/apps/minio.yaml

# Wait for MinIO to be ready
print_status "⏳ Waiting for MinIO to be ready..." $YELLOW
kubectl wait --for=condition=available --timeout=300s deployment/minio -n pronas-pcd

# Build and deploy backend
print_status "🏗️ Building backend image..." $YELLOW
docker build -t pronas-pcd-backend:latest ./backend

print_status "🚀 Deploying backend..." $YELLOW
kubectl apply -f infra/k8s/apps/backend.yaml

# Wait for backend to be ready
print_status "⏳ Waiting for backend to be ready..." $YELLOW
kubectl wait --for=condition=available --timeout=300s deployment/backend -n pronas-pcd

# Run database migrations
print_status "🗄️ Running database migrations..." $YELLOW
kubectl exec -n pronas-pcd deployment/backend -- alembic upgrade head

# Build and deploy frontend
print_status "🏗️ Building frontend image..." $YELLOW
docker build -t pronas-pcd-frontend:latest ./frontend

print_status "🎨 Deploying frontend..." $YELLOW
kubectl apply -f infra/k8s/apps/frontend.yaml

# Wait for frontend to be ready
print_status "⏳ Waiting for frontend to be ready..." $YELLOW
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n pronas-pcd

# Deploy nginx
print_status "🌐 Deploying Nginx..." $YELLOW
kubectl apply -f infra/k8s/apps/nginx.yaml

# Wait for nginx to be ready
print_status "⏳ Waiting for Nginx to be ready..." $YELLOW
kubectl wait --for=condition=available --timeout=300s deployment/nginx -n pronas-pcd

# Apply ingress
print_status "🚪 Applying Ingress..." $YELLOW
kubectl apply -f infra/k8s/ingress/ingress.yaml

# Display status
print_status "📊 Deployment Status:" $YELLOW
kubectl get pods -n pronas-pcd

print_status "🎉 Kubernetes deployment completed!" $GREEN

# Get external IP
EXTERNAL_IP=$(kubectl get service nginx-service -n pronas-pcd -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -n "$EXTERNAL_IP" ]; then
    print_status "🌐 External IP: $EXTERNAL_IP" $GREEN
    print_status "Update your DNS to point pronas-pcd.gov.br to $EXTERNAL_IP" $YELLOW
else
    print_status "⏳ External IP is pending..." $YELLOW
fi
EOF

chmod +x scripts/deploy-k8s.sh

echo "✅ Scripts Kubernetes criados!"

echo ""
echo "🎉 LOTE 4 PARTE 2 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Kubernetes Manifests completos (Namespace, ConfigMaps, Secrets)"
echo "• Deployments para todos os serviços (PostgreSQL, Redis, MinIO, Backend, Frontend, Nginx)"
echo "• Persistent Volumes para armazenamento de dados"
echo "• Services para comunicação interna"
echo "• Ingress com SSL e rate limiting"
echo "• Scripts de deploy automatizado para Kubernetes"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 4 Parte 3 (CI/CD - GitHub Actions)"
echo "2. Configure um cluster Kubernetes"
echo "3. Execute: ./scripts/deploy-k8s.sh"
echo ""
echo "📊 Status:"
echo "• Lote 4.1: ✅ Docker Production + Nginx"
echo "• Lote 4.2: ✅ Kubernetes Manifests"
echo "• Lote 4.3: ⏳ CI/CD (próximo)"
echo "• Lote 4.4: ⏳ Monitoring"
echo "• Lote 4.5: ⏳ Final Scripts"
echo ""