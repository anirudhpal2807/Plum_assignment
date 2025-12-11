# API Reference Documentation

## Base URL

```
http://localhost:8000
```

For production, replace with your domain:
```
https://api.yourdomain.com
```

## Authentication

Currently, the API is public. For production, implement:
- API Key authentication
- JWT tokens
- OAuth 2.0

## Response Format

All responses are JSON with standard structure:

```json
{
  "status": "ok|error|warning",
  "data": {},
  "metadata": {}
}
```

---

## Endpoints

### 1. Health Check

#### GET /

Get API status and version info.

**Request:**
```bash
curl -X GET "http://localhost:8000/"
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Medical Report Simplifier API",
  "version": "1.0.0"
}
```

---

### 2. Process Medical Report

#### POST /simplify-report

Convert medical report to structured JSON.

**Supported Input Types:**
- Plain text medical report
- Image files (JPG, PNG, BMP, TIFF)
- (Future: PDF, DOCX)

**Request - Text Input:**

```bash
curl -X POST "http://localhost:8000/simplify-report" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Hemoglobin 10.2 g/dL (Low)
WBC 11200 /uL (High)
Glucose 125 mg/dL"
```

**Request - File Upload:**

```bash
curl -X POST "http://localhost:8000/simplify-report" \
  -F "file=@blood_report.jpg"
```

**Request - Python:**

```python
import requests

# Text input
response = requests.post(
    "http://localhost:8000/simplify-report",
    data={"text": "Hemoglobin 10.2 g/dL (Low)"}
)

# File input
with open("blood_report.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/simplify-report",
        files=files
    )

result = response.json()
print(result)
```

**Parameters:**

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| text      | string | No*      | Plain text medical report |
| file      | file   | No*      | Image/document file |

*Either `text` or `file` is required (not both)

**Supported File Types:**
- `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff` (images)
- `.txt` (plain text)
- `.pdf` (future support)

**File Size Limits:**
- Images: Max 10 MB
- Text: Max 1 MB

**Response (200 OK) - Success:**

```json
{
  "status": "ok",
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 10.2,
      "unit": "g/dL",
      "status": "low",
      "ref_range": {
        "low": 12.0,
        "high": 15.0
      },
      "category": "hematology",
      "normalization_confidence": 0.89,
      "parse_confidence": 0.85
    },
    {
      "name": "White Blood Cell Count",
      "value": 11200,
      "unit": "/uL",
      "status": "high",
      "ref_range": {
        "low": 4000,
        "high": 11000
      },
      "category": "hematology",
      "normalization_confidence": 0.92,
      "parse_confidence": 0.88
    }
  ],
  "summary": "Low hemoglobin and high white blood cell count.",
  "explanations": [
    {
      "test_name": "Hemoglobin",
      "status": "low",
      "value": 10.2,
      "unit": "g/dL",
      "reference_range": {
        "low": 12.0,
        "high": 15.0
      },
      "explanation": "Low hemoglobin may indicate anemia, which can cause fatigue and weakness. Consult your doctor for proper evaluation."
    },
    {
      "test_name": "White Blood Cell Count",
      "status": "high",
      "value": 11200,
      "unit": "/uL",
      "reference_range": {
        "low": 4000,
        "high": 11000
      },
      "explanation": "High WBC can occur with infections, inflammation, stress, or certain conditions. Only a doctor can determine the cause."
    }
  ],
  "tests_summary": [
    {
      "name": "Hemoglobin",
      "value": 10.2,
      "unit": "g/dL",
      "status": "low",
      "reference_low": 12.0,
      "reference_high": 15.0,
      "category": "hematology"
    },
    {
      "name": "White Blood Cell Count",
      "value": 11200,
      "unit": "/uL",
      "status": "high",
      "reference_low": 4000,
      "reference_high": 11000,
      "category": "hematology"
    }
  ],
  "metadata": {
    "extraction_confidence": 0.92,
    "normalization_confidence": 0.90,
    "total_tests_extracted": 2,
    "total_tests_parsed": 2,
    "total_tests_normalized": 2,
    "failed_tests": [],
    "guardrail_warnings": []
  }
}
```

**Response (400 Bad Request):**

```json
{
  "status": "error",
  "error": "Either 'text' or 'file' must be provided"
}
```

