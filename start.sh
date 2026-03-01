#!/bin/bash

# LuminalLib Docker Startup Script
# This script automates the Docker setup and startup process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
}

check_docker_daemon() {
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    print_success "Docker daemon is running"
}

setup_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found"
        if [ -f .env.example ]; then
            print_warning "Creating .env from .env.example"
            cp .env.example .env
            print_success ".env created from .env.example"
            print_warning "Please edit .env with your configuration"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

cleanup_old_containers() {
    print_header "Cleaning up old containers"
    
    # Check if there are running containers
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        read -p "Old containers are running. Stop them? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down
            print_success "Old containers stopped and removed"
        fi
    fi
}

build_services() {
    print_header "Building services"
    echo "This may take a few minutes on first run..."
    
    docker-compose build
    print_success "Services built successfully"
}

start_services() {
    print_header "Starting services"
    
    docker-compose up -d
    print_success "Services started in background"
}

wait_for_health() {
    print_header "Waiting for services to be healthy"
    
    local max_attempts=60
    local attempt=0
    
    echo "Checking PostgreSQL..."
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps postgres | grep -q "healthy"; then
            print_success "PostgreSQL is healthy"
            break
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "PostgreSQL failed to become healthy"
        echo "Logs:"
        docker-compose logs postgres | tail -20
        exit 1
    fi
    
    attempt=0
    echo -e "\nChecking Backend..."
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps backend | grep -q "healthy"; then
            print_success "Backend is healthy"
            break
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Backend failed to become healthy"
        echo "Logs:"
        docker-compose logs backend | tail -20
        exit 1
    fi
    
    attempt=0
    echo -e "\nChecking Frontend..."
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps frontend | grep -q "healthy"; then
            print_success "Frontend is healthy"
            break
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_warning "Frontend is taking longer to start (this is normal)"
    else
        print_success "Frontend is healthy"
    fi
}

show_status() {
    print_header "Service Status"
    docker-compose ps
}

show_access_info() {
    print_header "✨ LuminalLib is Ready!"
    
    echo -e "${GREEN}Access the application:${NC}"
    echo ""
    echo -e "  ${BLUE}Frontend:${NC}        http://localhost:3000"
    echo -e "  ${BLUE}API Docs:${NC}        http://localhost:8000/docs"
    echo -e "  ${BLUE}DB Admin:${NC}        http://localhost:8080"
    echo ""
    echo -e "${GREEN}Useful commands:${NC}"
    echo ""
    echo -e "  View logs:             ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  View specific logs:    ${YELLOW}docker-compose logs -f backend${NC}"
    echo -e "  Access PostgreSQL:     ${YELLOW}docker-compose exec postgres psql -U postgres -d luminallib_db${NC}"
    echo -e "  Access backend shell:  ${YELLOW}docker-compose exec backend bash${NC}"
    echo -e "  Stop services:         ${YELLOW}docker-compose down${NC}"
    echo ""
}

# Main execution
main() {
    print_header "🚀 LuminalLib Docker Setup"
    
    # Get script directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd "$SCRIPT_DIR"
    
    # Check prerequisites
    print_header "Checking prerequisites"
    check_docker
    check_docker_compose
    check_docker_daemon
    
    # Setup environment
    setup_env
    
    # Cleanup old containers
    cleanup_old_containers
    
    # Build and start
    build_services
    start_services
    
    # Wait for health
    wait_for_health
    
    # Show status
    show_status
    
    # Show access info
    show_access_info
}

# Run main function
main
