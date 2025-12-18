#!/bin/bash
set -e

# Configuration
PROJECT_ID="your-gcp-project-id"  # 要変更: GCPプロジェクトID
REGION="asia-northeast1"  # 東京リージョン
JOB_NAME="binance-moneyforward-sync"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${JOB_NAME}"

echo "=== Binance to MoneyForward Sync - Cloud Run Deployment ==="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "Error: Not logged in to gcloud."
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set project
echo "Setting GCP project to: ${PROJECT_ID}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo ""
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Build and push Docker image
echo ""
echo "Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Create or update Cloud Run Job
echo ""
echo "Deploying Cloud Run Job..."
gcloud run jobs deploy ${JOB_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --set-secrets BINANCE_API_KEY=BINANCE_API_KEY:latest,BINANCE_API_SECRET=BINANCE_API_SECRET:latest,MONEYFORWARD_USER=MONEYFORWARD_USER:latest,MONEYFORWARD_PASSWORD=MONEYFORWARD_PASSWORD:latest \
    --max-retries 3 \
    --task-timeout 30m \
    --memory 1Gi \
    --cpu 1

echo ""
echo "=== Deployment completed successfully! ==="
echo ""
echo "To run the job manually:"
echo "  gcloud run jobs execute ${JOB_NAME} --region ${REGION}"
echo ""
echo "To set up scheduled execution (daily at 23:00 JST):"
echo "  gcloud scheduler jobs create http ${JOB_NAME}-scheduler \\"
echo "    --location ${REGION} \\"
echo "    --schedule '0 23 * * *' \\"
echo "    --time-zone 'Asia/Tokyo' \\"
echo "    --uri 'https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run' \\"
echo "    --http-method POST \\"
echo "    --oauth-service-account-email [SERVICE_ACCOUNT_EMAIL]"
echo ""