**Response (500 Internal Server Error):**

```json
{
  "status": "error",
  "error": "Internal server error: [description]",
  "tests": [],
  "summary": ""
}
```

**Status Codes:**
- `200`: Success - tests extracted and processed
- `400`: Bad request - invalid input
- `500`: Server error - processing failed

---

### 3. Get Supported Tests

#### GET /supported-tests

Retrieve all supported blood tests with reference ranges.

**Request:**
```bash
curl -X GET "http://localhost:8000/supported-tests"
```

**Response (200 OK):**

```json
{
  "status": "ok",
  "tests": {
    "Hemoglobin": {
      "unit": "g/dL",
      "reference_range": {
        "low": 12.0,
        "high": 15.0
      },
      "category": "hematology",
      "explanation": "Hemoglobin is the protein in red blood cells that carries oxygen",
      "aliases": ["hemoglobin", "hb", "hgb", "hemoglobln"]
    },
    "White Blood Cell Count": {
      "unit": "/uL",
      "reference_range": {
        "low": 4000,
        "high": 11000
      },
      "category": "hematology",
      "explanation": "WBC helps your body fight infections and stress",
      "aliases": ["wbc", "white blood cell", "wbc count", "leukocyte"]
    },
    "Blood Glucose": {
      "unit": "mg/dL",
      "reference_range": {
        "low": 70,
        "high": 100
      },
      "category": "metabolic",
      "explanation": "Blood glucose measures sugar levels in your bloodstream",
      "aliases": ["glucose", "fasting glucose", "blood sugar", "fbs"]
    },
    "...": {}
  },
  "total_tests": 20
}
```

**Parameters:** None

**Use Cases:**
- Display list of supported tests to user
- Validate test names
- Show reference ranges
- Populate autocomplete fields

---

### 4. Batch Processing

#### POST /batch-simplify

Process multiple reports in a single request.

**Request:**

```bash
curl -X POST "http://localhost:8000/batch-simplify" \
  -H "Content-Type: application/json" \
  -d '{
    "reports": [
      "Hemoglobin 10.2 g/dL (Low)",
      "WBC 11200 /uL (High)",
      "Glucose 125 mg/dL"
    ]
  }'
```

**Request - Python:**

```python
import requests

reports = [
    "Hemoglobin 10.2 g/dL (Low)",
    "WBC 11200 /uL (High)"
]

response = requests.post(
    "http://localhost:8000/batch-simplify",
    json={"reports": reports}
)

result = response.json()
print(result)
```

**Parameters:**

| Parameter | Type           | Required | Description |
|-----------|----------------|----------|-------------|
| reports   | array[string]  | Yes      | List of plain text reports (max 100) |

**Response (200 OK):**

```json
{
  "status": "ok",
  "total_reports": 2,
  "results": [
    {
      "batch_index": 0,
      "status": "ok",
      "tests": [...],
      "summary": "Low hemoglobin.",
      "explanations": [...]
    },
    {
      "batch_index": 1,
      "status": "ok",
      "tests": [...],
      "summary": "High white blood cell count.",
      "explanations": [...]
    }
  ]
}
```

**Status Codes:**
- `200`: Success - batch processed
- `400`: Bad request - invalid format or >100 reports
- `500`: Server error

**Advantages:**
- Single request for multiple reports
- More efficient than sequential API calls
- Atomic operation (all-or-nothing processing)

---

## Error Responses

### Common Error Codes

#### 400 Bad Request

```json
{
  "status": "error",
  "error": "Either 'text' or 'file' must be provided"
}
```

**Causes:**
- No input provided
- Both text and file provided
- File type unsupported
- Invalid request format

#### 413 Request Entity Too Large

```json
{
  "status": "error",
  "error": "File size exceeds maximum (10 MB)"
}
```

#### 422 Unprocessable Entity

```json
{
  "status": "error",
  "error": "Invalid input format"
}
```

#### 500 Internal Server Error

```json
{
  "status": "error",
  "error": "Internal server error: [details]"
}
```

**Causes:**
- OCR failure
- Processing exception
- File I/O error
- Configuration error

---

## Response Fields Explained

### Test Object

