#!/bin/bash

# SSL Certificate Renewal Script for Inspector
# This script automatically renews Let's Encrypt certificates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/path/to/your/inspector"  # Update this path
DOMAIN="brianchiu.top"
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

# Function to check if script is run as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check if certbot is installed
check_certbot() {
    if ! command -v certbot &> /dev/null; then
        print_error "certbot is not installed. Please install it first:"
        echo "  sudo apt-get update && sudo apt-get install certbot"
        exit 1
    fi
}

# Function to stop nginx service
stop_nginx() {
    print_status "Stopping nginx service..."
    cd "$PROJECT_DIR"
    docker-compose -f $COMPOSE_FILE stop nginx
}

# Function to renew certificates
renew_certificates() {
    print_status "Renewing SSL certificates..."
    
    # Check if certificates need renewal
    if certbot certificates | grep -q "VALID"; then
        print_status "Attempting to renew certificates..."
        certbot renew --quiet --agree-tos --email admin@$DOMAIN
    else
        print_warning "No valid certificates found. Please obtain certificates first:"
        echo "  sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN"
        exit 1
    fi
}

# Function to copy certificates
copy_certificates() {
    print_status "Copying certificates to project directory..."
    
    # Create SSL directory if it doesn't exist
    mkdir -p "$PROJECT_DIR/ssl"
    
    # Copy certificate files
    cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$PROJECT_DIR/ssl/$DOMAIN.crt"
    cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$PROJECT_DIR/ssl/$DOMAIN.key"
    
    # Set proper permissions
    chown $SUDO_USER:$SUDO_USER "$PROJECT_DIR/ssl/$DOMAIN.crt"
    chown $SUDO_USER:$SUDO_USER "$PROJECT_DIR/ssl/$DOMAIN.key"
    chmod 600 "$PROJECT_DIR/ssl/$DOMAIN.crt"
    chmod 600 "$PROJECT_DIR/ssl/$DOMAIN.key"
}

# Function to start nginx service
start_nginx() {
    print_status "Starting nginx service..."
    cd "$PROJECT_DIR"
    docker-compose -f $COMPOSE_FILE start nginx
}

# Function to verify certificate renewal
verify_renewal() {
    print_status "Verifying certificate renewal..."
    
    # Check certificate expiration
    local cert_file="$PROJECT_DIR/ssl/$DOMAIN.crt"
    if [[ -f "$cert_file" ]]; then
        local expiry_date=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
        print_status "Certificate expires on: $expiry_date"
    else
        print_error "Certificate file not found: $cert_file"
        exit 1
    fi
}

# Function to test nginx configuration
test_nginx() {
    print_status "Testing nginx configuration..."
    cd "$PROJECT_DIR"
    if docker-compose -f $COMPOSE_FILE exec nginx nginx -t; then
        print_status "Nginx configuration is valid"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
}

# Main execution
main() {
    print_status "Starting SSL certificate renewal process..."
    
    # Check prerequisites
    check_root
    check_certbot
    
    # Update project directory path
    if [[ "$PROJECT_DIR" == "/path/to/your/inspector" ]]; then
        print_error "Please update PROJECT_DIR in this script to point to your Inspector installation"
        exit 1
    fi
    
    # Execute renewal process
    stop_nginx
    renew_certificates
    copy_certificates
    start_nginx
    test_nginx
    verify_renewal
    
    print_status "SSL certificate renewal completed successfully!"
    print_status "Certificates are valid and nginx is running."
}

# Run main function
main "$@"
