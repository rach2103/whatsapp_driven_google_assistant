#!/bin/bash

# WhatsApp Drive Assistant Setup Script
# This script helps set up the entire environment

set -e

echo "🚀 WhatsApp Drive Assistant Setup"
echo "=================================="

# Check if required tools are installed
check_dependencies() {
    echo "📋 Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ All dependencies are installed"
}

# Create environment file if it doesn't exist
setup_environment() {
    echo "🔧 Setting up environment..."
    
    if [ ! -f .env ]; then
        cp .env.sample .env
        echo "📄 Created .env file from template"
        echo "⚠️  Please edit .env with your actual credentials before continuing"
        echo ""
        echo "Required credentials:"
        echo "- Google OAuth2 Client ID and Secret"
        echo "- Twilio Account SID and Auth Token"
        echo "- OpenAI API Key"
        echo "- Google Sheets ID for audit logging"
        echo ""
        read -p "Press Enter after updating .env file..."
    else
        echo "✅ .env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    echo "📁 Creating directories..."
    
    mkdir -p workflow scripts docs nginx/ssl
    mkdir -p data/n8n data/postgres data/redis
    
    echo "✅ Directories created"
}

# Generate webhook secret if not set
generate_secrets() {
    echo "🔐 Generating secrets..."
    
    if ! grep -q "WEBHOOK_SECRET=" .env || grep -q "your_random_webhook_secret_here" .env; then
        WEBHOOK_SECRET=$(openssl rand -hex 32)
        sed -i "s/your_random_webhook_secret_here/$WEBHOOK_SECRET/" .env
        echo "✅ Generated webhook secret"
    fi
    
    if ! grep -q "JWT_SECRET=" .env || grep -q "your_jwt_secret_for_session_management" .env; then
        JWT_SECRET=$(openssl rand -hex 32)
        sed -i "s/your_jwt_secret_for_session_management/$JWT_SECRET/" .env
        echo "✅ Generated JWT secret"
    fi
}

# Start services
start_services() {
    echo "🐳 Starting Docker services..."
    
    # Pull latest images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    echo "✅ Services started"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
}

# Wait for n8n to be ready
wait_for_n8n() {
    echo "⏳ Waiting for n8n to be ready..."
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:5678/healthz > /dev/null 2>&1; then
            echo "✅ n8n is ready!"
            break
        fi
        
        echo "   Attempt $attempt/$max_attempts - waiting..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ n8n failed to start within expected time"
        echo "Check logs with: docker-compose logs n8n"
        exit 1
    fi
}

# Import workflow
import_workflow() {
    echo "📥 Workflow import instructions:"
    echo ""
    echo "1. Open http://localhost:5678 in your browser"
    echo "2. Login with credentials from .env file"
    echo "3. Go to Workflows → Import from File"
    echo "4. Select 'workflow/whatsapp-drive-assistant.json'"
    echo "5. Configure the following credentials:"
    echo "   - Google Drive OAuth2 (google-drive-oauth)"
    echo "   - Google Sheets OAuth2 (google-sheets-oauth)"
    echo "   - OpenAI API (openai-api)"
    echo "   - Twilio Basic Auth (twilio-auth)"
    echo ""
    echo "📱 Twilio Webhook URL: http://localhost:5678/webhook/whatsapp-webhook"
    echo "   (Use ngrok for external access during development)"
}

# Create audit spreadsheet template
create_audit_template() {
    echo "📊 Creating audit log template..."
    
    cat > docs/audit-spreadsheet-template.md << 'EOF'
# Audit Log Spreadsheet Template

Create a Google Sheet with the following columns in the first row:

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Timestamp | From | Operation | Message | Status | Target | Count |

## Column Descriptions:
- **Timestamp**: When the operation occurred
- **From**: WhatsApp number that initiated the request
- **Operation**: Type of operation (list, delete, move, summary, help)
- **Message**: Original message or response sent
- **Status**: SUCCESS or FAILED
- **Target**: File/folder name or path
- **Count**: Number of items processed

## Setup Instructions:
1. Create a new Google Sheet
2. Add the column headers as shown above
3. Share the sheet with the Google account used for OAuth
4. Copy the spreadsheet ID from the URL
5. Add the ID to your .env file as AUDIT_SPREADSHEET_ID
EOF

    echo "✅ Audit template created in docs/audit-spreadsheet-template.md"
}

# Show final instructions
show_final_instructions() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "Next steps:"
    echo "1. Configure credentials in n8n interface"
    echo "2. Set up Twilio webhook URL"
    echo "3. Create audit spreadsheet (see docs/audit-spreadsheet-template.md)"
    echo "4. Test with WhatsApp commands"
    echo ""
    echo "Useful commands:"
    echo "- View logs: docker-compose logs -f n8n"
    echo "- Stop services: docker-compose down"
    echo "- Restart services: docker-compose restart"
    echo "- Backup workflow: ./scripts/backup-workflow.sh"
    echo ""
    echo "🌐 n8n Interface: http://localhost:5678"
    echo "📖 Documentation: README.md"
}

# Main execution
main() {
    check_dependencies
    setup_environment
    create_directories
    generate_secrets
    start_services
    wait_for_n8n
    create_audit_template
    import_workflow
    show_final_instructions
}

# Run main function
main "$@"