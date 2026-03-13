#!/bin/bash
# Quick setup script for Google Cloud SDK and Authentication
# For Sikh Temple Membership System

set -e  # Exit on error

echo "=========================================="
echo "Google Cloud Vision API Setup"
echo "=========================================="
echo ""

# Check if gcloud is already installed
if command -v gcloud &> /dev/null; then
    echo "✓ gcloud CLI is already installed"
    gcloud --version
    echo ""
else
    echo "Installing Google Cloud SDK..."
    echo ""

    # Add Cloud SDK repo for Debian/Ubuntu
    if [ -f /etc/debian_version ]; then
        echo "Detected Debian/Ubuntu system"

        # Add the Cloud SDK distribution URI as a package source
        echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

        # Import the Google Cloud public key
        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

        # Update and install the Cloud SDK
        sudo apt-get update && sudo apt-get install -y google-cloud-cli

        echo "✓ gcloud CLI installed successfully"
    else
        echo "⚠ Unable to auto-install gcloud on this system"
        echo "Please install manually from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Step 1: Initialize gcloud"
echo "=========================================="
echo ""
echo "This will open a browser window to sign in to Google Cloud"
read -p "Press Enter to continue..."

gcloud init

echo ""
echo "=========================================="
echo "Step 2: Set up Application Default Credentials"
echo "=========================================="
echo ""
echo "This will authenticate your local development environment"
read -p "Press Enter to continue..."

gcloud auth application-default login

echo ""
echo "=========================================="
echo "Step 3: Enable Vision API"
echo "=========================================="
echo ""

# Get the current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "⚠ No project selected"
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

echo "Enabling Vision API for project: $PROJECT_ID"
gcloud services enable vision.googleapis.com

echo ""
echo "=========================================="
echo "Step 4: Test the setup"
echo "=========================================="
echo ""

cd "$(dirname "$0")/backend"

if [ ! -d "venv" ]; then
    echo "⚠ Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "Running Vision API test..."
python test_vision_api.py

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the backend: cd backend && source venv/bin/activate && python app.py"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Upload a test form to verify OCR is working"
echo ""
echo "For more information, see GCLOUD_AUTH_SETUP.md"
