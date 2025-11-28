# setup.ps1
# One-click setup script for the Multi-Agent QAOps Orchestrator

# Check if the virtual environment directory exists
if (-not (Test-Path -Path "venv" -PathType Container)) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
    if ($?) {
        Write-Host "Virtual environment created successfully." -ForegroundColor Green
    } else {
        Write-Host "Error creating virtual environment. Please ensure Python 3 is installed and in your PATH." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists."
}

# Activate the virtual environment and install dependencies
Write-Host "Activating virtual environment and installing dependencies..."
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

if ($?) {
    Write-Host "Setup complete! You can now run the orchestrator with:" -ForegroundColor Green
    Write-Host "python main_orchestrator.py" -ForegroundColor Cyan
} else {
    Write-Host "Error installing dependencies from requirements.txt." -ForegroundColor Red
    exit 1
}
