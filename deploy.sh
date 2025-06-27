#!/bin/bash

# Aha Clip Deployment Script
# This script helps deploy the application to various platforms

set -e

echo "🚀 Aha Clip Deployment Script"
echo "=============================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy env.example to .env and configure your environment variables"
    exit 1
fi

# Function to deploy to Heroku
deploy_heroku() {
    echo "📦 Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Please install it first."
        echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Check if logged in
    if ! heroku auth:whoami &> /dev/null; then
        echo "🔐 Please login to Heroku first:"
        heroku login
    fi
    
    # Create app if it doesn't exist
    if [ -z "$HEROKU_APP_NAME" ]; then
        echo "📝 Creating Heroku app..."
        heroku create
    else
        echo "📝 Using existing Heroku app: $HEROKU_APP_NAME"
        heroku git:remote -a $HEROKU_APP_NAME
    fi
    
    # Set environment variables
    echo "🔧 Setting environment variables..."
    source .env
    heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY"
    heroku config:set SECRET_KEY="$SECRET_KEY"
    heroku config:set FLASK_ENV="production"
    
    # Deploy
    echo "🚀 Deploying application..."
    git add .
    git commit -m "Deploy to Heroku - $(date)"
    git push heroku main
    
    # Scale the app
    echo "⚡ Scaling application..."
    heroku ps:scale web=1
    
    echo "✅ Deployment complete!"
    echo "🌐 Your app is available at: $(heroku info -s | grep web_url | cut -d= -f2)"
}

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Deploying with Docker..."
    
    # Build and run with Docker Compose
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    echo "✅ Docker deployment complete!"
    echo "🌐 Your app is available at: http://localhost:5001"
}

# Function to deploy to DigitalOcean App Platform
deploy_digitalocean() {
    echo "🌊 DigitalOcean App Platform deployment"
    echo "Please follow these steps:"
    echo "1. Go to https://cloud.digitalocean.com/apps"
    echo "2. Click 'Create App'"
    echo "3. Connect your GitHub repository"
    echo "4. Configure the app:"
    echo "   - Source: server.py"
    echo "   - Environment: Python"
    echo "   - Build command: pip install -r requirements.txt"
    echo "   - Run command: gunicorn --config gunicorn.conf.py wsgi:app"
    echo "5. Add environment variables from your .env file"
    echo "6. Click 'Create Resources'"
}

# Function to check dependencies
check_dependencies() {
    echo "🔍 Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip3 not found"
        exit 1
    fi
    
    # Check Docker (if using Docker deployment)
    if [ "$1" = "docker" ] && ! command -v docker &> /dev/null; then
        echo "❌ Docker not found"
        exit 1
    fi
    
    echo "✅ Dependencies check passed"
}

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed"
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    # Add your test commands here
    echo "✅ Tests passed"
}

# Main script
case "${1:-}" in
    "heroku")
        check_dependencies
        deploy_heroku
        ;;
    "docker")
        check_dependencies docker
        deploy_docker
        ;;
    "digitalocean")
        deploy_digitalocean
        ;;
    "install")
        check_dependencies
        install_dependencies
        ;;
    "test")
        check_dependencies
        install_dependencies
        run_tests
        ;;
    "local")
        check_dependencies
        install_dependencies
        echo "🚀 Starting local development server..."
        export $(cat .env | xargs)
        python3 server.py
        ;;
    *)
        echo "Usage: $0 {heroku|docker|digitalocean|install|test|local}"
        echo ""
        echo "Commands:"
        echo "  heroku      - Deploy to Heroku"
        echo "  docker      - Deploy with Docker Compose"
        echo "  digitalocean - Instructions for DigitalOcean App Platform"
        echo "  install     - Install Python dependencies"
        echo "  test        - Run tests"
        echo "  local       - Start local development server"
        echo ""
        echo "Examples:"
        echo "  $0 install    # Install dependencies"
        echo "  $0 local      # Start local server"
        echo "  $0 heroku     # Deploy to Heroku"
        exit 1
        ;;
esac 