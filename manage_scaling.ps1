# manage_scaling.ps1
# Usage: .\manage_scaling.ps1 -Mode "LIVE" (or "ECO")

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("LIVE", "ECO")]
    [string]$Mode
)

$PROJECT_ID = "stately-lambda-495113-j3"
$REGION = "us-central1"
$SERVICES = @("backend", "axiom")

if ($Mode -eq "LIVE") {
    foreach ($service in $SERVICES) {
        Write-Host "Updating service: $service to LIVE mode (Always-on, 1Gi, Gen2)..."
        gcloud run services update $service --region=$REGION --min-instances=1 --no-cpu-throttling --memory=1Gi --execution-environment=gen2 --quiet
    }
} else {
    foreach ($service in $SERVICES) {
        Write-Host "Updating service: $service to ECO mode (Scale-to-zero, 512Mi, Gen1)..."
        gcloud run services update $service --region=$REGION --min-instances=0 --cpu-throttling --memory=512Mi --execution-environment=gen1 --quiet
    }
}

Write-Host "✅ Mode applied: $Mode" -ForegroundColor Green