```json
{
  "name": "Hemoglobin",           // Canonical test name
  "value": 10.2,                  // Numeric value
  "unit": "g/dL",                 // Unit of measurement
  "status": "low|high|normal",    // Status indicator
  "ref_range": {                  // Reference range
    "low": 12.0,
    "high": 15.0
  },
  "category": "hematology",       // Test category
  "normalization_confidence": 0.89, // 0-1 confidence score
  "parse_confidence": 0.85        // 0-1 confidence score
}
```

### Explanation Object

```json
{
  "test_name": "Hemoglobin",
  "status": "low",
  "value": 10.2,
  "unit": "g/dL",
  "reference_range": {
    "low": 12.0,
    "high": 15.0
  },
  "explanation": "Low hemoglobin may indicate anemia..."
}
```

### Metadata Object

```json
{
  "extraction_confidence": 0.92,       // OCR quality (0-1)
  "normalization_confidence": 0.90,   // Name mapping quality (0-1)
  "total_tests_extracted": 2,         // Raw test count
  "total_tests_parsed": 2,            // Successfully parsed
  "total_tests_normalized": 2,        // Successfully normalized
  "failed_tests": [],                 // Tests that failed
  "guardrail_warnings": []            // Hallucinated tests
}
```

---

## Test Categories

Available test categories:

- **hematology**: Blood cell tests
- **metabolic**: Glucose, electrolytes
- **lipid**: Cholesterol, triglycerides
- **renal**: Kidney function tests
- **hepatic**: Liver function tests
- **electrolytes**: Sodium, potassium, chloride
- **minerals**: Calcium, magnesium, etc.
- **endocrine**: Thyroid, hormones (future)

---

## Rate Limiting (Future)

```
Current: No limits
Planned:
  • 100 requests/minute per IP
  • 1000 requests/hour per API key
  • 10 MB/hour image processing
```

---

## Examples

### Example 1: Complete Text Processing

```bash
curl -X POST "http://localhost:8000/simplify-report" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Hemoglobin%2010.2%20g%2FdL%20%28Low%29%0AWBC%2011200%20%2FuL%20%28High%29%0ABlood%20Glucose%20125%20mg%2FdL"
```

### Example 2: Python Integration

```python
import requests
import json

def process_medical_report(text):
    response = requests.post(
        "http://localhost:8000/simplify-report",
        data={"text": text}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        if result['status'] == 'ok':
            # Process tests
            for test in result['tests']:
                print(f"{test['name']}: {test['value']} {test['unit']} ({test['status']})")
            
            # Show summary
            print("\nSummary:", result['summary'])
            
            # Show explanations
            for exp in result['explanations']:
                print(f"\n{exp['test_name']}: {exp['explanation']}")
        else:
            print("Error:", result.get('error'))
    else:
        print("Request failed:", response.status_code)

# Usage
report = """
Hemoglobin 10.2 g/dL (Low)
WBC 11200 /uL (High)
Glucose 125 mg/dL (High)
Total Cholesterol 220 mg/dL (High)
"""

process_medical_report(report)
```

### Example 3: JavaScript Integration

```javascript
async function processReport(text) {
    const formData = new FormData();
    formData.append('text', text);
    
    try {
        const response = await fetch('http://localhost:8000/simplify-report', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'ok') {
            // Display results
            console.log('Summary:', result.summary);
            console.log('Confidence:', result.metadata.normalization_confidence);
            
            // Process tests
            result.tests.forEach(test => {
                console.log(`${test.name}: ${test.value} ${test.unit}`);
            });
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Usage
const reportText = `Hemoglobin 10.2 g/dL (Low)
WBC 11200 /uL (High)`;
processReport(reportText);
```

---

## Best Practices

### Input Validation
- Validate file size before upload
- Check file type matches extension
- Sanitize text input (remove extra whitespace)

### Error Handling
- Check `status` field first
- Provide user-friendly error messages
- Log errors for debugging
- Implement retry logic for network errors

### Performance
- Use batch endpoint for multiple reports
- Cache supported tests list
- Implement request timeout (30 seconds)
- Show progress indicators for slow operations

### Security
- Use HTTPS in production
- Never log medical data
- Validate all inputs
- Implement rate limiting
- Use authentication/API keys

---

## Changelog

### v1.0.0 (2024-12-08)
- Initial release
- Text and image processing
- 20+ supported tests
- Batch processing
- Full API documentation

---

**Last Updated**: December 8, 2024
