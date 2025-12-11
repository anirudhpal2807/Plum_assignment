# System Architecture & Pipeline Design

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  (Web UI / Mobile App / Third-party Integration)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                    HTTP/REST API
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  POST /simplify-report (Text/File Input)               │    │
│  │  GET  /supported-tests (Reference Data)                │    │
│  │  POST /batch-simplify (Multiple Reports)               │    │
│  │  GET  /health (Status Check)                           │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE ORCHESTRATOR                         │
│  (app/modules/pipeline.py)                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 1. Route to appropriate processor                       │    │
│  │ 2. Sequence module execution                            │    │
│  │ 3. Combine results                                      │    │
│  │ 4. Format final output                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────┬──────────┬──────────┬──────────┬──────────────────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
    ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
    │ OCR  │  │Parser│  │Norm  │  │Summ  │
    └──────┘  └──────┘  └──────┘  └──────┘
       
       • Extract   • Parse  • Fuzzy  • Explain
       • Text      • Values • Match  • Guard
       • Confidence• Status • Map    • Summary
```

## Data Flow Through Pipeline

```
┌─────────────────┐
│  Input          │
│  • Text         │
│  • Image        │
│  • PDF          │
└────────┬────────┘
         │
         ▼
    ╔═════════════════════════════════════════╗
    ║  STEP 1: OCR/TEXT EXTRACTION            ║
    ║  Module: ocr.py                         ║
    ╠═════════════════════════════════════════╣
    ║ Input:  File path or raw text          ║
    ║ Process:                                ║
    ║  • Read image (if needed)               ║
    ║  • Preprocess (denoise, threshold)      ║
    ║  • Apply Tesseract OCR                  ║
    ║  • Parse lines with regex               ║
    ║  • Estimate confidence                  ║
    ║ Output: Raw test lines + confidence     ║
    ║ Example:                                ║
    ║  {                                      ║
    ║    "tests_raw": [                       ║
    ║      "Hemoglobin 10.2 g/dL (Low)",     ║
    ║      "WBC 11200 /uL (High)"            ║
    ║    ],                                   ║
    ║    "confidence": 0.85                   ║
    ║  }                                      ║
    ╚════════────┬─────────────────────────────╝
                 │
                 ▼
    ╔═════════════════════════════════════════╗
    ║  STEP 2: TEST PARSING                   ║
    ║  Module: parser.py                      ║
    ╠═════════════════════════════════════════╣
    ║ Input:  Raw test lines                 ║
    ║ Process:                                ║
    ║  • Extract test components (regex):     ║
    ║    - Test name                          ║
    ║    - Numeric value                      ║
    ║    - Unit of measurement                ║
    ║    - Status indicator (Low/High/Normal) ║
    ║  • Validate components                  ║
    ║  • Calculate confidence per test        ║
    ║ Output: ParsedTest objects              ║
    ║ Example:                                ║
    ║  ParsedTest(                            ║
    ║    name="Hemoglobin",                   ║
    ║    value=10.2,                          ║
    ║    unit="g/dL",                         ║
    ║    status="low",                        ║
    ║    confidence=0.85                      ║
    ║  )                                      ║
    ╚════────────┬────────────────────────────╝
                 │
                 ▼
    ╔═════════════════════════════════════════╗
    ║  STEP 3: NORMALIZATION                  ║
    ║  Module: normalizer.py                  ║
    ╠═════════════════════════════════════════╣
    ║ Input:  ParsedTest objects              ║
    ║ Process:                                ║
    ║  • Find canonical test name:            ║
    ║    1. Exact match                       ║
    ║    2. Alias lookup                      ║
    ║    3. Fuzzy matching (rapidfuzz)        ║
    ║  • Load reference data                  ║
    ║  • Normalize unit                       ║
    ║  • Compute status using ranges          ║
    ║  • Combine confidence scores            ║
    ║ Output: Normalized test dict            ║
    ║ Example:                                ║
    ║  {                                      ║
    ║    "name": "Hemoglobin",                ║
    ║    "value": 10.2,                       ║
    ║    "unit": "g/dL",                      ║
    ║    "status": "low",                     ║
    ║    "ref_range": {                       ║
    ║      "low": 12.0,                       ║
    ║      "high": 15.0                       ║
    ║    },                                   ║
    ║    "normalization_confidence": 0.89     ║
    ║  }                                      ║
    ╚════────────┬────────────────────────────╝
                 │
                 ▼
    ╔═════════════════════════════════════════╗
    ║  STEP 4: GUARDRAIL CHECK                ║
    ║  Module: summarizer.py                  ║
    ╠═════════════════════════════════════════╣
    ║ Input:  Raw tests, normalized tests    ║
    ║ Process:                                ║
    ║  • Check each normalized test           ║
    ║  • Verify existence in raw input        ║
    ║  • Detect hallucinated tests            ║
    ║  • Filter suspicious results            ║
    ║ Output: Validated test set + warnings   ║
    ║ Example:                                ║
    ║  {                                      ║
    ║    "status": "ok|warning",              ║
    ║    "hallucinated_tests": [...]          ║
    ║  }                                      ║
    ╚════────────┬────────────────────────────╝
                 │
                 ▼
    ╔═════════════════════════════════════════╗
    ║  STEP 5: SUMMARY GENERATION             ║
    ║  Module: summarizer.py                  ║
    ╠═════════════════════════════════════════╣
    ║ Input:  Validated tests                ║
    ║ Process:                                ║
    ║  • Group by status (Low/High/Normal)    ║
    ║  • Generate summary text                ║
    ║  • Create explanations per test         ║
    ║  • Use explanation templates            ║
    ║  • Ensure patient-friendly language     ║
    ║ Output: Summary + explanations          ║
    ║ Example:                                ║
    ║  {                                      ║
    ║    "summary": "Low hemoglobin",         ║
    ║    "explanations": [                    ║
    ║      {                                  ║
    ║        "test_name": "Hemoglobin",      ║
    ║        "status": "low",                 ║
    ║        "explanation": "..."             ║
    ║      }                                  ║
    ║    ]                                    ║
    ║  }                                      ║
    ╚════────────┬────────────────────────────╝
                 │
                 ▼
    ┌──────────────────────────┐
    │  FINAL JSON OUTPUT       │
    │  • Tests (array)         │
    │  • Summary (string)      │
    │  • Explanations (array)  │
    │  • Metadata (object)     │
    │  • Status (ok/error)     │
    └──────────────────────────┘
