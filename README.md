# WhatsApp-Driven Google Drive Assistant

A powerful n8n workflow that enables WhatsApp users to interact with Google Drive through simple text commands. The system provides file listing, deletion, moving, and AI-powered document summarization capabilities.

## 🚀 Features

- **WhatsApp Integration**: Uses Twilio Sandbox for WhatsApp messaging
- **Google Drive Operations**: List, delete, move files and folders
- **AI Summarization**: OpenAI GPT-4 powered document summaries
- **Security**: OAuth2 authentication with audit logging
- **Safety Guards**: Confirmation requirements for destructive operations

## 📋 Prerequisites

- n8n instance (local or cloud)
- Twilio account with WhatsApp Sandbox
- Google Cloud Project with Drive API enabled
- OpenAI API key
- Docker (for deployment)

## 🛠️ Setup Instructions

### 1. Twilio WhatsApp Sandbox Setup

1. Create a Twilio account at [twilio.com](https://www.twilio.com)
2. Navigate to WhatsApp Sandbox in Twilio Console
3. Note your Account SID and Auth Token
4. Set up webhook URL: `https://your-n8n-domain.com/webhook/twilio-whatsapp`

### 2. Google Cloud Setup

1. Create a Google Cloud Project
2. Enable Google Drive API
3. Create OAuth 2.0 credentials:
   - Go to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Add authorized redirect URIs for n8n
4. Download the JSON credentials file

### 3. OpenAI Setup

1. Create an OpenAI account at [openai.com](https://openai.com)
2. Generate an API key
3. Ensure you have GPT-4 access

### 4. Environment Variables

Create a `.env` file with the following variables:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886

# Google Drive Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-n8n-domain.com/callback

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Security
CONFIRMATION_KEYWORD=CONFIRM
AUDIT_SPREADSHEET_ID=your_audit_spreadsheet_id
```

## 📱 Command Syntax

### File Operations

| Command | Syntax | Example | Description |
|---------|--------|---------|-------------|
| LIST | `LIST /path` | `LIST /ProjectX` | List files in specified folder |
| DELETE | `DELETE /path/file` | `DELETE /ProjectX/report.pdf` | Delete specific file |
| MOVE | `MOVE /source /destination` | `MOVE /ProjectX/report.pdf /Archive` | Move file to new location |
| SUMMARY | `SUMMARY /path` | `SUMMARY /ProjectX` | Generate AI summary of documents |

### Safety Features

- **Confirmation Required**: Add `CONFIRM` to destructive commands
- **Example**: `DELETE /ProjectX/report.pdf CONFIRM`

### Help Commands

- `HELP` - Show available commands
- `HELP LIST` - Show LIST command details
- `HELP DELETE` - Show DELETE command details

## 🐳 Docker Deployment

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd watsapp

# Create environment file
cp .env.example .env
# Edit .env with your credentials

# Run with Docker Compose
docker-compose up -d
```

### Docker Compose Configuration

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_secure_password
      - WEBHOOK_URL=https://your-domain.com
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

volumes:
  n8n_data:
```

## 🔧 Workflow Import

1. Open n8n at `http://localhost:5678`
2. Go to Workflows
3. Click "Import from File"
4. Select `workflow.json` from this repository
5. Configure the credentials as prompted

## 📊 Audit Logging

The system maintains an audit log in Google Sheets with the following information:
- Timestamp
- User WhatsApp number
- Command executed
- Result status
- Error messages (if any)

## 🔒 Security Features

- **OAuth2 Authentication**: Secure Google Drive access
- **Command Validation**: Input sanitization and validation
- **Confirmation Requirements**: Destructive operations require confirmation
- **Audit Trail**: All operations are logged
- **Rate Limiting**: Prevents abuse

## 🚨 Error Handling

The system provides clear error messages for:
- Invalid commands
- File not found
- Permission denied
- Network errors
- API rate limits

## 📈 Monitoring

Monitor the workflow through:
- n8n execution history
- Google Sheets audit log
- Twilio webhook logs
- OpenAI API usage dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review n8n documentation
3. Open an issue on GitHub

## 🔄 Updates

- **v1.0.0**: Initial release with basic operations
- **v1.1.0**: Added AI summarization
- **v1.2.0**: Enhanced security and audit logging 