# Production Deployment Guide

This guide covers deploying the WhatsApp Drive Assistant in production environments with proper security, monitoring, and scalability considerations.

## Prerequisites

- Docker and Docker Compose
- Domain name with SSL certificate
- Google Cloud Platform account
- Twilio account with WhatsApp Business API
- OpenAI API account
- Production-grade database (PostgreSQL recommended)

## Production Architecture

```
Internet → Load Balancer → Nginx → n8n → Google Drive API
    ↓                                ↓
WhatsApp ← Twilio API              OpenAI API
    ↓
Audit Logs → Google Sheets
```

## Environment Setup

### 1. Server Requirements

**Minimum Specifications:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB SSD
- Network: 100 Mbps

**Recommended Specifications:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: 1 Gbps

### 2. Domain and SSL

```bash
# Install Certbot for Let's Encrypt
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Production Environment File

Create `.env.production`:

```env
# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_production_password
N8N_HOST=your-domain.com
N8N_PORT=5678
N8N_PROTOCOL=https

# Database Configuration
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=postgres
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=secure_db_password

# Production Settings
NODE_ENV=production
EXECUTIONS_PROCESS=main
EXECUTIONS_MODE=queue
N8N_LOG_LEVEL=info
N8N_METRICS=true

# Security
N8N_SECURE_COOKIE=true
WEBHOOK_URL=https://your-domain.com
N8N_DISABLE_UI=false

# Google Drive API
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret
GOOGLE_REDIRECT_URI=https://your-domain.com/rest/oauth2-credential/callback

# Twilio Production
TWILIO_ACCOUNT_SID=your_production_twilio_account_sid
TWILIO_AUTH_TOKEN=your_production_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+your_production_number
TWILIO_WEBHOOK_URL=https://your-domain.com/webhook/whatsapp-webhook

# OpenAI Production
OPENAI_API_KEY=your_production_openai_api_key
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=1000

# Security Secrets
WEBHOOK_SECRET=generate_strong_32_char_secret
JWT_SECRET=generate_strong_32_char_jwt_secret

# Audit Logging
AUDIT_SPREADSHEET_ID=your_production_google_sheets_id

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=20
MAX_REQUESTS_PER_HOUR=200

# Production Safety
REQUIRE_DELETE_CONFIRMATION=true
MAX_FILES_PER_OPERATION=100
VERIFY_TWILIO_SIGNATURE=true
DEBUG_MODE=false
```

## Docker Compose Production Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: whatsapp-drive-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - n8n
    networks:
      - n8n-network

  n8n:
    image: n8nio/n8n:latest
    container_name: whatsapp-drive-n8n
    restart: unless-stopped
    environment:
      - N8N_BASIC_AUTH_ACTIVE=${N8N_BASIC_AUTH_ACTIVE}
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=${N8N_PORT}
      - N8N_PROTOCOL=${N8N_PROTOCOL}
      - DB_TYPE=${DB_TYPE}
      - DB_POSTGRESDB_HOST=${DB_POSTGRESDB_HOST}
      - DB_POSTGRESDB_PORT=${DB_POSTGRESDB_PORT}
      - DB_POSTGRESDB_DATABASE=${DB_POSTGRESDB_DATABASE}
      - DB_POSTGRESDB_USER=${DB_POSTGRESDB_USER}
      - DB_POSTGRESDB_PASSWORD=${DB_POSTGRESDB_PASSWORD}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - GENERIC_TIMEZONE=UTC
      - N8N_LOG_LEVEL=${N8N_LOG_LEVEL}
      - N8N_METRICS=${N8N_METRICS}
      - EXECUTIONS_PROCESS=${EXECUTIONS_PROCESS}
      - EXECUTIONS_MODE=${EXECUTIONS_MODE}
      - N8N_SECURE_COOKIE=${N8N_SECURE_COOKIE}
    volumes:
      - n8n_data:/home/node/.n8n
      - ./workflow:/home/node/workflows:ro
    depends_on:
      - postgres
      - redis
    networks:
      - n8n-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    container_name: whatsapp-drive-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${DB_POSTGRESDB_DATABASE}
      - POSTGRES_USER=${DB_POSTGRESDB_USER}
      - POSTGRES_PASSWORD=${DB_POSTGRESDB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - n8n-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_POSTGRESDB_USER} -d ${DB_POSTGRESDB_DATABASE}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: whatsapp-drive-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - n8n-network
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: whatsapp-drive-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - n8n-network
    profiles:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: whatsapp-drive-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secure_grafana_password
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana-dashboard.json:/etc/grafana/provisioning/dashboards/dashboard.json:ro
    networks:
      - n8n-network
    profiles:
      - monitoring

volumes:
  n8n_data:
    driver: local
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  n8n-network:
    driver: bridge
```

