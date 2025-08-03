# Troubleshooting Guide

This guide helps you resolve common issues with the WhatsApp-Driven Google Drive Assistant.

## 🚨 Common Issues

### 1. Docker Issues

#### Problem: Docker not installed
**Symptoms:** `docker: command not found`
**Solution:**
```bash
# Install Docker Desktop
# Windows/Mac: Download from https://www.docker.com/products/docker-desktop
# Linux: Follow https://docs.docker.com/engine/install/
```

#### Problem: Docker Compose not found
**Symptoms:** `docker-compose: command not found`
**Solution:**
```bash
# Install Docker Compose
# Windows/Mac: Usually included with Docker Desktop
# Linux: Follow https://docs.docker.com/compose/install/
```

#### Problem: Port 5678 already in use
**Symptoms:** `Error starting userland proxy: listen tcp :5678: bind: address already in use`
**Solution:**
```bash
# Check what's using the port
lsof -i :5678  # Linux/Mac
netstat -ano | findstr :5678  # Windows

# Stop the conflicting service or change port in docker-compose.yml
```

### 2. Environment Configuration Issues

#### Problem: Missing environment variables
**Symptoms:** Setup script fails with validation errors
**Solution:**
1. Copy `env.example` to `.env`
2. Fill in all required variables:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI`
   - `OPENAI_API_KEY`

#### Problem: Invalid API keys
**Symptoms:** Authentication errors in logs
**Solution:**
- Verify API keys are correct and active
- Check account status and billing
- Ensure proper permissions are granted

### 3. Twilio Configuration Issues

#### Problem: WhatsApp webhook not receiving messages
**Symptoms:** No incoming messages in n8n
**Solution:**
1. Verify webhook URL in Twilio Console
2. Ensure URL is publicly accessible
3. Check webhook path: `/webhook/twilio-whatsapp`
4. Verify Twilio account is active

#### Problem: Twilio authentication errors
**Symptoms:** `401 Unauthorized` errors
**Solution:**
- Verify Account SID and Auth Token
- Check if credentials are from the correct environment (sandbox/production)
- Ensure account is not suspended

### 4. Google Drive Issues

#### Problem: OAuth2 authentication fails
**Symptoms:** `Invalid credentials` errors
**Solution:**
1. Verify OAuth2 credentials in Google Cloud Console
2. Check authorized redirect URIs
3. Ensure Google Drive API is enabled
4. Verify application is in correct environment (sandbox/production)

#### Problem: File operations fail
**Symptoms:** `File not found` or permission errors
**Solution:**
- Verify file paths are correct
- Check file permissions in Google Drive
- Ensure OAuth2 scope includes necessary permissions
- Verify file exists and is accessible

### 5. OpenAI Issues

#### Problem: API key authentication fails
**Symptoms:** `401 Unauthorized` from OpenAI
**Solution:**
- Verify API key is correct
- Check account billing status
- Ensure API key has necessary permissions
- Verify account is not suspended

#### Problem: Rate limiting
**Symptoms:** `429 Too Many Requests` errors
**Solution:**
- Implement rate limiting in workflow
- Check OpenAI usage limits
- Consider upgrading plan if needed

### 6. n8n Workflow Issues

#### Problem: Workflow import fails
**Symptoms:** Import errors or missing nodes
**Solution:**
1. Verify workflow.json is valid JSON
2. Check n8n version compatibility
3. Ensure all required nodes are available
4. Import manually through n8n interface

#### Problem: Credentials not working
**Symptoms:** Authentication errors in workflow execution
**Solution:**
1. Go to Settings > Credentials in n8n
2. Create new credentials for each service:
   - Google Drive OAuth2
   - Twilio Basic Auth
   - OpenAI API
   - Google Sheets OAuth2
3. Test each credential individually

#### Problem: Webhook not responding
**Symptoms:** 404 or timeout errors
**Solution:**
1. Verify webhook is active in n8n
2. Check webhook URL is correct
3. Ensure n8n is accessible from internet
4. Verify webhook path matches Twilio configuration

### 7. Performance Issues

#### Problem: Slow response times
**Symptoms:** Delayed WhatsApp responses
**Solution:**
- Check system resources (CPU, memory)
- Monitor API rate limits
- Optimize workflow execution
- Consider scaling up resources

#### Problem: Memory issues
**Symptoms:** Container crashes or slow performance
**Solution:**
```bash
# Increase Docker memory limits
# In Docker Desktop settings, increase memory allocation
# Or add to docker-compose.yml:
environment:
  - NODE_OPTIONS=--max-old-space-size=4096
