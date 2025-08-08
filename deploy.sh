#!/bin/bash

# Inspector Production Deployment Script
# Usage: ./deploy.sh [start|stop|restart|logs|status]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="inspector"
COMPOSE_FILE="docker-compose.prod.yml"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if required files exist
check_files() {
    local missing_files=()
    
    if [[ ! -f ".env" ]]; then
        missing_files+=(".env")
    fi
    
    if [[ ! -f "nginx.conf" ]]; then
        missing_files+=("nginx.conf")
    fi
    
    if [[ ! -d "ssl" ]]; then
        missing_files+=("ssl directory")
    fi
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        print_error "Missing required files/directories:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        print_warning "Please ensure all required files are present before deployment."
        exit 1
    fi
}

# Function to create SSL directory if it doesn't exist
setup_ssl() {
    if [[ ! -d "ssl" ]]; then
        print_warning "SSL directory not found. Creating..."
        mkdir -p ssl
        print_warning "Please add your SSL certificates to the ssl/ directory:"
        echo "  - ssl/brianchiu.top.crt (SSL certificate)"
        echo "  - ssl/brianchiu.top.key (SSL private key)"
        echo ""
        print_warning "You can obtain free SSL certificates from Let's Encrypt:"
        echo "  certbot certonly --standalone -d brianchiu.top -d www.brianchiu.top"
        exit 1
    fi
}

# Function to start services
start_services() {
    print_status "Starting Inspector services..."
    
    # Pull latest images
    docker-compose -f $COMPOSE_FILE pull
    
    # Build and start services
    docker-compose -f $COMPOSE_FILE up -d --build
    
    print_status "Services started successfully!"
    print_status "Application will be available at: https://brianchiu.top"
    print_status "Health check: https://brianchiu.top/health"
}

# Function to stop services
stop_services() {
    print_status "Stopping Inspector services..."
    docker-compose -f $COMPOSE_FILE down
    print_status "Services stopped successfully!"
}

# Function to restart services
restart_services() {
    print_status "Restarting Inspector services..."
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE up -d --build
    print_status "Services restarted successfully!"
}

# Function to show logs
show_logs() {
    print_status "Showing logs for Inspector services..."
    docker-compose -f $COMPOSE_FILE logs -f
}

# Function to show status
show_status() {
    print_status "Inspector services status:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    print_status "Service health checks:"
    docker-compose -f $COMPOSE_FILE exec -T inspector curl -f http://localhost:8000/health || print_error "Backend health check failed"
    docker-compose -f $COMPOSE_FILE exec -T db pg_isready -U inspector || print_error "Database health check failed"
}

# Function to backup database
backup_database() {
    local backup_dir="backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="${backup_dir}/inspector_backup_${timestamp}.sql"
    
    mkdir -p $backup_dir
    
    print_status "Creating database backup..."
    docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U inspector inspector > "$backup_file"
    print_status "Database backup created: $backup_file"
}

# Function to update application
update_application() {
    print_status "Updating Inspector application..."
    
    # Pull latest code
    git pull origin main
    
    # Rebuild and restart services
    restart_services
    
    print_status "Application updated successfully!"
}

# Main script logic
case "${1:-}" in
    "start")
        check_docker
        check_files
        setup_ssl
        start_services
        ;;
    "stop")
        check_docker
        stop_services
        ;;
    "restart")
        check_docker
        check_files
        setup_ssl
        restart_services
        ;;
    "logs")
        check_docker
        show_logs
        ;;
    "status")
        check_docker
        show_status
        ;;
    "backup")
        check_docker
        backup_database
        ;;
    "update")
        check_docker
        check_files
        setup_ssl
        update_application
        ;;
    *)
        echo "Inspector Deployment Script"
        echo ""
        echo "Usage: $0 [start|stop|restart|logs|status|backup|update]"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Show service logs"
        echo "  status  - Show service status and health"
        echo "  backup  - Create database backup"
        echo "  update  - Update application from git and restart"
        echo ""
        echo "Prerequisites:"
        echo "  - Docker and Docker Compose installed"
        echo "  - .env file with configuration"
        echo "  - SSL certificates in ssl/ directory"
        echo "  - Domain brianchiu.top pointing to this server"
        ;;
esac
