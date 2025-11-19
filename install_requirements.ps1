# Create and activate virtual environment if it doesn't exist
if (-not (Test-Path .venv)) {
    python -m venv .venv
}

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Additional required packages
pip install python-nmap
pip install APScheduler==3.10.4
pip install requests==2.31.0