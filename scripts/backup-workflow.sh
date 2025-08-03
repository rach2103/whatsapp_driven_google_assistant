#!/bin/bash

# Backup n8n Workflow Script
# Exports the current workflow from n8n

set -e

# Configuration
N8N_HOST="${N8N_HOST:-localhost}"
N8N_PORT="${N8N_PORT:-5678}"
N8N_USER="${N8N_BASIC_AUTH_USER:-admin}"
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "📦 n8n Workflow Backup Tool"
echo "============================"

# Create backup directory
mkdir -p "$BACKUP_DIR"

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

# Get credentials for backup
get_credentials() {
    echo "🔐 Getting authentication..."
    
    if [ -f .env ]; then
        source .env
        N8N_PASSWORD="$N8N_BASIC_AUTH_PASSWORD"
    fi
    
    if [ -z "$N8N_PASSWORD" ]; then
        echo "Enter n8n password:"
        read -s N8N_PASSWORD
    fi
}

# Export workflow
export_workflow() {
    echo "📤 Exporting workflow..."
    
    # Get workflow ID (assuming our workflow name)
    WORKFLOW_NAME="WhatsApp Drive Assistant"
    
    # Use n8n CLI through docker if available
    if docker-compose ps n8n | grep -q "Up"; then
        echo "Using Docker container to export..."
        
        # Export all workflows
        docker-compose exec n8n n8n export:workflow --all --output="/home/node/workflows/backup_${TIMESTAMP}.json"
        
        # Copy from container to host
        docker cp "$(docker-compose ps -q n8n):/home/node/workflows/backup_${TIMESTAMP}.json" "$BACKUP_DIR/"
        
        echo "✅ Workflow exported to $BACKUP_DIR/backup_${TIMESTAMP}.json"
    else
        echo "❌ n8n container not running"
        exit 1
    fi
}

# Create compressed backup
create_archive() {
    echo "🗜️  Creating compressed backup..."
    
    BACKUP_NAME="whatsapp-drive-assistant-backup-${TIMESTAMP}"
    
    # Create temporary directory for full backup
    mkdir -p "temp_backup/$BACKUP_NAME"
    
    # Copy workflow files
    cp workflow/*.json "temp_backup/$BACKUP_NAME/"
    cp "$BACKUP_DIR/backup_${TIMESTAMP}.json" "temp_backup/$BACKUP_NAME/"
    
    # Copy configuration files
    cp .env.sample "temp_backup/$BACKUP_NAME/"
    cp docker-compose.yml "temp_backup/$BACKUP_NAME/"
    cp README.md "temp_backup/$BACKUP_NAME/"
    
    # Copy scripts
    cp -r scripts "temp_backup/$BACKUP_NAME/"
    
    # Create archive
    cd temp_backup
    tar -czf "../$BACKUP_DIR/${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
    cd ..
    
    # Cleanup
    rm -rf temp_backup
    
    echo "✅ Full backup created: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
}

# List existing backups
list_backups() {
    echo "📋 Existing backups:"
    
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR)" ]; then
        ls -lah "$BACKUP_DIR"
    else
        echo "No backups found"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    echo "🧹 Cleaning up old backups (keeping last 5)..."
    
    if [ -d "$BACKUP_DIR" ]; then
        # Keep only the 5 most recent backup files
        ls -t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm -f
        ls -t "$BACKUP_DIR"/*.json 2>/dev/null | tail -n +6 | xargs -r rm -f
        
        echo "✅ Cleanup completed"
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -l, --list     List existing backups"
    echo "  -c, --cleanup  Cleanup old backups"
    echo "  -h, --help     Show this help"
    echo ""
    echo "Examples:"
    echo "  $0              Create new backup"
    echo "  $0 --list       List all backups"
    echo "  $0 --cleanup    Remove old backups"
}

# Main execution
main() {
    case "${1:-}" in
        -l|--list)
            list_backups
            ;;
        -c|--cleanup)
            cleanup_old_backups
            ;;
        -h|--help)
            show_usage
            ;;
        "")
            check_n8n_status
            get_credentials
            export_workflow
            create_archive
            cleanup_old_backups
            echo ""
            echo "🎉 Backup completed successfully!"
            echo "Backup file: $BACKUP_DIR/whatsapp-drive-assistant-backup-${TIMESTAMP}.tar.gz"
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"