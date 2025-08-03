#!/bin/bash

# Test WhatsApp Webhook Script
# Simulates Twilio WhatsApp webhook calls for testing

set -e

# Configuration
N8N_HOST="${N8N_HOST:-localhost}"
N8N_PORT="${N8N_PORT:-5678}"
WEBHOOK_PATH="webhook/whatsapp-webhook"

echo "🧪 WhatsApp Webhook Test Tool"
echo "============================="

# Test payloads for different commands
test_list_command() {
    echo "📁 Testing LIST command..."
    
    curl -X POST "http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "X-Twilio-Signature: test-signature" \
        -d "From=whatsapp:+1234567890&Body=LIST /ProjectX&MessageSid=test123&AccountSid=test"
    
    echo -e "\n✅ LIST command test sent"
}

test_delete_command() {
    echo "🗑️ Testing DELETE command..."
    
    curl -X POST "http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "X-Twilio-Signature: test-signature" \
        -d "From=whatsapp:+1234567890&Body=DELETE /ProjectX/test.pdf CONFIRM&MessageSid=test124&AccountSid=test"
    
    echo -e "\n✅ DELETE command test sent"
}

test_move_command() {
    echo "📂 Testing MOVE command..."
    
    curl -X POST "http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "X-Twilio-Signature: test-signature" \
        -d "From=whatsapp:+1234567890&Body=MOVE /ProjectX/test.pdf /Archive&MessageSid=test125&AccountSid=test"
    
    echo -e "\n✅ MOVE command test sent"
}

test_summary_command() {
    echo "📄 Testing SUMMARY command..."
    
    curl -X POST "http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "X-Twilio-Signature: test-signature" \
        -d "From=whatsapp:+1234567890&Body=SUMMARY /ProjectX&MessageSid=test126&AccountSid=test"
    
    echo -e "\n✅ SUMMARY command test sent"
}

test_help_command() {
    echo "❓ Testing HELP command..."
    
    curl -X POST "http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "X-Twilio-Signature: test-signature" \
        -d "From=whatsapp:+1234567890&Body=HELP&MessageSid=test127&AccountSid=test"
    
    echo -e "\n✅ HELP command test sent"
}

test_invalid_command() {
    echo "❌ Testing invalid command..."
    
    curl -X POST "http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "X-Twilio-Signature: test-signature" \
        -d "From=whatsapp:+1234567890&Body=INVALID&MessageSid=test128&AccountSid=test"
    
    echo -e "\n✅ Invalid command test sent"
}

# Check if n8n is running
check_n8n_status() {
    echo "🔍 Checking n8n status..."
    
    if ! curl -s "http://$N8N_HOST:$N8N_PORT/healthz" > /dev/null 2>&1; then
        echo "❌ n8n is not accessible at http://$N8N_HOST:$N8N_PORT"
        echo "Make sure n8n is running: docker-compose up -d"
        exit 1
    fi
    
    echo "✅ n8n is running"
}

# Run all tests
run_all_tests() {
    echo "🚀 Running all webhook tests..."
    echo ""
    
    test_help_command
    sleep 2
    
    test_list_command
    sleep 2
    
    test_delete_command
    sleep 2
    
    test_move_command
    sleep 2
    
    test_summary_command
    sleep 2
    
    test_invalid_command
    
    echo ""
    echo "🎉 All tests completed!"
    echo "Check n8n execution logs for results"
}

# Show webhook info
show_webhook_info() {
    echo "📡 Webhook Information"
    echo "====================="
    echo "URL: http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH"
    echo "Method: POST"
    echo "Content-Type: application/x-www-form-urlencoded"
    echo ""
    echo "Required Headers:"
    echo "- X-Twilio-Signature (for signature verification)"
    echo ""
    echo "Twilio Payload Format:"
    echo "- From: whatsapp:+1234567890"
    echo "- Body: Command text"
    echo "- MessageSid: Unique message ID"
    echo "- AccountSid: Twilio account ID"
}

# Show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  list      Test LIST command"
    echo "  delete    Test DELETE command"
    echo "  move      Test MOVE command"
    echo "  summary   Test SUMMARY command"
    echo "  help      Test HELP command"
    echo "  invalid   Test invalid command"
    echo "  all       Run all tests"
    echo "  info      Show webhook information"
    echo ""
    echo "Examples:"
    echo "  $0 all      Run all tests"
    echo "  $0 list     Test only LIST command"
    echo "  $0 info     Show webhook details"
}

# Main execution
main() {
    check_n8n_status
    
    case "${1:-all}" in
        list)
            test_list_command
            ;;
        delete)
            test_delete_command
            ;;
        move)
            test_move_command
            ;;
        summary)
            test_summary_command
            ;;
        help)
            test_help_command
            ;;
        invalid)
            test_invalid_command
            ;;
        all)
            run_all_tests
            ;;
        info)
            show_webhook_info
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"