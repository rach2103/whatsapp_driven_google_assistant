# WhatsApp-Driven Google Drive Assistant

A powerful n8n workflow that enables Google Drive management through WhatsApp messages using Twilio and AI-powered document summarization.

## Features

- 📱 **WhatsApp Integration**: Send commands via WhatsApp using Twilio Sandbox
- 📁 **Google Drive Operations**: List, delete, move files and folders
- 🤖 **AI Summarization**: Get intelligent summaries of documents using OpenAI GPT-4o
- 📊 **Audit Logging**: Complete audit trail in Google Sheets
- 🔒 **Security**: OAuth2 authentication and safety guards against accidental deletions
- 🐳 **Easy Deployment**: Docker-based setup with one-click import

## Supported Commands

Send these commands via WhatsApp:

- `LIST /ProjectX` - List all files in the /ProjectX folder
- `DELETE /ProjectX/report.pdf` - Delete a specific file (requires CONFIRM keyword)
- `MOVE /ProjectX/report.pdf /Archive` - Move file to another folder
- `SUMMARY /ProjectX` - Get AI-powered summaries of all documents in folder
- `HELP` - Show available commands

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Cloud Platform account
- Twilio account with WhatsApp Sandbox
- OpenAI API key

### 1. Clone Repository

```bash
git clone <repository-url>
cd whatsapp-drive-assistant
```

### 2. Environment Setup

```bash
cp .env.sample .env
# Edit .env with your credentials (see Configuration section)
```

### 3. Start n8n

```bash
docker-compose up -d
```

### 4. Import Workflow

1. Open http://localhost:5678
2. Go to Workflows → Import from File
3. Select `workflow/whatsapp-drive-assistant.json`
4. Configure credentials (see Configuration section)

## Configuration

### Google Drive Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:5678/rest/oauth2-credential/callback`
5. Download credentials JSON and note Client ID/Secret

### Twilio WhatsApp Setup

1. Sign up at [Twilio](https://www.twilio.com/)
2. Go to Console → Messaging → Try it out → Send a WhatsApp message
3. Join your sandbox by sending the code to the Twilio WhatsApp number
4. Note your Account SID, Auth Token, and WhatsApp number

### OpenAI Setup

1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to environment variables

### Environment Variables

Update `.env` with your credentials:

```env
# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_password

# Google Drive
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Webhook Security
WEBHOOK_SECRET=your_webhook_secret
```

## Workflow Architecture

The workflow consists of several key components:

1. **WhatsApp Webhook**: Receives messages from Twilio
2. **Command Parser**: Extracts and validates commands
3. **Google Drive Connector**: Handles all Drive operations
4. **AI Summarizer**: Processes documents for summaries
5. **Audit Logger**: Records all operations
6. **Response Handler**: Sends formatted replies back to WhatsApp

## Security Features

- **OAuth2 Authentication**: Secure Google Drive access
- **Webhook Validation**: Twilio signature verification
- **Deletion Confirmation**: Requires "CONFIRM" keyword for deletions
- **Audit Trail**: All operations logged with timestamps
- **Scoped Access**: Only operates within authenticated user's Drive

## Command Examples

### List Files
```
LIST /Projects
```
Response: Lists all files and folders in /Projects

### Delete File (with confirmation)
```
DELETE /Projects/old-report.pdf CONFIRM
```
Response: File deleted successfully and logged

### Move File
```
MOVE /Projects/report.pdf /Archive/2024
```
Response: File moved successfully

### Get Summaries
```
SUMMARY /Projects
```
Response: AI-generated bullet-point summaries of all documents

## Troubleshooting

### Common Issues

1. **Webhook not receiving messages**
   - Check Twilio webhook URL configuration
   - Verify n8n is accessible from internet (use ngrok for local testing)

2. **Google Drive authentication fails**
   - Ensure OAuth redirect URI matches exactly
   - Check Google Cloud Console API quotas

3. **AI summaries not working**
   - Verify OpenAI API key is valid
   - Check API usage limits

### Logs

Check n8n execution logs:
```bash
docker-compose logs n8n
```

## Development

### Local Development with ngrok

For local testing, expose n8n to the internet:

```bash
# Install ngrok
npm install -g ngrok

# Expose n8n
ngrok http 5678

# Update Twilio webhook URL with ngrok URL
```

### Workflow Modifications

1. Edit workflow in n8n interface
2. Export updated workflow
3. Replace `workflow/whatsapp-drive-assistant.json`

## File Structure

```
whatsapp-drive-assistant/
├── workflow/
│   └── whatsapp-drive-assistant.json    # Main n8n workflow
├── scripts/
│   ├── setup.sh                         # Setup script
│   └── backup-workflow.sh               # Workflow backup
├── docker-compose.yml                   # Docker configuration
├── .env.sample                          # Environment template
├── README.md                            # This file
└── docs/
    └── API.md                           # API documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create a GitHub issue
- Check the troubleshooting section
- Review n8n documentation

---

**Note**: This workflow handles sensitive data. Always follow security best practices and comply with your organization's data handling policies.