## Nginx Configuration

Create `nginx/nginx.prod.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream n8n {
        server n8n:5678;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=webhook:10m rate=30r/m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Webhook endpoint with higher rate limit
        location /webhook/ {
            limit_req zone=webhook burst=10 nodelay;
            proxy_pass http://n8n;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Main application
        location / {
            limit_req zone=api burst=5 nodelay;
            proxy_pass http://n8n;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Health check endpoint
        location /healthz {
            access_log off;
            proxy_pass http://n8n;
        }
    }
}
```

## Database Initialization

Create `postgres/init.sql`:

```sql
-- Create database if not exists
CREATE DATABASE n8n;

-- Create user with limited privileges
CREATE USER n8n_user WITH PASSWORD 'secure_db_password';
GRANT ALL PRIVILEGES ON DATABASE n8n TO n8n_user;

-- Performance optimizations
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

## Deployment Process

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Application Deployment

```bash
# Clone repository
git clone <repository-url>
cd whatsapp-drive-assistant

# Set up environment
cp .env.sample .env.production
# Edit .env.production with production values

# Deploy with monitoring
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 3. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### 1. Application Metrics

Access Grafana at `https://your-domain.com:3000`:
- n8n execution metrics
- Webhook response times
- Error rates
- Resource utilization

### 2. Log Management

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f n8n

# Set up log rotation
sudo nano /etc/logrotate.d/docker-containers
```

### 3. Health Checks

```bash
# Create monitoring script
cat > /usr/local/bin/health-check.sh << 'EOF'
#!/bin/bash
curl -f https://your-domain.com/healthz || exit 1
EOF

chmod +x /usr/local/bin/health-check.sh

# Add to cron for monitoring
echo "*/5 * * * * /usr/local/bin/health-check.sh" | crontab -
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. System Hardening

```bash
# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Enable fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### 3. Container Security

```yaml
# Add to docker-compose.prod.yml
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp
```

## Backup Strategy

### 1. Database Backup

```bash
# Create backup script
cat > /usr/local/bin/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker-compose exec postgres pg_dump -U n8n n8n > $BACKUP_DIR/n8n_$DATE.sql
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-db.sh

# Schedule daily backups
echo "0 2 * * * /usr/local/bin/backup-db.sh" | crontab -
```

### 2. Application Backup

```bash
# Backup workflow and configuration
./scripts/backup-workflow.sh

# Schedule weekly backups
echo "0 3 * * 0 cd /path/to/app && ./scripts/backup-workflow.sh" | crontab -
```

## Scaling Considerations

### 1. Horizontal Scaling

For high-volume deployments:
- Use load balancer with multiple n8n instances
- Implement Redis for session storage
- Use managed PostgreSQL service

### 2. Performance Optimization

```env
# Production optimizations
EXECUTIONS_PROCESS=main
EXECUTIONS_MODE=queue
N8N_CONCURRENCY_PRODUCTION=10
```

## Troubleshooting

### Common Production Issues

1. **High Memory Usage**
   ```bash
   # Monitor resources
   docker stats
   
   # Increase memory limits
   deploy:
     resources:
       limits:
         memory: 2G
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connectivity
   docker-compose exec n8n nc -zv postgres 5432
   
   # Review connection pool settings
   DB_POSTGRESDB_POOL_SIZE=20
   ```

3. **SSL Certificate Issues**
   ```bash
   # Renew certificates
   sudo certbot renew
   
   # Check certificate status
   sudo certbot certificates
   ```

## Maintenance

### Regular Tasks

1. **Weekly**:
   - Review application logs
   - Check disk space usage
   - Verify backup integrity

2. **Monthly**:
   - Update Docker images
   - Review security patches
   - Analyze performance metrics

3. **Quarterly**:
   - Security audit
   - Capacity planning review
   - Disaster recovery testing

### Update Process

```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
./scripts/test-webhook.sh all
```

This deployment guide ensures a secure, scalable, and maintainable production environment for the WhatsApp Drive Assistant.