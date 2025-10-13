# run_server.ps1 - safe PowerShell launcher for the Flask app
# Usage: Right-click -> Run with PowerShell, or from PowerShell: .\run_server.ps1

# Absolute path to the venv python discovered by the environment configuration
$python = 'C:/Users/Lilitha.Nomaxayi/MRI Software/MRI SA LEAD (UC) - Intern Circle - Portfolios of Evidence/Lilitha Nomaxayi/PyThOn ( workout)/.venv/eathon2/.venv/Scripts/python.exe'

# Script to run (this file lives in the project root)
$script = Join-Path $PSScriptRoot 'app.py'

Write-Host "Using Python: $python"
Write-Host "Running: $script"

# Use the call operator & to launch the interpreter with properly quoted paths
& $python $script
