# PowerShell script to activate virtual environment and run Python script

# Set variables - modify these paths as needed
$VenvPath = "..\.venv"  # Path to your virtual environment
$PythonScript = "full_start.py"  # Name of your Python script
$env:PYTHONPATH = "$env:PYTHONPATH;D:\Documents\PycharmProjects\eagle-eye"

# Check if virtual environment exists
if (-Not (Test-Path $VenvPath)) {
    Write-Host "Error: Virtual environment not found at $VenvPath" -ForegroundColor Red
    Write-Host "Please create a virtual environment first using: python -m venv $VenvPath" -ForegroundColor Yellow
    exit 1
}

# Check if Python script exists
if (-Not (Test-Path $PythonScript)) {
    Write-Host "Error: Python script not found at $PythonScript" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment... ($VenvPath)" -ForegroundColor Green
& "$VenvPath\Scripts\Activate.ps1"

# Check if activation was successful
if (!$?) {
    Write-Host "Error: Failed to activate virtual environment ($LASTEXITCODE) ($?)" -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment activated successfully!" -ForegroundColor Green

# Run Python script
Write-Host "Running Python script: $PythonScript" -ForegroundColor Green
python $PythonScript

# Check if Python script ran successfully
if ($LASTEXITCODE -eq 0) {
    Write-Host "Python script completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Python script failed with exit code: $LASTEXITCODE" -ForegroundColor Red
}

# Optional: Deactivate virtual environment
# deactivate
