# Setup & Configuration Guide

## Prerequisites

### System Requirements
- **OS**: Windows 10+, Linux (Ubuntu 18.04+), or macOS 10.14+
- **Python**: 3.8, 3.9, 3.10, 3.11, or 3.12
- **RAM**: 4 GB minimum (8 GB recommended)
- **Disk**: 2 GB free space

### Software Requirements
1. **Git** (optional, for version control)
2. **Python Package Manager** (pip)
3. **Tesseract OCR** (binary installation required)

---

## Installation Steps

### Step 1: Install Tesseract OCR Engine

This is **REQUIRED** for image processing.

#### Windows

**Option A: Using Installer (Recommended)**

1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Download `tesseract-ocr-w64-setup-v5.x.exe` (64-bit) or `tesseract-ocr-w32-setup-v5.x.exe` (32-bit)
3. Run installer
4. Select installation path (default: `C:\Program Files\Tesseract-OCR`)
5. Finish installation
6. Verify installation:
   ```powershell
   tesseract --version
   ```

**Option B: Using Chocolatey**

```powershell
# Install chocolatey first if not installed
# Then run:
choco install tesseract
```

**Option C: Using Package Manager**

```powershell
# Using scoop package manager
scoop install tesseract
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev

# Verify
tesseract --version
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install tesseract
sudo dnf install tesseract-devel
```

#### macOS

```bash
# Using Homebrew
brew install tesseract

# Verify
tesseract --version
```

---

### Step 2: Clone or Download Project

```bash
# Using git
git clone https://github.com/yourusername/medical_report_api.git
cd medical_report_api

# Or download and extract ZIP file
```

---

### Step 3: Create Python Virtual Environment

**Recommended:** Use virtual environment to isolate dependencies

#### Windows (PowerShell)

```powershell
# Navigate to project directory
cd path\to\medical_report_api

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then run activate again
```

#### Windows (Command Prompt)

```cmd
cd path\to\medical_report_api
python -m venv venv
venv\Scripts\activate.bat
```

#### Linux/macOS

```bash
cd path/to/medical_report_api
python3 -m venv venv
source venv/bin/activate
```

---

### Step 4: Install Python Dependencies

```bash
# Ensure virtual environment is activated
pip install --upgrade pip setuptools wheel

# Install from requirements.txt
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 python-multipart-0.0.6 ...
```

---

### Step 5: Verify Installation

```bash
# Check Python packages
python -c "import fastapi, cv2, pytesseract; print('✓ All packages installed')"

# Test Tesseract
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"

# Test FastAPI
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
```

---

## Configuration

### 1. Tesseract Path Configuration (if not in PATH)

If Tesseract is not in your system PATH, update `app/modules/ocr.py`:

```python
# Find this section in ocr.py
import pytesseract

# Add this line (Windows example)
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# macOS example
pytesseract.pytesseract.pytesseract_cmd = '/usr/local/bin/tesseract'

# Linux example
pytesseract.pytesseract.pytesseract_cmd = '/usr/bin/tesseract'
```

### 2. Configure Logging

Edit `app/config/logger.py` to customize:

```python
# Change log level
logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Change log file location
log_file = "/custom/path/logs.log"

# Change log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
```

### 3. Add Custom Tests

Add new tests to `app/config/reference_ranges.json`:

```json
{
  "blood_tests": {
    "New Test Name": {
      "aliases": ["short", "alternate"],
      "unit": "mg/dL",
      "reference_range": {
        "low": 0,
        "high": 100
      },
      "category": "metabolic",
      "explanation": "Brief explanation of what this test measures"
    }
  }
}
```

### 4. Customize Explanations

Edit `app/config/explanation_templates.json`:

```json
{
  "explanations": {
    "low": {
      "New Test Name": "Custom explanation for low values"
    },
    "high": {
      "New Test Name": "Custom explanation for high values"
    }
  }
}
```

### 5. Adjust Fuzzy Matching Threshold

In `app/modules/normalizer.py`, change fuzzy threshold:

```python
# More lenient (catches more variations)
self.fuzzy_threshold = 75

# More strict (only exact matches and very similar)
self.fuzzy_threshold = 90
```

---

## Running the Application

### Option 1: Development Server (with auto-reload)

```bash
# Activate virtual environment first
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Option 2: Production Server

```bash
# Using gunicorn with multiple workers
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:8000 app.main:app --timeout 120
```

### Option 3: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Install Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t medical-report-api .
docker run -p 8000:8000 medical-report-api
```

---

## Access the API

### 1. Swagger Documentation

Open in browser:
```
http://localhost:8000/docs
```

Try endpoints directly in the UI

### 2. ReDoc Documentation

```
http://localhost:8000/redoc
```

Alternative documentation view

