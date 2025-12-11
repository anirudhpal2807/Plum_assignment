# AI Medical Report Summarizer

## Complete Technical Documentation

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Author:** Medical Report Simplifier Team

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Workflow](#2-system-workflow--how-the-project-works)
3. [Tech Stack Used](#3-tech-stack-used)
4. [API Endpoint Documentation](#4-api-endpoint-documentation)
5. [Installation & Setup](#5-installation--setup)
6. [Configuration](#6-configuration)
7. [Supported Medical Tests](#7-supported-medical-tests)
8. [Project Structure](#8-project-structure)
9. [Module Documentation](#9-module-documentation)
10. [Error Handling](#10-error-handling)
11. [Examples & Use Cases](#11-examples--use-cases)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Project Overview

### What is AI Medical Report Summarizer?

The **AI Medical Report Summarizer** is an intelligent system that transforms complex medical laboratory reports into easy-to-understand, patient-friendly summaries. It uses advanced text processing, pattern recognition, and medical knowledge bases to extract, normalize, and explain medical test results.

### Problem Statement

Medical reports contain:
- Complex medical terminology
- Abbreviated test names (CBC, LFT, KFT, etc.)
- Reference ranges that vary by lab
- Technical units that patients don't understand

**This leads to:**
- Patient confusion and anxiety
- Misinterpretation of results
- Dependency on doctors for basic understanding
- Delayed health awareness

### Solution

The AI Medical Report Summarizer:
1. **Extracts** test data from images, PDFs, or text
2. **Normalizes** test names to standard medical terminology
3. **Compares** values against reference ranges
4. **Generates** three levels of output:
   - **Structured Data** - Machine-readable JSON
   - **Detailed Summary** - Complete medical interpretation
   - **Simple Summary** - Patient-friendly explanation

### Target Users

| User Type | Use Case |
|-----------|----------|
| **Patients** | Understand their own medical reports |
| **Doctors** | Quick overview of patient results |
| **Healthcare Apps** | Integrate medical report processing |
| **Developers** | Build health-tech applications |
| **Clinics/Labs** | Automated report summarization |
| **Telemedicine Platforms** | Remote health consultation support |

### Key Features

| Feature | Description |
|---------|-------------|
| 📄 **Multi-format Input** | Supports JPG, PNG, PDF, BMP, TIFF, and plain text |
| 🔍 **OCR Processing** | Extracts text from medical report images |
| 🧠 **Smart Normalization** | Maps 70+ test aliases to standard names |
| 📊 **Status Detection** | Identifies Low, Normal, High values |
| 💡 **Patient-Friendly Summaries** | Explains results in simple language |
| 🏥 **Rich AI Reports** | Generates comprehensive medical summaries |
| ⚠️ **Abnormal Cause Analysis** | Lists possible causes for abnormal results |
| 💊 **Health Recommendations** | Provides actionable health advice |
| 🔒 **Guardrail Protection** | Prevents hallucinated/fabricated test results |
| 📱 **Responsive Frontend** | Works on desktop, tablet, and mobile |

---

## 2. System Workflow / How the Project Works

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                     │
│         (Image / PDF / Text - Medical Report)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (HTML/JS)                               │
│    • File Upload (Drag & Drop)                                          │
│    • Text Paste                                                          │
│    • Sample Data Loader                                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP POST Request
┌─────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND SERVER                              │
│                    (http://localhost:8000)                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MEDICAL REPORT PIPELINE                               │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌────────────┐   ┌────────────────┐     │
│  │   OCR    │ → │  PARSER  │ → │ NORMALIZER │ → │  SUMMARIZER    │     │
│  │ Module   │   │  Module  │   │   Module   │   │    Module      │     │
│  └──────────┘   └──────────┘   └────────────┘   └────────────────┘     │
│       │              │               │                  │               │
│       ▼              ▼               ▼                  ▼               │
│   Extract        Parse Test      Standardize       Generate Rich       │
│   Text from      Lines with      Names & Add       AI Summary          │
│   Image/PDF      Values/Units    Reference         with Causes         │
│                                  Ranges            & Recommendations   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         JSON RESPONSE                                    │
│                                                                          │
│  {                                                                       │
│    "status": "ok",                                                       │
│    "tests": [...],           ← Structured Test Data                     │
│    "summary": "...",         ← Simple Summary                           │
│    "explanations": [...],    ← Detailed Explanations                    │
│    "report": {...}           ← Rich AI Report                           │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND DISPLAY                                    │
│                                                                          │
│  • Results Table with Status Badges (Normal/Low/High)                   │
│  • Patient Information Card                                              │
│  • Summary Statistics (Total/Normal/Abnormal)                           │
│  • Test Interpretations                                                  │
│  • Key Medical Concepts                                                  │
│  • Possible Causes for Abnormal Results                                 │
│  • Health Recommendations                                                │
│  • Print & Copy Options                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Processing Flow

#### Step 1: User Input
User provides medical report via:
- **File Upload**: Drag & drop or browse (JPG, PNG, PDF, BMP, TIFF)
- **Text Paste**: Copy-paste report text directly

#### Step 2: Backend Receives Request
FastAPI server receives the request:
- **File Upload** → `/simplify-report` endpoint
- **Text Input** → `/simplify-report-text` endpoint

#### Step 3: Pipeline Processing

| Stage | Module | Input | Output |
|-------|--------|-------|--------|
| **1. Extraction** | `ocr.py` | Image/PDF/Text | Raw test lines |
| **2. Parsing** | `parser.py` | Raw lines | Parsed test objects (name, value, unit) |
| **3. Normalization** | `normalizer.py` | Parsed tests | Standardized names + status (low/normal/high) |
| **4. Guardrail** | `summarizer.py` | Normalized tests | Validated tests (removes hallucinations) |
| **5. Summary** | `summarizer.py` | Validated tests | Rich AI report + explanations |

#### Step 4: Response Generation
API returns comprehensive JSON with:
- Structured test data
- Simple summary
- Detailed explanations
- Rich AI report (patient info, interpretations, causes, recommendations)

#### Step 5: Frontend Display
Frontend renders:
- Results table with color-coded status badges
- Rich AI-style medical report
- Print and copy functionality

---

## 3. Tech Stack Used

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12+ | Primary programming language |
| **FastAPI** | 0.104.1 | High-performance web framework |
| **Uvicorn** | 0.24.0 | ASGI server for FastAPI |
| **Pydantic** | 2.5.0 | Data validation and settings |

### OCR & Image Processing

| Technology | Version | Purpose |
|------------|---------|---------|
| **Tesseract OCR** | 5.x | Text extraction from images |
| **pytesseract** | 0.3.10 | Python wrapper for Tesseract |
| **OpenCV** | 4.8.1 | Image preprocessing |
| **Pillow** | 10.1.0 | Image handling |

### PDF Processing

| Technology | Version | Purpose |
|------------|---------|---------|
| **PyPDF2** | 3.x | PDF text extraction |

### Text Matching & NLP

| Technology | Version | Purpose |
|------------|---------|---------|
| **RapidFuzz** | 3.5.2 | Fuzzy string matching (80% threshold) |
| **FuzzyWuzzy** | 0.18.0 | Additional fuzzy matching |
| **python-Levenshtein** | 0.21.1 | Fast string distance calculation |

### Frontend Technologies

| Technology | Purpose |
|------------|---------|
| **HTML5** | Page structure |
| **CSS3** | Styling with responsive design |
| **Vanilla JavaScript** | Interactive functionality |
| **Fetch API** | HTTP requests to backend |

### Development & Testing

| Technology | Version | Purpose |
|------------|---------|---------|
| **pytest** | 7.4.3 | Unit testing framework |
| **pytest-asyncio** | 0.21.1 | Async test support |
| **pytest-cov** | 4.1.0 | Code coverage |

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              frontend.html                            │ │
│  │  • Responsive UI (Mobile/Tablet/Desktop)             │ │
│  │  • Dark Mode Support                                  │ │
│  │  • Drag & Drop File Upload                           │ │
│  │  • Print & Copy Features                             │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼ REST API (JSON)
┌────────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              FastAPI Application                      │ │
│  │  • CORS Middleware                                    │ │
│  │  • Request Validation                                 │ │
│  │  • Error Handling                                     │ │
│  └──────────────────────────────────────────────────────┘ │
│                            │                               │
│                            ▼                               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           Processing Pipeline                         │ │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌───────────┐  │ │
│  │  │   OCR   │→│ Parser  │→│Normalizer│→│Summarizer │  │ │
│  │  └─────────┘ └─────────┘ └──────────┘ └───────────┘  │ │
│  └──────────────────────────────────────────────────────┘ │
│                            │                               │
│                            ▼                               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              Configuration Layer                      │ │
│  │  • reference_ranges.json (70+ tests)                 │ │
│  │  • explanation_templates.json                         │ │
│  │  • Logging Configuration                              │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 4. API Endpoint Documentation

### Base URL
```
http://localhost:8000
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health status |
| POST | `/simplify-report` | Process file (image/PDF) |
| POST | `/simplify-report-text` | Process text input |
| GET | `/supported-tests` | List all supported tests |
| POST | `/batch-simplify` | Process multiple reports |

---

### **GET /**

**Purpose:** Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Medical Report Simplifier API",
  "version": "1.0.0"
}
```

---

### **GET /health**

**Purpose:** Detailed health status with Tesseract availability

**Response:**
```json
{
  "status": "healthy",
  "service": "Medical Report Simplifier API",
  "tesseract_available": true
}
```

---

### **POST /simplify-report**

**Purpose:** Process medical report from image or PDF file

**Content-Type:** `multipart/form-data`

**Request:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | Image (JPG, PNG, BMP, TIFF) or PDF file |

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/simplify-report" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@medical_report.pdf"
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/simplify-report', {
  method: 'POST',
  body: formData
});

const result = await response.json();
```

**Success Response (200 OK):**
```json
{
  "status": "ok",
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 12.5,
      "unit": "g/dL",
      "status": "normal",
      "test_status": "normal",
      "ref_range": {
        "low": 12.0,
        "high": 17.5
      },
      "category": "hematology",
      "normalization_confidence": 0.95,
      "parse_confidence": 0.92
    }
  ],
  "summary": "All 5 test result(s) are within normal ranges. Your health indicators look good!",
  "explanations": [
    {
      "test_name": "Hemoglobin",
      "status": "normal",
      "value": 12.5,
      "unit": "g/dL",
      "reference_range": {"low": 12.0, "high": 17.5},
      "explanation": "Your Hemoglobin is within the normal range, indicating healthy levels."
    }
  ],
  "report": {
    "title": "Complete Blood Count (CBC)",
    "generated_at": "2025-12-11T10:30:00.000Z",
    "patient_info": {
      "name": "Patient",
      "age": "N/A",
      "sex": "N/A",
      "date": "11 Dec 2025",
      "referred_by": "N/A"
    },
    "overall_status": "All Clear",
    "overall_message": "All 5 test(s) are within normal ranges. Your results indicate healthy levels.",
    "test_overviews": [...],
    "interpretations": [...],
    "key_concepts": [...],
    "abnormal_causes": [],
    "recommendations": [
      "Continue maintaining your healthy lifestyle.",
      "Schedule regular health check-ups as recommended by your doctor."
    ],
    "summary_stats": {
      "total_tests": 5,
      "normal_count": 5,
      "abnormal_count": 0,
      "categories_tested": ["hematology"]
    }
  },
  "metadata": {
    "total_tests_extracted": 5,
    "total_tests_parsed": 5,
    "total_tests_normalized": 5
  }
}
```

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid file type |
| 500 | Internal server error |

---

### **POST /simplify-report-text**

**Purpose:** Process medical report from plain text

**Content-Type:** `application/x-www-form-urlencoded`

**Request:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | Medical report text |

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/simplify-report-text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Hemoglobin: 12.5 g/dL%0AWBC: 8500 /uL%0APlatelets: 250000 /uL"
```

**JavaScript Example:**
```javascript
const formData = new URLSearchParams();
formData.append('text', reportText);

const response = await fetch('http://localhost:8000/simplify-report-text', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  body: formData
});

const result = await response.json();
```

**Response:** Same as `/simplify-report`

---

### **GET /supported-tests**

**Purpose:** Get list of all supported medical tests with reference ranges

**Response:**
```json
{
  "status": "ok",
  "tests": [
    {
      "name": "Hemoglobin",
      "unit": "g/dL",
      "reference_range": {"low": 12.0, "high": 17.5},
      "category": "hematology",
      "explanation": "Hemoglobin carries oxygen in red blood cells",
      "aliases": ["hemoglobin", "hb", "hgb", "haemoglobin"]
    },
    {
      "name": "White Blood Cell Count",
      "unit": "/uL",
      "reference_range": {"low": 4000, "high": 11000},
      "category": "hematology",
      "explanation": "WBC helps fight infections",
      "aliases": ["wbc", "white blood cell", "wbc count", "tlc"]
    }
    // ... more tests
  ],
  "total_tests": 70
}
```

---

### **POST /batch-simplify**

**Purpose:** Process multiple reports in a single request

**Content-Type:** `application/json`

**Request:**
```json
[
  "Hemoglobin: 12.5 g/dL\nWBC: 8500 /uL",
  "Glucose: 110 mg/dL\nCreatinine: 1.2 mg/dL",
  "TSH: 2.5 mIU/L\nT4: 8.0 ug/dL"
]
```

**Response:**
```json
{
  "status": "ok",
  "total_reports": 3,
  "results": [
    {
      "batch_index": 0,
      "status": "ok",
      "tests": [...],
      "summary": "..."
    },
    {
      "batch_index": 1,
      "status": "ok",
      "tests": [...],
      "summary": "..."
    },
    {
      "batch_index": 2,
      "status": "ok",
      "tests": [...],
      "summary": "..."
    }
  ]
}
```

**Limits:**
- Maximum 100 reports per batch

---

## 5. Installation & Setup

### Prerequisites

- **Python 3.10+** (recommended 3.12)
- **Tesseract OCR** (for image processing)
- **pip** (Python package manager)

### Step 1: Clone/Download Project

```bash
cd C:\MERN_project\PLUm\medical_report_api
```

### Step 2: Install Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR\`
3. Add to PATH or set environment variable

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt contents:**
```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pytesseract==0.3.10
opencv-python==4.8.1.78
Pillow==10.1.0
rapidfuzz==3.5.2
PyPDF2==3.0.1
pydantic==2.5.0
```

### Step 4: Start the Server

**Option 1: Using Python**
```bash
python run_server.py
```

**Option 2: Using PowerShell Script**
```powershell
.\start_server.ps1
```

**Option 3: Using Batch File**
```cmd
start_server.bat
```

### Step 5: Access the Application

- **Frontend:** Open `frontend.html` in browser
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 6. Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TESSERACT_CMD` | Path to Tesseract executable | Auto-detected |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

### Configuration Files

#### `app/config/reference_ranges.json`

Contains 70+ medical test definitions:

```json
{
  "blood_tests": {
    "Hemoglobin": {
      "aliases": ["hemoglobin", "hb", "hgb", "haemoglobin"],
      "unit": "g/dL",
      "reference_range": {"low": 12.0, "high": 17.5},
      "category": "hematology",
      "explanation": "Hemoglobin carries oxygen in red blood cells"
    }
    // ... more tests
  }
}
```

#### `app/config/explanation_templates.json`

Contains patient-friendly explanations:

```json
{
  "explanations": {
    "high": {
      "Hemoglobin": "Your hemoglobin is higher than normal. This could indicate dehydration or other conditions.",
      "Blood Glucose": "High blood sugar may indicate diabetes or prediabetes."
    },
    "low": {
      "Hemoglobin": "Low hemoglobin may indicate anemia. Consider iron-rich foods.",
      "Blood Glucose": "Low blood sugar (hypoglycemia) may cause dizziness and fatigue."
    },
    "normal": {
      "default": "This test is within the normal range."
    }
  }
}
```

---

## 7. Supported Medical Tests

### Test Categories

| Category | Tests Count | Examples |
|----------|-------------|----------|
| **Hematology (CBC)** | 15+ | Hemoglobin, WBC, RBC, Platelets, MCV, MCH |
| **Liver Function (LFT)** | 10+ | SGPT, SGOT, ALP, Bilirubin, GGT, Albumin |
| **Kidney Function (KFT)** | 5+ | Creatinine, BUN, Uric Acid, eGFR |
| **Lipid Profile** | 6 | Cholesterol, LDL, HDL, VLDL, Triglycerides |
| **Thyroid Panel** | 5 | TSH, T3, T4, Free T3, Free T4 |
| **Diabetes Panel** | 6 | FBS, PPBS, HbA1c, RBS, Fasting Insulin |
| **Cardiac Markers** | 5 | Troponin, CK-MB, BNP, LDH |
| **Vitamins & Minerals** | 8+ | Vitamin D, B12, Iron, Ferritin, Calcium |
| **Electrolytes** | 6 | Sodium, Potassium, Chloride, Magnesium |
| **Hormones** | 10+ | Cortisol, Testosterone, Estrogen, FSH, LH |
| **Inflammatory** | 6 | ESR, CRP, hs-CRP, RF, ANA |

### Complete Test List

<details>
<summary>Click to expand full test list (70+ tests)</summary>

**Hematology:**
- Hemoglobin, White Blood Cell Count, Red Blood Cell Count
- Platelet Count, Hematocrit, MCV, MCH, MCHC, RDW, MPV
- Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils

**Liver Function:**
- SGPT/ALT, SGOT/AST, ALP, Total Bilirubin, Direct Bilirubin
- GGT, Albumin, Total Protein, Globulin

**Kidney Function:**
- Creatinine, Blood Urea Nitrogen, Uric Acid, eGFR

**Lipid Profile:**
- Total Cholesterol, LDL, HDL, VLDL, Triglycerides, Lipoprotein(a)

**Thyroid:**
- TSH, T3, T4, Free T3, Free T4

**Diabetes:**
- Fasting Blood Sugar, PPBS, HbA1c, RBS, Fasting Insulin, C-Peptide

**Cardiac:**
- Troponin, CK-MB, BNP, LDH, Homocysteine

**Vitamins:**
- Vitamin D, Vitamin B12, Folic Acid, Iron, Ferritin, TIBC

**Electrolytes:**
- Sodium, Potassium, Chloride, Calcium, Magnesium, Phosphorus

**Urine:**
- Urine pH, Specific Gravity, Urine Protein, Urine Glucose, Microalbumin

**Hormones:**
- Cortisol, Testosterone, Estrogen, Prolactin, FSH, LH, AMH

**Inflammatory:**
- ESR, CRP, hs-CRP, Rheumatoid Factor, ANA, Procalcitonin

</details>

---

## 8. Project Structure

```
medical_report_api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   │
│   ├── config/
│   │   ├── config.py           # Configuration loader
│   │   ├── logger.py           # Logging setup
│   │   ├── reference_ranges.json   # 70+ test definitions
│   │   └── explanation_templates.json  # Patient-friendly explanations
│   │
│   └── modules/
│       ├── ocr.py              # OCR & text extraction
│       ├── parser.py           # Test line parsing
│       ├── normalizer.py       # Test name normalization
│       ├── summarizer.py       # Summary & report generation
│       └── pipeline.py         # Main processing orchestrator
│
├── docs/
│   └── DOCUMENTATION.md        # This file
│
├── logs/                       # Application logs
│
├── sample_reports/             # Sample medical reports for testing
│
├── tests/                      # Unit tests
│
├── frontend.html               # Web UI
├── requirements.txt            # Python dependencies
├── run_server.py               # Server startup script
├── start_server.ps1            # PowerShell startup script
├── start_server.bat            # Windows batch startup
└── README.md                   # Quick start guide
```

---

## 9. Module Documentation

### 9.1 OCR Module (`ocr.py`)

**Purpose:** Extract text from images and PDFs

**Key Functions:**

| Function | Input | Output |
|----------|-------|--------|
| `extract_from_image()` | Image path | Raw text lines |
| `extract_from_text()` | Plain text | Parsed test lines |

**Features:**
- Tesseract OCR integration
- Image preprocessing (grayscale, thresholding)
- Multi-line text extraction
- Confidence scoring

---

### 9.2 Parser Module (`parser.py`)

**Purpose:** Parse raw text lines into structured test data

**Key Functions:**

| Function | Input | Output |
|----------|-------|--------|
| `parse_line()` | Single text line | ParsedTest object |
| `parse_multiple_lines()` | List of lines | List of ParsedTest |

**Supported Formats:**
```
Hemoglobin: 12.5 g/dL
WBC Count = 8500 /uL
Glucose (Fasting) - 110 mg/dL
RBC 4.5 million/uL (4.0-6.0)
```

**ParsedTest Object:**
```python
class ParsedTest:
    name: str          # "Hemoglobin"
    value: float       # 12.5
    unit: str          # "g/dL"
    raw_line: str      # Original text
    confidence: float  # 0.0 - 1.0
```

---

### 9.3 Normalizer Module (`normalizer.py`)

**Purpose:** Standardize test names and determine status

**Key Functions:**

| Function | Input | Output |
|----------|-------|--------|
| `normalize_test()` | ParsedTest | Normalized dict |
| `normalize_multiple_tests()` | List of ParsedTest | Normalized results |

**Features:**
- 70+ test alias mappings
- Fuzzy matching (80% threshold)
- Reference range comparison
- Status determination (low/normal/high)

**Example:**
```python
Input:  "hb" → Output: "Hemoglobin"
Input:  "wbc count" → Output: "White Blood Cell Count"
Input:  "fbs" → Output: "Fasting Blood Sugar"
```

---

### 9.4 Summarizer Module (`summarizer.py`)

**Purpose:** Generate patient-friendly summaries and rich reports

**Key Functions:**

| Function | Input | Output |
|----------|-------|--------|
| `generate_summary()` | Normalized tests | Rich report dict |
| `guardrail_check()` | Raw + normalized | Hallucination check |

**Rich Report Structure:**
```python
{
    "title": "Complete Blood Count (CBC)",
    "patient_info": {...},
    "overall_status": "All Clear",
    "test_overviews": [...],
    "interpretations": [...],
    "key_concepts": [...],
    "abnormal_causes": [...],
    "recommendations": [...]
}
```

---

### 9.5 Pipeline Module (`pipeline.py`)

**Purpose:** Orchestrate all modules

**Key Functions:**

| Function | Input | Output |
|----------|-------|--------|
| `process_image()` | Image path | Complete result |
| `process_pdf()` | PDF path | Complete result |
| `process_text()` | Plain text | Complete result |

**Pipeline Flow:**
```
Input → OCR → Parser → Normalizer → Guardrail → Summarizer → Output
```

---

## 10. Error Handling

### Status Codes

| Status | Meaning |
|--------|---------|
| `ok` | Processing successful |
| `no_tests_found` | No tests detected in input |
| `parse_failed` | Could not parse any tests |
| `normalization_failed` | Could not normalize tests |
| `error` | Unexpected error |

### Error Response Format

```json
{
  "status": "error",
  "error": "Detailed error message",
  "step": "ocr|parser|normalizer|summarizer"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Tesseract not found` | OCR not installed | Install Tesseract OCR |
| `Unsupported file type` | Wrong file format | Use JPG, PNG, PDF, BMP, TIFF |
| `No tests found` | Poor image quality | Use clearer image or paste text |
| `Parse failed` | Unusual format | Check report format |

---

## 11. Examples & Use Cases

### Example 1: CBC Report Processing

**Input Text:**
```
Complete Blood Count Report

Hemoglobin: 11.2 g/dL
WBC Count: 12500 /uL
RBC Count: 4.5 million/uL
Platelet Count: 280000 /uL
```

**Output:**
```json
{
  "status": "ok",
  "summary": "High White Blood Cell Count. 3 other test(s) are within normal range.",
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 11.2,
      "status": "low",
      "ref_range": {"low": 12.0, "high": 17.5}
    },
    {
      "name": "White Blood Cell Count",
      "value": 12500,
      "status": "high",
      "ref_range": {"low": 4000, "high": 11000}
    }
    // ... more tests
  ],
  "report": {
    "overall_status": "Review Recommended",
    "abnormal_causes": [
      {
        "test_name": "White Blood Cell Count",
        "status": "high",
        "causes": {
          "title": "High WBC Count (Leukocytosis) Causes",
          "causes": [
            "Bacterial infections",
            "Inflammation",
            "Allergic reactions",
            "Stress response"
          ]
        }
      }
    ],
    "recommendations": [
      "Consult with your healthcare provider to discuss these results.",
      "Do not self-diagnose or self-medicate based on these results."
    ]
  }
}
```

### Example 2: Diabetes Panel

**Input:**
```
Fasting Blood Sugar: 126 mg/dL
HbA1c: 7.2 %
Post Prandial Blood Sugar: 185 mg/dL
```

**Output Summary:**
```
High Fasting Blood Sugar, High HbA1c, and High Post Prandial Blood Sugar.

Recommendations:
- Consult with your healthcare provider to discuss these results.
- Monitor your carbohydrate intake and maintain healthy eating habits.
- Regular exercise helps control blood sugar levels.
```

---

## 12. Troubleshooting

### Issue: Tesseract not found

**Symptoms:**
```
WARNING - pytesseract cannot access tesseract binary
```

**Solution:**
1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Set environment variable:
   ```powershell
   $env:TESSERACT_CMD = 'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### Issue: PDF text extraction fails

**Symptoms:**
```
Could not extract text from PDF
```

**Solution:**
1. Ensure PDF is not image-based (scanned)
2. For scanned PDFs, use image upload instead
3. Install PyPDF2: `pip install PyPDF2`

### Issue: Tests not being recognized

**Symptoms:**
- Tests showing as "Unknown"
- Low normalization count

**Solution:**
1. Check test name spelling
2. Use standard test names or aliases
3. Review `reference_ranges.json` for supported tests

### Issue: Port already in use

**Symptoms:**
```
Address already in use
```

**Solution:**
```powershell
# Find and kill process using port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

---

## License

This project is for educational and development purposes.

---

## Support

For issues or feature requests, please contact the development team.

---

**© 2025 AI Medical Report Summarizer - Making Healthcare Accessible**
