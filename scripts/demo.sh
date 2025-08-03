#!/bin/bash

# WhatsApp Drive Assistant Demo Script
# Demonstrates all features with simulated WhatsApp interactions

set -e

# Configuration
N8N_HOST="${N8N_HOST:-localhost}"
N8N_PORT="${N8N_PORT:-5678}"
WEBHOOK_PATH="webhook/whatsapp-webhook"
DEMO_PHONE="+1234567890"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🎬 WhatsApp Drive Assistant Demo${NC}"
echo -e "${CYAN}====================================${NC}"
echo ""

# Check if n8n is running
check_n8n_status() {
    echo -e "${BLUE}🔍 Checking n8n status...${NC}"
    
    if ! curl -s "http://$N8N_HOST:$N8N_PORT/healthz" > /dev/null 2>&1; then
        echo -e "${RED}❌ n8n is not accessible at http://$N8N_HOST:$N8N_PORT${NC}"
        echo -e "${YELLOW}Make sure n8n is running: docker-compose up -d${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ n8n is running${NC}"
    echo ""
}

# Simulate WhatsApp message
send_whatsapp_message() {
    local message="$1"
    local description="$2"
    
    echo -e "${PURPLE}📱 WhatsApp User: ${message}${NC}"
    echo -e "${BLUE}   ${description}${NC}"
    echo ""
    
    # Send webhook request
    response=$(curl -s -X POST "http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "X-Twilio-Signature: demo-signature" \
        -d "From=whatsapp:${DEMO_PHONE}&Body=${message}&MessageSid=demo$(date +%s)&AccountSid=demo")
    
    echo -e "${GREEN}🤖 Assistant: Processing your request...${NC}"
    echo ""
    sleep 2
}

# Demo scenario
run_demo_scenario() {
    echo -e "${CYAN}📋 Demo Scenario: Managing Project Files${NC}"
    echo -e "${CYAN}=====================================${NC}"
    echo ""
    echo -e "${YELLOW}In this demo, we'll simulate a user managing their Google Drive files${NC}"
    echo -e "${YELLOW}through WhatsApp messages. The assistant will respond to each command.${NC}"
    echo ""
    read -p "Press Enter to start the demo..."
    echo ""
    
    # 1. Help Command
    echo -e "${CYAN}📖 Step 1: Getting Help${NC}"
    echo -e "${CYAN}----------------------${NC}"
    send_whatsapp_message "HELP" "User wants to see available commands"
    
    # 2. List Files
    echo -e "${CYAN}📁 Step 2: Listing Files${NC}"
    echo -e "${CYAN}-----------------------${NC}"
    send_whatsapp_message "LIST /ProjectX" "User wants to see files in ProjectX folder"
    
    # 3. Get Document Summary
    echo -e "${CYAN}📄 Step 3: Getting Document Summaries${NC}"
    echo -e "${CYAN}------------------------------------${NC}"
    send_whatsapp_message "SUMMARY /ProjectX" "User wants AI summaries of documents"
    
    # 4. Move File
    echo -e "${CYAN}📂 Step 4: Moving a File${NC}"
    echo -e "${CYAN}-----------------------${NC}"
    send_whatsapp_message "MOVE /ProjectX/report.pdf /Archive" "User wants to move a file to archive"
    
    # 5. Delete File (without confirmation)
    echo -e "${CYAN}🗑️ Step 5: Attempting to Delete (Safety Check)${NC}"
    echo -e "${CYAN}----------------------------------------------${NC}"
    send_whatsapp_message "DELETE /ProjectX/old-file.pdf" "User tries to delete without CONFIRM keyword"
    
    # 6. Delete File (with confirmation)
    echo -e "${CYAN}🗑️ Step 6: Deleting with Confirmation${NC}"
    echo -e "${CYAN}------------------------------------${NC}"
    send_whatsapp_message "DELETE /ProjectX/old-file.pdf CONFIRM" "User deletes file with proper confirmation"
    
    # 7. Invalid Command
    echo -e "${CYAN}❌ Step 7: Invalid Command${NC}"
    echo -e "${CYAN}-------------------------${NC}"
    send_whatsapp_message "INVALID COMMAND" "User sends an unrecognized command"
    
    echo -e "${GREEN}🎉 Demo completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📊 What happened behind the scenes:${NC}"
    echo -e "${YELLOW}• Each message was processed by the n8n workflow${NC}"
    echo -e "${YELLOW}• Commands were validated and parsed${NC}"
    echo -e "${YELLOW}• Google Drive operations were simulated${NC}"
    echo -e "${YELLOW}• AI summaries would be generated for real documents${NC}"
    echo -e "${YELLOW}• All operations would be logged to Google Sheets${NC}"
    echo -e "${YELLOW}• Responses would be sent back via Twilio WhatsApp API${NC}"
    echo ""
}

# Interactive mode
run_interactive_demo() {
    echo -e "${CYAN}🎮 Interactive Demo Mode${NC}"
    echo -e "${CYAN}========================${NC}"
    echo ""
    echo -e "${YELLOW}Enter WhatsApp messages to test the assistant.${NC}"
    echo -e "${YELLOW}Type 'quit' to exit, 'help' for available commands.${NC}"
    echo ""
    
    while true; do
        echo -e "${PURPLE}📱 Enter message: ${NC}"
        read -r message
        
        case "$message" in
            "quit"|"exit"|"q")
                echo -e "${GREEN}👋 Demo ended. Thanks for trying the WhatsApp Drive Assistant!${NC}"
                break
                ;;
            "help"|"HELP")
                echo -e "${BLUE}Available commands:${NC}"
                echo -e "${BLUE}• LIST /folder - List files in folder${NC}"
                echo -e "${BLUE}• DELETE /path/file CONFIRM - Delete file${NC}"
                echo -e "${BLUE}• MOVE /source/file /destination - Move file${NC}"
                echo -e "${BLUE}• SUMMARY /folder - Get AI summaries${NC}"
                echo -e "${BLUE}• HELP - Show help message${NC}"
                echo ""
                ;;
            "")
                continue
                ;;
            *)
                send_whatsapp_message "$message" "Testing user command"
                ;;
        esac
    done
}

