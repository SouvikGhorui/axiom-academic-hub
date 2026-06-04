# Setup environment variables
$PROJECT_ID = "stately-lambda-495113-j3"
$REGION = "us-central1"
$REPO_NAME = "axiom-repo"
$DB_INSTANCE = "axiom-db"

# Set the active project
Write-Host "Setting active project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

Write-Host "Enabling Google Cloud Services..."
gcloud services enable run.googleapis.com `
    cloudbuild.googleapis.com `
    artifactregistry.googleapis.com `
    secretmanager.googleapis.com `
    sqladmin.googleapis.com

Write-Host "Creating Artifact Registry..."
gcloud artifacts repositories create $REPO_NAME `
    --repository-format=docker `
    --location=$REGION `
    --description="Axiom Hub Docker repository"

Write-Host "Creating Secret Manager entries..."
$SECRETS = @("DATABASE_URL", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "JWT_SECRET_KEY", "GEMINI_API_KEY", "FRONTEND_URL", "GOOGLE_REDIRECT_URI")
foreach ($secret in $SECRETS) {
    gcloud secrets create $secret --replication-policy="automatic"
}

Write-Host "Creating Cloud SQL Instance (PostgreSQL)..."
Write-Host "Note: This can take 5-10 minutes."
gcloud sql instances create $DB_INSTANCE `
    --database-version=POSTGRES_15 `
    --tier=db-f1-micro `
    --region=$REGION `
    --storage-type=HDD `
    --storage-size=10GB `
    --edition=enterprise

Write-Host "Infrastructure provisioning commands complete!"
Write-Host "Next steps:"
Write-Host "1. Go to https://console.cloud.google.com/security/secret-manager"
Write-Host "2. Add 'versions' to each secret with your actual configuration values."
Write-Host "3. Run 'gcloud builds submit --config cloudbuild.yaml' to trigger your first deploy."
