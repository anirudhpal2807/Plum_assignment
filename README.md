# AI Medical Report Simplifier

A backend API service that converts medical lab reports (text, images, or PDFs) into patient-friendly summaries using Python, FastAPI, and OCR.

## Features

- **Multiple Input Formats**: Text, images (JPG, PNG, BMP), and PDF files
- **OCR Processing**: Extract text from scanned reports using Tesseract
- **Intelligent Parsing**: Extract test name, value, unit, and status
- **Fuzzy Matching**: Handle OCR typos and spelling variations
- **Reference Ranges**: Compare against standard medical ranges
- **Patient-Friendly Explanations**: Generate easy-to-understand summaries

## Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR** - [Download for Windows](https://github.com/UB-Mannheim/tesseract/wiki)

### Installation

```bash
cd medical_report_api
pip install -r requirements.txt
```

### Run Server

**PowerShell:**
```powershell
$env:TESSERACT_CMD = 'C:\Program Files\Tesseract-OCR\tesseract.exe'
python run_server.py
```

**Or use the start script:**
```powershell
.\start_server.ps1
```

Server runs at: `http://localhost:8000`

### Test the API

Open `frontend.html` in your browser to use the web interface.

Or use curl:
```bash
curl -X POST "http://localhost:8000/simplify-report-text" \
  -d "report_text=Hemoglobin 10.2 g/dL"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/simplify-report-text` | POST | Process text input |
| `/simplify-report` | POST | Process file upload (image/PDF) |
| `/supported-tests` | GET | List all supported tests |

## Project Structure

```
medical_report_api/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── config/
│   │   ├── reference_ranges.json  # Test definitions
│   │   └── explanation_templates.json
│   └── modules/
│       ├── ocr.py                 # Image text extraction
│       ├── parser.py              # Test line parsing
│       ├── normalizer.py          # Test name matching
│       ├── summarizer.py          # Summary generation
│       └── pipeline.py            # Main orchestrator
├── frontend.html                  # Web UI
├── requirements.txt
└── run_server.py
```

## Supported Tests

The system recognizes 30+ common blood tests including:

- **Hematology**: Hemoglobin, RBC, WBC, Platelets, Hematocrit, MCV, MCH, MCHC
- **Metabolic**: Glucose, HbA1c, Uric Acid
- **Lipid Profile**: Cholesterol, LDL, HDL, Triglycerides
- **Liver Function**: AST, ALT, ALP, Bilirubin
- **Kidney Function**: Creatinine, BUN
- **Thyroid**: TSH, T3, T4
- **Vitamins**: Vitamin D, Vitamin B12
- **Electrolytes**: Sodium, Potassium, Chloride, Calcium

## Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP_GUIDE.md)

## License

MIT License
