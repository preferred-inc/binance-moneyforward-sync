#!/bin/bash
set -e

# Configuration
PROJECT_ID="your-gcp-project-id"  # 要変更: GCPプロジェクトID

echo "=== Setting up Google Cloud Secrets ==="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed."
    exit 1
fi

# Set project
gcloud config set project ${PROJECT_ID}

# Enable Secret Manager API
echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

# Create secrets
echo ""
echo "Creating secrets..."

# BINANCE_API_KEY
echo -n "Enter BINANCE_API_KEY: "
read -s BINANCE_API_KEY
echo ""
echo -n "${BINANCE_API_KEY}" | gcloud secrets create BINANCE_API_KEY --data-file=- || \
    echo -n "${BINANCE_API_KEY}" | gcloud secrets versions add BINANCE_API_KEY --data-file=-

# BINANCE_API_SECRET
echo -n "Enter BINANCE_API_SECRET: "
read -s BINANCE_API_SECRET
echo ""
echo -n "${BINANCE_API_SECRET}" | gcloud secrets create BINANCE_API_SECRET --data-file=- || \
    echo -n "${BINANCE_API_SECRET}" | gcloud secrets versions add BINANCE_API_SECRET --data-file=-

# MONEYFORWARD_USER
echo -n "Enter MONEYFORWARD_USER (email): "
read MONEYFORWARD_USER
echo -n "${MONEYFORWARD_USER}" | gcloud secrets create MONEYFORWARD_USER --data-file=- || \
    echo -n "${MONEYFORWARD_USER}" | gcloud secrets versions add MONEYFORWARD_USER --data-file=-

# MONEYFORWARD_PASSWORD
echo -n "Enter MONEYFORWARD_PASSWORD: "
read -s MONEYFORWARD_PASSWORD
echo ""
echo -n "${MONEYFORWARD_PASSWORD}" | gcloud secrets create MONEYFORWARD_PASSWORD --data-file=- || \
    echo -n "${MONEYFORWARD_PASSWORD}" | gcloud secrets versions add MONEYFORWARD_PASSWORD --data-file=-

echo ""
echo "=== Secrets created successfully! ==="
echo ""
echo "Created/Updated secrets:"
echo "  - BINANCE_API_KEY"
echo "  - BINANCE_API_SECRET"
echo "  - MONEYFORWARD_USER"
echo "  - MONEYFORWARD_PASSWORD"
echo ""
