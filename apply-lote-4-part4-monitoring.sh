#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 4 - PARTE 4
# PRONAS/PCD System - Monitoring & Observability  
# Execute após aplicar as Partes 1, 2 e 3

set -e

echo "🚀 LOTE 4 PARTE 4: Monitoring & Observability"
echo "============================================="

if [ ! -d ".github/workflows" ]; then
    echo "❌ Execute as Partes 1, 2 e 3 primeiro."
    exit 1
fi

echo "📝 Criando stack de monitoramento..."

# Prometheus configuration
mkdir -p infra/monitoring/prometheus
cat > infra/monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'pronas-pcd-prod'
    environment: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - "rules/*.yml"

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Backend API metrics
  - job_name: 'pronas-pcd-backend'
    static_configs:
      - targets: ['backend-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s

  # Node exporter for system metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # PostgreSQL metrics
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis metrics
  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Nginx metrics
  - job_name: 'nginx-prometheus-exporter'
    static_configs:
      - targets: ['nginx-exporter:9113']

  # Docker/Container metrics
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 30s
EOF

# Prometheus rules
mkdir -p infra/monitoring/prometheus/rules
cat > infra/monitoring/prometheus/rules/alerts.yml << 'EOF'
groups:
  - name: pronas-pcd-alerts
    rules:
    # Application alerts
    - alert: BackendDown
      expr: up{job="pronas-pcd-backend"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "PRONAS/PCD Backend is down"
        description: "Backend service has been down for more than 1 minute"

    - alert: HighResponseTime
      expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="pronas-pcd-backend"}[5m])) > 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High response time detected"
        description: "95th percentile response time is {{ $value }}s"

    - alert: HighErrorRate
      expr: rate(http_requests_total{job="pronas-pcd-backend",status=~"5.."}[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value }} requests/second"

    # Database alerts
    - alert: PostgreSQLDown
      expr: up{job="postgres-exporter"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "PostgreSQL is down"
        description: "PostgreSQL database has been down for more than 1 minute"

    - alert: PostgreSQLTooManyConnections
      expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.8
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "PostgreSQL too many connections"
        description: "PostgreSQL has {{ $value }}% of connections used"

    - alert: PostgreSQLSlowQueries
      expr: pg_stat_activity_max_tx_duration > 60
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "PostgreSQL slow queries detected"
        description: "PostgreSQL has queries running longer than 60 seconds"

    # Redis alerts
    - alert: RedisDown
      expr: up{job="redis-exporter"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Redis is down"
        description: "Redis service has been down for more than 1 minute"

    - alert: RedisHighMemoryUsage
      expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Redis high memory usage"
        description: "Redis memory usage is {{ $value }}%"

    # System alerts
    - alert: HighCPUUsage
      expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High CPU usage detected"
        description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"

    - alert: HighMemoryUsage
      expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.85
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage detected"
        description: "Memory usage is {{ $value }}% on {{ $labels.instance }}"

    - alert: LowDiskSpace
      expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Low disk space"
        description: "Disk space is {{ $value }}% full on {{ $labels.instance }}"

    # Security alerts
    - alert: TooManyFailedLogins
      expr: increase(http_requests_total{job="pronas-pcd-backend",endpoint="/api/v1/auth/login",status="401"}[5m]) > 10
      for: 1m
      labels:
        severity: warning
      annotations:
        summary: "Too many failed login attempts"
        description: "{{ $value }} failed login attempts in the last 5 minutes"

    - alert: UnauthorizedAccess
      expr: increase(http_requests_total{job="pronas-pcd-backend",status="403"}[5m]) > 5
      for: 1m
      labels:
        severity: warning
      annotations:
        summary: "Unauthorized access attempts detected"
        description: "{{ $value }} unauthorized access attempts in the last 5 minutes"
EOF

# Alertmanager configuration
mkdir -p infra/monitoring/alertmanager
cat > infra/monitoring/alertmanager/alertmanager.yml << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@pronas-pcd.gov.br'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
    group_wait: 10s
    repeat_interval: 5m
  - match:
      severity: warning
    receiver: 'warning-alerts'
    repeat_interval: 1h

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://127.0.0.1:5001/'
    send_resolved: true

- name: 'critical-alerts'
  email_configs:
  - to: 'ops-critical@pronas-pcd.gov.br'
    subject: '[CRÍTICO] {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alerta: {{ .Annotations.summary }}
      Descrição: {{ .Annotations.description }}
      Severidade: {{ .Labels.severity }}
      Instância: {{ .Labels.instance }}
      Horário: {{ .StartsAt }}
      {{ end }}
  webhook_configs:
  - url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    send_resolved: true

- name: 'warning-alerts'
  email_configs:
  - to: 'ops-warning@pronas-pcd.gov.br'
    subject: '[AVISO] {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alerta: {{ .Annotations.summary }}
      Descrição: {{ .Annotations.description }}
      Severidade: {{ .Labels.severity }}
      {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
EOF

# Grafana dashboards
mkdir -p infra/monitoring/grafana/dashboards
cat > infra/monitoring/grafana/dashboards/pronas-pcd-overview.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "PRONAS/PCD - System Overview",
    "description": "Dashboard principal do sistema PRONAS/PCD",
    "tags": ["pronas-pcd", "overview"],
    "timezone": "America/Sao_Paulo",
    "panels": [
      {
        "id": 1,
        "title": "System Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"pronas-pcd-backend\"}",
            "legendFormat": "Backend"
          },
          {
            "expr": "up{job=\"postgres-exporter\"}",
            "legendFormat": "Database"
          },
          {
            "expr": "up{job=\"redis-exporter\"}",
            "legendFormat": "Redis"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{job=\"pronas-pcd-backend\"}[5m])",
            "legendFormat": "{{ method }} {{ status }}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4}
      },
      {
        "id": 3,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=\"pronas-pcd-backend\"}[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{job=\"pronas-pcd-backend\"}[5m]))",
            "legendFormat": "50th percentile"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4}
      },
      {
        "id": 4,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "Active connections"
          },
          {
            "expr": "pg_settings_max_connections",
            "legendFormat": "Max connections"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12}
      },
      {
        "id": 5,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "Memory usage %"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

# Grafana provisioning
mkdir -p infra/monitoring/grafana/provisioning/{datasources,dashboards}
cat > infra/monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

cat > infra/monitoring/grafana/provisioning/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'pronas-pcd'
    orgId: 1
    folder: 'PRONAS/PCD'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

echo "✅ Configurações de monitoramento criadas!"

echo "📝 Criando Docker Compose para monitoramento..."

# Monitoring Docker Compose
cat > docker-compose.monitoring.yml << 'EOF'
version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: pronas_pcd_prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./infra/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./infra/monitoring/prometheus/rules:/etc/prometheus/rules:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    networks:
      - monitoring_network
      - pronas_network

  # Alertmanager
  alertmanager:
    image: prom/alertmanager:latest
    container_name: pronas_pcd_alertmanager
    restart: unless-stopped
    ports:
      - "9093:9093"
    volumes:
      - ./infra/monitoring/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    networks:
      - monitoring_network

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: pronas_pcd_grafana
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SECURITY_DISABLE_GRAVATAR=true
      - GF_ANALYTICS_REPORTING_ENABLED=false
      - GF_ANALYTICS_CHECK_FOR_UPDATES=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./infra/monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./infra/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
    networks:
      - monitoring_network

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: pronas_pcd_node_exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring_network

  # PostgreSQL Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: pronas_pcd_postgres_exporter
    restart: unless-stopped
    ports:
      - "9187:9187"
    environment:
      - DATA_SOURCE_NAME=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}?sslmode=disable
    networks:
      - monitoring_network
      - pronas_network

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: pronas_pcd_redis_exporter
    restart: unless-stopped
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis://redis:6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    networks:
      - monitoring_network
      - pronas_network

  # cAdvisor for container metrics
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: pronas_pcd_cadvisor
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    networks:
      - monitoring_network

  # Nginx Prometheus Exporter
  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    container_name: pronas_pcd_nginx_exporter
    restart: unless-stopped
    ports:
      - "9113:9113"
    command:
      - -nginx.scrape-uri=http://nginx/nginx_status
    networks:
      - monitoring_network
      - pronas_network

volumes:
  prometheus_data:
    driver: local
  alertmanager_data:
    driver: local
  grafana_data:
    driver: local

networks:
  monitoring_network:
    driver: bridge
  pronas_network:
    external: true
EOF

echo "✅ Docker Compose de monitoramento criado!"

echo "📝 Criando Kubernetes manifests para monitoramento..."

# Prometheus Kubernetes deployment
mkdir -p infra/k8s/monitoring
cat > infra/k8s/monitoring/prometheus.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: pronas-pcd
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093
    
    scrape_configs:
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']
      
      - job_name: 'pronas-pcd-backend'
        static_configs:
          - targets: ['backend-service:8000']
        metrics_path: '/metrics'
      
      - job_name: 'postgres-exporter'
        static_configs:
          - targets: ['postgres-exporter:9187']
      
      - job_name: 'redis-exporter'
        static_configs:
          - targets: ['redis-exporter:9121']
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: pronas-pcd
  labels:
    app: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config-volume
          mountPath: /etc/prometheus
        - name: storage-volume
          mountPath: /prometheus
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: config-volume
        configMap:
          name: prometheus-config
      - name: storage-volume
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: pronas-pcd
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
  type: ClusterIP
EOF

# Grafana Kubernetes deployment
cat > infra/k8s/monitoring/grafana.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: pronas-pcd
  labels:
    app: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin123"
        - name: GF_USERS_ALLOW_SIGN_UP
          value: "false"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: grafana-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: pronas-pcd
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
EOF

echo "✅ Manifests Kubernetes de monitoramento criados!"

echo "📝 Criando scripts de monitoramento..."

# Monitoring setup script
cat > scripts/setup-monitoring.sh << 'EOF'
#!/bin/bash

set -e

echo "📊 Configurando Stack de Monitoramento PRONAS/PCD"
echo "=================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${2}${1}${NC}"
}

# Check if monitoring network exists
if ! docker network ls | grep -q "monitoring_network"; then
    print_status "🔗 Criando network de monitoramento..." $YELLOW
    docker network create monitoring_network
fi

# Load environment variables
if [ -f ".env.production" ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
    print_status "✅ Variáveis de ambiente carregadas" $GREEN
else
    print_status "❌ Arquivo .env.production não encontrado" $RED
    exit 1
fi

# Start monitoring stack
print_status "🚀 Iniciando stack de monitoramento..." $YELLOW
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
print_status "⏳ Aguardando serviços ficarem prontos..." $YELLOW
sleep 30

# Health checks
print_status "🏥 Verificando status dos serviços..." $YELLOW

# Check Prometheus
if curl -f -s http://localhost:9090/-/healthy > /dev/null; then
    print_status "✅ Prometheus está funcionando" $GREEN
else
    print_status "❌ Prometheus não está respondendo" $RED
fi

# Check Grafana
if curl -f -s http://localhost:3001/api/health > /dev/null; then
    print_status "✅ Grafana está funcionando" $GREEN
else
    print_status "❌ Grafana não está respondendo" $RED
fi

# Check Alertmanager
if curl -f -s http://localhost:9093/-/healthy > /dev/null; then
    print_status "✅ Alertmanager está funcionando" $GREEN
else
    print_status "❌ Alertmanager não está respondendo" $RED
fi

# Display service URLs
print_status "🌐 URLs dos Serviços:" $YELLOW
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3001 (admin/admin123)"
echo "- Alertmanager: http://localhost:9093"

print_status "📊 Stack de monitoramento configurado com sucesso!" $GREEN
EOF

chmod +x scripts/setup-monitoring.sh

# Log aggregation script
cat > scripts/collect-logs.sh << 'EOF'
#!/bin/bash

# Script para coletar logs do sistema PRONAS/PCD

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs/collected_$TIMESTAMP"

echo "📋 Coletando logs do sistema PRONAS/PCD"
echo "======================================="

# Create log directory
mkdir -p $LOG_DIR

# Collect Docker logs
echo "🐳 Coletando logs do Docker..."
docker-compose -f docker-compose.prod.yml logs --tail=1000 > $LOG_DIR/docker_logs.txt 2>&1

# Collect individual service logs
for service in backend frontend nginx postgres redis; do
    echo "📝 Coletando logs do $service..."
    docker-compose -f docker-compose.prod.yml logs --tail=1000 $service > $LOG_DIR/${service}_logs.txt 2>&1 || true
done

# Collect system logs (if available)
if command -v journalctl &> /dev/null; then
    echo "📋 Coletando logs do sistema..."
    journalctl --since "1 hour ago" > $LOG_DIR/system_logs.txt 2>&1 || true
fi

# Collect Kubernetes logs (if running on K8s)
if command -v kubectl &> /dev/null && kubectl cluster-info &> /dev/null; then
    echo "☸️ Coletando logs do Kubernetes..."
    mkdir -p $LOG_DIR/k8s
    
    # Get pod logs
    kubectl get pods -n pronas-pcd -o name | while read pod; do
        pod_name=$(basename $pod)
        kubectl logs -n pronas-pcd $pod --tail=1000 > $LOG_DIR/k8s/${pod_name}.log 2>&1 || true
    done
    
    # Get events
    kubectl get events -n pronas-pcd > $LOG_DIR/k8s/events.txt 2>&1 || true
fi

# Create archive
tar -czf logs_${TIMESTAMP}.tar.gz -C logs collected_$TIMESTAMP

echo "✅ Logs coletados em: logs_${TIMESTAMP}.tar.gz"
echo "📁 Diretório temporário: $LOG_DIR"
EOF

chmod +x scripts/collect-logs.sh

echo "✅ Scripts de monitoramento criados!"

echo ""
echo "🎉 LOTE 4 PARTE 4 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Stack completa de monitoramento (Prometheus, Grafana, Alertmanager)"
echo "• Alertas configurados para sistema, aplicação e segurança"
echo "• Exporters para PostgreSQL, Redis, Nginx e métricas de sistema"
echo "• Dashboards Grafana para visualização de métricas"
echo "• Docker Compose para monitoramento local"
echo "• Manifests Kubernetes para monitoramento em cluster"
echo "• Scripts para configuração e coleta de logs"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 4 Parte 5 (Final - Backup & Scripts finais)"
echo "2. Execute: ./scripts/setup-monitoring.sh"
echo "3. Configure notificações no Alertmanager"
echo ""
echo "📊 Status:"
echo "• Lote 4.1: ✅ Docker Production + Nginx"
echo "• Lote 4.2: ✅ Kubernetes Manifests"
echo "• Lote 4.3: ✅ CI/CD GitHub Actions"
echo "• Lote 4.4: ✅ Monitoring & Observability"
echo "• Lote 4.5: ⏳ Final Scripts (próximo)"
echo ""
echo "🌐 URLs de Monitoramento:"
echo "• Prometheus: http://localhost:9090"
echo "• Grafana: http://localhost:3001 (admin/admin123)"
echo "• Alertmanager: http://localhost:9093"
echo ""