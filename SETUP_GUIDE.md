# WhatsApp Google Drive Assistant - Setup Guide

## 🎯 Current Status
✅ **n8n is running** on http://localhost:5678  
✅ **Basic workflow is imported** and working  
✅ **Command parsing is functional**  

## 📋 Next Steps to Complete the Project

### 1. Configure API Credentials

#### A. Google Drive OAuth2 Setup
1. **Go to:** https://console.cloud.google.com/
2. **Create a new project** or select existing
3. **Enable Google Drive API**
4. **Create OAuth2 credentials:**
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:5678/callback`
5. **Note down:** Client ID and Client Secret

#### B. OpenAI API Setup
1. **Go to:** https://platform.openai.com/api-keys
2. **Create new API key**
3. **Note down:** API key

#### C. Twilio Setup
1. **Go to:** https://console.twilio.com/
2. **Get Account SID and Auth Token**
3. **Get WhatsApp Sandbox number**
4. **Note down:** Account SID, Auth Token, Phone Number

### 2. Configure n8n Credentials

#### A. Google Drive OAuth2
1. **In n8n:** Settings → Credentials
2. **Add new credential:** Google Drive OAuth2
3. **Enter:** Client ID and Client Secret from step 1A
4. **Test the connection**

#### B. OpenAI API
1. **In n8n:** Settings → Credentials
2. **Add new credential:** OpenAI API
3. **Enter:** API key from step 1B
4. **Test the connection**

#### C. Twilio Basic Auth
1. **In n8n:** Settings → Credentials
2. **Add new credential:** HTTP Basic Auth
3. **Username:** Your Twilio Account SID
4. **Password:** Your Twilio Auth Token
5. **Name:** "Twilio Basic Auth"

### 3. Configure Environment Variables

Update your `.env` file with:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_whatsapp_number

# Google Configuration
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5678/callback

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Security
CONFIRMATION_KEYWORD=CONFIRM
N8N_ENCRYPTION_KEY=your-32-character-encryption-key

# Audit Logging (Optional)
AUDIT_SPREADSHEET_ID=your_google_sheet_id
```

### 4. Test the System

#### A. Test Basic Commands
Send these WhatsApp messages to your Twilio number:
- `HELP` - Should show help message
- `LIST /test` - Should show Google Drive integration needed
- `DELETE /file.pdf` - Should show safety warning
- `DELETE /file.pdf CONFIRM` - Should show Google Drive integration needed

#### B. Test Twilio Webhook
1. **Get your webhook URL:** `http://localhost:5678/webhook/twilio-whatsapp`
2. **Configure in Twilio Console:**
   - Go to Twilio Console → Messaging → Settings → WhatsApp Sandbox
   - Set webhook URL to your n8n webhook URL
   - Set HTTP method to POST

### 5. Add Google Drive Integration

Once credentials are set up, we can add:
- **Google Drive List** node for LIST command
- **Google Drive Delete** node for DELETE command  
- **Google Drive Move** node for MOVE command

### 6. Add OpenAI Integration

Once credentials are set up, we can add:
- **OpenAI** node for SUMMARY command
- **Document processing** for PDF/DOCX files

### 7. Add Twilio Send Message

Once credentials are set up, we can add:
- **HTTP Request** node to send responses back to WhatsApp

## 🚀 Current Workflow Status

The current workflow successfully:
- ✅ Receives WhatsApp messages via Twilio webhook
- ✅ Parses commands (LIST, DELETE, MOVE, SUMMARY, HELP)
- ✅ Validates parameters and provides safety checks
- ✅ Returns appropriate responses
- ✅ Handles errors gracefully

## 🔧 Next Enhancement Steps

1. **Add Google Drive nodes** for file operations
2. **Add OpenAI nodes** for AI summarization
3. **Add Twilio send message** functionality
4. **Add audit logging** with Google Sheets
5. **Add error handling** and retry logic

## 📞 Support

If you encounter issues:
1. Check n8n logs: `docker-compose logs n8n`
2. Verify credentials are working
3. Test webhook connectivity
4. Check environment variables

---

**Ready to proceed with credential setup?** 