### 3. Programmatic Access

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/simplify-report",
    data={"text": "Hemoglobin 10.2 g/dL (Low)"}
)
print(response.json())
```

**cURL:**
```bash
curl -X POST "http://localhost:8000/simplify-report" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Hemoglobin 10.2 g/dL"
```

**JavaScript/Fetch:**
```javascript
fetch('http://localhost:8000/simplify-report', {
  method: 'POST',
  body: new FormData(document.querySelector('form'))
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## Running Tests

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_parser.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Manual Testing

Test with sample file:

```bash
python -c "
from app.modules.pipeline import MedicalReportPipeline
import json

pipeline = MedicalReportPipeline()
result = pipeline.process_text('Hemoglobin 10.2 g/dL (Low)')
print(json.dumps(result, indent=2))
"
```

---

## Environment Variables (Optional)

Create `.env` file in project root:

```env
# Application
APP_NAME=Medical Report API
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs

# OCR
TESSERACT_PATH=/usr/bin/tesseract
OCR_TIMEOUT=30

# Fuzzy Matching
FUZZY_THRESHOLD=80

# Rate Limiting (future)
RATE_LIMIT_PER_MINUTE=100
```

Load in `app/main.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", 8000))
```

---

## Troubleshooting

### Issue: "No module named 'pytesseract'"

**Solution:**
```bash
pip install pytesseract
# OR reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Issue: "tesseract is not installed or it is not in your PATH"

**Solution:**
```python
# Add to app/modules/ocr.py at the top:
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue: "ImportError: libGL.so.1"

**Solution (Linux):**
```bash
sudo apt-get install libgl1-mesa-glx
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use different port
python -m uvicorn app.main:app --port 8001

# Or kill process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

### Issue: Out of memory with large images

**Solution:**
```python
# Resize images before processing
import cv2
image = cv2.imread("large_image.jpg")
resized = cv2.resize(image, (1920, 1080))  # Smaller size
```

---

## Performance Tuning

### 1. Increase Worker Count (Production)

```bash
gunicorn -w 8 -b 0.0.0.0:8000 app.main:app
```

### 2. Enable Caching

```python
# In app/main.py
from functools import lru_cache

@lru_cache(maxsize=100)
def get_supported_tests():
    # This result is cached
    return config.get_reference_ranges()
```

### 3. Optimize Image Preprocessing

```python
# In app/modules/ocr.py
# Reduce image resolution before OCR
image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
```

### 4. Use AsyncIO for I/O Operations

```python
# Already implemented in FastAPI endpoints
async def simplify_report(text: Optional[str] = None):
    # Handles concurrency automatically
    pass
```

---

## Monitoring & Logging

### View Logs

```bash
# Windows
Get-Content logs\20240108.log -Tail 50

# Linux/macOS
tail -f logs/20240108.log
```

### Enable Debug Logging

```python
# In app/config/logger.py
logger.setLevel(logging.DEBUG)
```

### Monitor Performance

```bash
# Using uvicorn's built-in metrics
curl http://localhost:8000/metrics

# Or use third-party tools
pip install prometheus-client
```

---

## Backup & Migration

### Backup Configuration

```bash
# Backup reference data and configs
cp -r app/config backup_config/

# Backup logs
cp -r logs backup_logs/
```

### Export Data

```python
# Export all supported tests
from app.config.config import ConfigLoader
import json

config = ConfigLoader()
ranges = config.get_reference_ranges()

with open("backup_reference_ranges.json", "w") as f:
    json.dump(ranges, f, indent=2)
```

---

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS/TLS certificates
- [ ] Implement API authentication (API key/JWT)
- [ ] Enable CORS only for trusted domains
- [ ] Validate all file uploads
- [ ] Implement rate limiting
- [ ] Don't log sensitive medical data
- [ ] Regular security updates (`pip install --upgrade`)
- [ ] Run security scan: `pip install bandit; bandit -r app/`

---

## Deployment Checklist

- [ ] Update `requirements.txt` with production versions
- [ ] Set environment variables correctly
- [ ] Configure logging to file
- [ ] Test all endpoints thoroughly
- [ ] Set up monitoring/alerting
- [ ] Configure backup strategy
- [ ] Document custom configuration
- [ ] Plan disaster recovery
- [ ] Get security audit
- [ ] Ensure HIPAA/compliance requirements

---

## Maintenance

### Regular Updates

```bash
# Check for outdated packages
pip list --outdated

# Update packages
pip install --upgrade package_name

# Or update all
pip install --upgrade -r requirements.txt
```

### Database Cleanup (if using persistence)

```python
# Implement periodic cleanup
from datetime import datetime, timedelta

# Delete logs older than 30 days
import os
for file in os.listdir("logs/"):
    file_path = os.path.join("logs/", file)
    if os.path.isfile(file_path):
        if datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path)) > timedelta(days=30):
            os.remove(file_path)
```

---

**Last Updated**: December 8, 2024