```

## Module Dependencies

```
main.py (FastAPI)
    │
    └── pipeline.py (Orchestrator)
            │
            ├── ocr.py
            │   ├── cv2 (OpenCV)
            │   ├── pytesseract
            │   └── PIL
            │
            ├── parser.py
            │   └── regex, dataclasses
            │
            ├── normalizer.py
            │   ├── rapidfuzz
            │   ├── config.py
            │   └── parser.py
            │
            └── summarizer.py
                └── config.py

config.py
    ├── reference_ranges.json
    └── explanation_templates.json

logger.py
    └── logging module
```

## Confidence Scoring System

```
┌─────────────────────────────────────────────────────┐
│  Overall Pipeline Confidence Calculation            │
│                                                     │
│  = (Extraction + Parsing + Normalization + Status) / 4
│                                                     │
└─────────────────────────────────────────────────────┘

STEP 1: EXTRACTION CONFIDENCE
  • Text length: > 20 chars (+0.15), < 20 chars (+0.03)
  • Medical keywords: +0.03 per keyword
  • Numbers present: +0.1
  • Base: 0.5
  • Range: 0.3 - 1.0

STEP 2: PARSING CONFIDENCE
  • Test name present & > 3 chars: +0.15
  • Value 0-100,000 range: +0.15
  • Unit present: +0.1
  • Status indicator: +0.1
  • Base: 0.5
  • Range: 0.2 - 1.0

STEP 3: NORMALIZATION CONFIDENCE
  • Exact match: 1.0
  • Alias match: 0.95
  • Fuzzy match 90-100%: 0.9
  • Fuzzy match 80-89%: 0.75
  • Not found: 0.0