# Show demo options
show_demo_menu() {
    echo -e "${CYAN}🎯 Demo Options${NC}"
    echo -e "${CYAN}===============${NC}"
    echo ""
    echo -e "${YELLOW}1. Full Scenario Demo - Automated demonstration of all features${NC}"
    echo -e "${YELLOW}2. Interactive Mode - Test commands manually${NC}"
    echo -e "${YELLOW}3. Performance Test - Send multiple requests${NC}"
    echo -e "${YELLOW}4. Exit${NC}"
    echo ""
    echo -e "${PURPLE}Choose an option (1-4): ${NC}"
    read -r choice
    
    case $choice in
        1)
            run_demo_scenario
            ;;
        2)
            run_interactive_demo
            ;;
        3)
            run_performance_test
            ;;
        4)
            echo -e "${GREEN}👋 Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid option. Please choose 1-4.${NC}"
            show_demo_menu
            ;;
    esac
}

# Performance test
run_performance_test() {
    echo -e "${CYAN}⚡ Performance Test${NC}"
    echo -e "${CYAN}==================${NC}"
    echo ""
    echo -e "${YELLOW}This test will send multiple requests to test the system's performance.${NC}"
    echo -e "${YELLOW}Number of requests to send (1-20): ${NC}"
    read -r num_requests
    
    if [[ ! "$num_requests" =~ ^[0-9]+$ ]] || [ "$num_requests" -lt 1 ] || [ "$num_requests" -gt 20 ]; then
        echo -e "${RED}❌ Invalid number. Using default of 5 requests.${NC}"
        num_requests=5
    fi
    
    echo -e "${BLUE}🚀 Sending $num_requests requests...${NC}"
    echo ""
    
    start_time=$(date +%s)
    
    for i in $(seq 1 $num_requests); do
        echo -e "${PURPLE}Request $i/$num_requests: HELP${NC}"
        curl -s -X POST "http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -H "X-Twilio-Signature: perf-test-$i" \
            -d "From=whatsapp:${DEMO_PHONE}&Body=HELP&MessageSid=perf$i&AccountSid=demo" > /dev/null
        sleep 0.5
    done
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo ""
    echo -e "${GREEN}✅ Performance test completed!${NC}"
    echo -e "${GREEN}   Requests: $num_requests${NC}"
    echo -e "${GREEN}   Duration: ${duration}s${NC}"
    echo -e "${GREEN}   Average: $(echo "scale=2; $duration/$num_requests" | bc)s per request${NC}"
    echo ""
}

# Show system information
show_system_info() {
    echo -e "${CYAN}💻 System Information${NC}"
    echo -e "${CYAN}=====================${NC}"
    echo ""
    echo -e "${BLUE}n8n URL: http://$N8N_HOST:$N8N_PORT${NC}"
    echo -e "${BLUE}Webhook URL: http://$N8N_HOST:$N8N_PORT/$WEBHOOK_PATH${NC}"
    echo -e "${BLUE}Demo Phone: $DEMO_PHONE${NC}"
    echo ""
    
    # Check Docker status
    if command -v docker &> /dev/null; then
        echo -e "${BLUE}Docker Status:${NC}"
        if docker-compose ps 2>/dev/null | grep -q "Up"; then
            echo -e "${GREEN}  ✅ Docker containers are running${NC}"
        else
            echo -e "${YELLOW}  ⚠️  Docker containers may not be running${NC}"
        fi
    fi
    echo ""
}

# Main execution
main() {
    show_system_info
    check_n8n_status
    
    echo -e "${GREEN}🎉 Welcome to the WhatsApp Drive Assistant Demo!${NC}"
    echo ""
    echo -e "${YELLOW}This demo simulates WhatsApp interactions with the Google Drive assistant.${NC}"
    echo -e "${YELLOW}In a real deployment, responses would be sent back to WhatsApp users.${NC}"
    echo ""
    
    show_demo_menu
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Demo interrupted. Goodbye!${NC}"; exit 0' INT

# Run main function
main "$@"