```

### 8. Logging and Debugging

#### Problem: No logs visible
**Symptoms:** Can't see what's happening
**Solution:**
```bash
# View n8n logs
docker-compose logs -f n8n

# View all service logs
docker-compose logs -f

# Check specific service
docker-compose logs -f postgres
```

#### Problem: Debug workflow execution
**Symptoms:** Need to trace workflow steps
**Solution:**
1. Enable debug mode in n8n settings
2. Add debug nodes to workflow
3. Check execution history in n8n interface
4. Monitor real-time execution

## 🔧 Advanced Troubleshooting

### Database Issues

#### Problem: PostgreSQL connection fails
**Symptoms:** Database connection errors
**Solution:**
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# Reset database (WARNING: loses all data)
docker-compose down
docker volume rm watsapp_postgres_data
docker-compose up -d
```

### Network Issues

#### Problem: Services can't communicate
**Symptoms:** Connection timeouts between services
**Solution:**
```bash
# Check network connectivity
docker network ls
docker network inspect watsapp_n8n-network

# Restart network
docker-compose down
docker-compose up -d
```

### SSL/HTTPS Issues

#### Problem: SSL certificate errors
**Symptoms:** HTTPS connection failures
**Solution:**
1. Verify SSL certificate is valid
2. Check certificate chain
3. Ensure proper SSL configuration in nginx
4. Test with HTTP first, then upgrade to HTTPS

## 📊 Monitoring and Health Checks

### Health Check Commands

```bash
# Check service status
docker-compose ps

# Check resource usage
docker stats

# Check n8n health
curl http://localhost:5678/healthz

# Check database connectivity
docker-compose exec postgres pg_isready

# Check Redis connectivity
docker-compose exec redis redis-cli ping
```

### Performance Monitoring

```bash
# Monitor CPU and memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check disk usage
docker system df

# Monitor network traffic
docker-compose exec n8n netstat -i
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check logs:** `docker-compose logs -f n8n`
2. **Verify configuration:** Check all environment variables
3. **Test connectivity:** Verify all external services are accessible
4. **Check documentation:** Review README.md and this guide
5. **Search issues:** Check if problem is already documented

### Useful Debug Information

When reporting issues, include:

```bash
# System information
docker --version
docker-compose --version
uname -a

# Service status
docker-compose ps

# Recent logs
docker-compose logs --tail=100 n8n

# Environment (remove sensitive data)
cat .env | grep -v PASSWORD | grep -v KEY
```

### Support Channels

1. **GitHub Issues:** Create detailed issue with debug information
2. **n8n Community:** Ask in n8n Discord or forum
3. **Documentation:** Check n8n and service provider docs
4. **Stack Overflow:** Search for similar issues

## 🔄 Recovery Procedures

### Complete Reset

If all else fails, perform a complete reset:

```bash
# Stop all services
docker-compose down

# Remove all volumes (WARNING: loses all data)
docker-compose down -v

# Remove all images
docker system prune -a

# Start fresh
cp env.example .env
# Edit .env with your credentials
./scripts/setup.sh
```

### Backup and Restore

```bash
# Backup workflow
cp workflow.json workflow.json.backup

# Backup environment
cp .env .env.backup

# Restore from backup
cp workflow.json.backup workflow.json
cp .env.backup .env
```

## 📝 Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `docker: command not found` | Docker not installed | Install Docker Desktop |
| `Port already in use` | Conflicting service | Change port or stop service |
| `401 Unauthorized` | Invalid credentials | Check API keys |
| `404 Not Found` | Wrong webhook URL | Verify webhook configuration |
| `429 Too Many Requests` | Rate limiting | Implement rate limiting |
| `Connection refused` | Service not running | Check service status |
| `Permission denied` | File permissions | Check file access rights |

## 🎯 Quick Fixes

### Most Common Quick Fixes

1. **Restart services:** `docker-compose restart`
2. **Check logs:** `docker-compose logs -f n8n`
3. **Verify credentials:** Test each API key individually
4. **Clear cache:** `docker-compose down && docker-compose up -d`
5. **Update images:** `docker-compose pull && docker-compose up -d` 