STEP 4: STATUS CONFIDENCE
  • Normal values center: 0.95
  • Normal values boundary: 0.7-0.85
  • High/Low clearly abnormal: 0.85-0.95
  • High/Low weakly abnormal: 0.65-0.85
```

## Error Handling Flow

```
┌─────────────────┐
│  Input          │
└────────┬────────┘
         │
         ▼
    Is input provided?
    ├─ No → Error 400: "Either text or file required"
    │
    └─ Yes ▼
         Is file valid?
         ├─ No → Error 400: "Unsupported file type"
         │
         └─ Yes ▼
              OCR Extraction successful?
              ├─ No → Error (Step: ocr)
              │       Reason: OCR failure
              │
              └─ Yes ▼
                   Tests parsed?
                   ├─ No → Status: "parse_failed"
                   │
                   └─ Yes ▼
                        Tests normalized?
                        ├─ No → Status: "normalization_failed"
                        │
                        └─ Yes ▼
                             Guardrail check ← Hallucinated tests?
                             ├─ Yes → Filtered + warning
                             │
                             └─ No ▼
                                  Success!
                                  Status: "ok"
```

## Performance Characteristics

```
OPERATION                TIME (typical)    FACTORS
────────────────────────────────────────────────────
Text extraction          0-10ms            None
Image read               50-200ms          Image size
Image preprocessing      100-300ms         Resolution
OCR (Tesseract)         300-1000ms        Text amount
Parsing (regex)          10-50ms           Test count
Normalization            50-200ms          Test count
Summarization            20-50ms           Test count
────────────────────────────────────────────────────
Single text report       50-200ms
Single image report      500ms-2s
Batch of 100 texts       5-20s
────────────────────────────────────────────────────
```

## Scalability Architecture (Future)

```
                    ┌──────────────────┐
                    │  Load Balancer   │
                    └────────┬─────────┘
                             │
        ┌────────────┬────────┼────────┬─────────┐
        │            │        │        │         │
        ▼            ▼        ▼        ▼         ▼
    ┌──────┐    ┌──────┐ ┌──────┐ ┌──────┐  ┌──────┐
    │ API  │    │ API  │ │ API  │ │ API  │  │ API  │
    │ Pod  │    │ Pod  │ │ Pod  │ │ Pod  │  │ Pod  │
    └──────┘    └──────┘ └──────┘ └──────┘  └──────┘
        │            │        │        │         │
        └────────────┴────────┼────────┴─────────┘
                             │
                    ┌────────▼────────┐
                    │   Job Queue     │
                    │  (Redis/RabbitMQ)
                    └────────┬────────┘
                             │
        ┌────────────┬────────┼────────┬─────────┐
        │            │        │        │         │
        ▼            ▼        ▼        ▼         ▼
    ┌──────┐    ┌──────┐ ┌──────┐ ┌──────┐  ┌──────┐
    │Worker│    │Worker│ │Worker│ │Worker│  │Worker│
    │Pool  │    │Pool  │ │Pool  │ │Pool  │  │Pool  │
    └──────┘    └──────┘ └──────┘ └──────┘  └──────┘
        │            │        │        │         │
        └────────────┴────────┼────────┴─────────┘
                             │
                    ┌────────▼────────┐
                    │  Result Cache   │
                    │  (Redis)        │
                    └─────────────────┘
```

## Security Architecture

```
                    ┌──────────────────┐
                    │  HTTPS/TLS       │
                    │  (Certificates)  │
                    └────────┬─────────┘
                             │
                    ┌────────▼──────────┐
                    │ Authentication    │
                    │ (API Key / JWT)   │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │ Rate Limiting     │
                    │ (requests/min)    │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │ Input Validation  │
                    │ (File type/size)  │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │ Data Processing   │
                    │ (No storage)      │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │ Encrypted Output  │
                    │ (Optional)        │
                    └───────────────────┘
```

---

**Last Updated**: December 8, 2024
