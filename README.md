# 🏥 AI Medical Report Summarizer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Tests](https://img.shields.io/badge/Tests-70+-brightgreen.svg)

**Transform complex medical lab reports into easy-to-understand, patient-friendly summaries**

[Features](#-features) • [Supported Reports](#-supported-medical-reports) • [Quick Start](#-quick-start) • [API Docs](#-api-endpoints) • [Demo](#-demo)

</div>

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 📄 **Multi-Format Input** | Supports JPG, PNG, PDF, BMP, TIFF, and plain text |
| 🔍 **OCR Processing** | Extracts text from scanned medical report images |
| 🧠 **Smart Normalization** | Maps 70+ test aliases to standard medical names |
| 📊 **Status Detection** | Identifies Low, Normal, High values automatically |
| 💡 **Patient-Friendly Summaries** | Explains results in simple, understandable language |
| 🏥 **Rich AI Reports** | Generates comprehensive medical summaries |
| ⚠️ **Abnormal Cause Analysis** | Lists possible causes for abnormal results |
| 💊 **Health Recommendations** | Provides actionable health advice |
| 🔒 **Guardrail Protection** | Prevents hallucinated/fabricated test results |
| 📱 **Responsive Frontend** | Works on desktop, tablet, and mobile |
| 🌙 **Dark Mode** | Supports system dark mode preference |
| 🖨️ **Print & Copy** | Print reports or copy summary to clipboard |

---

## 📋 Supported Medical Reports

### **70+ Medical Tests Across 12 Categories**

<details>
<summary><b>🩸 1. Complete Blood Count (CBC) - 15+ Tests</b></summary>

| Test | Aliases |
|------|---------|
| Hemoglobin | Hb, Hgb, Haemoglobin |
| White Blood Cell Count | WBC, TLC, Leucocytes |
| Red Blood Cell Count | RBC, Erythrocytes |
| Platelet Count | PLT, Thrombocytes |
| Hematocrit | HCT, PCV, Packed Cell Volume |
| MCV | Mean Corpuscular Volume |
| MCH | Mean Corpuscular Hemoglobin |
| MCHC | Mean Corpuscular Hemoglobin Concentration |
| RDW | Red Cell Distribution Width |
| MPV | Mean Platelet Volume |
| PDW | Platelet Distribution Width |
| Neutrophils | Neut%, Polymorphs |
| Lymphocytes | Lymph% |
| Monocytes | Mono% |
| Eosinophils | Eos% |
| Basophils | Baso% |

</details>

<details>
<summary><b>🫀 2. Liver Function Test (LFT) - 10+ Tests</b></summary>

| Test | Aliases |
|------|---------|
| SGPT | ALT, Alanine Aminotransferase |
| SGOT | AST, Aspartate Aminotransferase |
| ALP | Alkaline Phosphatase |
| Total Bilirubin | T.Bil, Bilirubin Total |
| Direct Bilirubin | Conjugated Bilirubin |
| Indirect Bilirubin | Unconjugated Bilirubin |
| GGT | Gamma GT, Gamma Glutamyl Transferase |
| Albumin | Serum Albumin |
| Total Protein | TP |
| Globulin | Serum Globulin |
| A/G Ratio | Albumin Globulin Ratio |

</details>

<details>
<summary><b>🫘 3. Kidney Function Test (KFT/RFT) - 5+ Tests</b></summary>

| Test | Aliases |
|------|---------|
| Creatinine | Serum Creatinine |
| Blood Urea Nitrogen | BUN, Urea, Blood Urea |
| Uric Acid | Serum Uric Acid |
| eGFR | Estimated Glomerular Filtration Rate |
| BUN/Creatinine Ratio | Urea Creatinine Ratio |

</details>

<details>
<summary><b>❤️ 4. Lipid Profile - 6 Tests</b></summary>

| Test | Aliases |
|------|---------|
| Total Cholesterol | Cholesterol, TC |
| LDL Cholesterol | LDL, Bad Cholesterol |
| HDL Cholesterol | HDL, Good Cholesterol |
| VLDL Cholesterol | VLDL |
| Triglycerides | TG, Triglyceride |
| Lipoprotein(a) | Lp(a) |

</details>

<details>
<summary><b>🍬 5. Diabetes Panel - 6 Tests</b></summary>

| Test | Aliases |
|------|---------|
| Fasting Blood Sugar | FBS, Glucose Fasting, Blood Sugar Fasting |
| Post Prandial Blood Sugar | PPBS, PP Sugar, PP Glucose |
| Random Blood Sugar | RBS, Random Glucose |
| HbA1c | Glycated Hemoglobin, A1C, Glycosylated Hb |
| Fasting Insulin | Insulin Fasting |
| C-Peptide | C Peptide |

</details>

<details>
<summary><b>🦋 6. Thyroid Panel - 5 Tests</b></summary>

| Test | Aliases |
|------|---------|
| TSH | Thyroid Stimulating Hormone |
| T3 | Triiodothyronine, Total T3 |
| T4 | Thyroxine, Total T4 |
| Free T3 | FT3 |
| Free T4 | FT4 |

</details>

<details>
<summary><b>💓 7. Cardiac Markers - 5 Tests</b></summary>

| Test | Aliases |
|------|---------|
| Troponin | Troponin I, Troponin T, cTnI |
| CK-MB | Creatine Kinase MB |
| BNP | Brain Natriuretic Peptide, NT-proBNP |
| LDH | Lactate Dehydrogenase |
| Homocysteine | Serum Homocysteine |

</details>

<details>
<summary><b>💊 8. Vitamins & Minerals - 8+ Tests</b></summary>

| Test | Aliases |
|------|---------|
| Vitamin D | 25-OH Vitamin D, Cholecalciferol, Vit D |
| Vitamin B12 | Cobalamin, B12 |
| Folic Acid | Folate, Vitamin B9 |
| Iron | Serum Iron, Fe |
| Ferritin | Serum Ferritin |
| TIBC | Total Iron Binding Capacity |
| Transferrin | Transferrin Saturation |
| Zinc | Serum Zinc |

</details>

<details>
<summary><b>⚡ 9. Electrolytes - 6 Tests</b></summary>

| Test | Aliases |
|------|---------|
| Sodium | Na, Serum Sodium |
| Potassium | K, Serum Potassium |
| Chloride | Cl, Serum Chloride |
| Calcium | Ca, Serum Calcium |
| Magnesium | Mg, Serum Magnesium |
| Phosphorus | Phosphate, Serum Phosphorus |

</details>

<details>
<summary><b>🧪 10. Urine Analysis - 5+ Tests</b></summary>

| Test | Aliases |
|------|---------|
| Urine pH | pH |
| Specific Gravity | SG, Urine SG |
| Urine Protein | Proteinuria, Albumin Urine |
| Urine Glucose | Glycosuria, Sugar Urine |
| Microalbumin | Urine Albumin, ACR |
| Urine Creatinine | Creatinine Urine |

</details>

<details>
<summary><b>🧬 11. Hormones - 10+ Tests</b></summary>

| Test | Aliases |
|------|---------|
| Cortisol | Serum Cortisol, Morning Cortisol |
| Testosterone | Total Testosterone, Free Testosterone |
| Estrogen | Estradiol, E2 |
| Progesterone | Serum Progesterone |
| Prolactin | PRL, Serum Prolactin |
| FSH | Follicle Stimulating Hormone |
| LH | Luteinizing Hormone |
| AMH | Anti-Mullerian Hormone |
| DHEA-S | Dehydroepiandrosterone Sulfate |
| Insulin | Fasting Insulin |

</details>

<details>
<summary><b>🔥 12. Inflammatory Markers - 6 Tests</b></summary>

| Test | Aliases |
|------|---------|
| ESR | Erythrocyte Sedimentation Rate |
| CRP | C-Reactive Protein |
| hs-CRP | High Sensitivity CRP |
| Rheumatoid Factor | RF, RA Factor |
| ANA | Antinuclear Antibody |
| Procalcitonin | PCT |

</details>

---

## 📁 Supported File Formats

| Format | Type | Description |
|--------|------|-------------|
| 📷 **JPG/JPEG** | Image | Scanned reports with OCR |
| 🖼️ **PNG** | Image | High-quality scanned reports |
| 📄 **PDF** | Document | Digital or scanned PDFs |
| 🎨 **BMP** | Image | Bitmap images |
| 📸 **TIFF** | Image | High-resolution scans |
| 📝 **Text** | Plain Text | Copy-paste report text |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (recommended 3.12)
- **Tesseract OCR** (for image processing)

### Installation

```bash
# Clone the repository
git clone https://github.com/anirudhpal2807/Plum_assignment.git
cd Plum_assignment

# Install dependencies
pip install -r requirements.txt
```

### Install Tesseract OCR

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

### Run the Server

```powershell
# Set Tesseract path (Windows)
$env:TESSERACT_CMD = 'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Start server
python run_server.py
```

Or use the start script:
```powershell
.\start_server.ps1
```

### Access the Application

| URL | Description |
|-----|-------------|
| `frontend.html` | Open in browser for Web UI |
| http://localhost:8000/docs | Swagger API Documentation |
| http://localhost:8000/redoc | ReDoc API Documentation |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Detailed health status |
| `POST` | `/simplify-report` | Process image/PDF file |
| `POST` | `/simplify-report-text` | Process text input |
| `GET` | `/supported-tests` | List all 70+ supported tests |
| `POST` | `/batch-simplify` | Process multiple reports |

### Example Request

```bash
curl -X POST "http://localhost:8000/simplify-report-text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Hemoglobin: 12.5 g/dL%0AWBC: 8500 /uL%0APlatelets: 250000 /uL"
```

### Example Response

```json
{
  "status": "ok",
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 12.5,
      "unit": "g/dL",
      "status": "normal",
      "ref_range": {"low": 12.0, "high": 17.5}
    }
  ],
  "summary": "All 3 test result(s) are within normal ranges.",
  "report": {
    "title": "Complete Blood Count (CBC)",
    "overall_status": "All Clear",
    "recommendations": [
      "Continue maintaining your healthy lifestyle."
    ]
  }
}
```

---

## 🎯 Demo

### Web Interface

1. Open `frontend.html` in your browser
2. Choose **File Upload** or **Text Paste** tab
3. Upload your medical report or paste text
4. Click **Analyze Report**
5. View results with:
   - 📊 Results Table (with status badges)
   - 📝 Summary
   - 💡 Explanations
   - 🏥 Rich AI Report
   - ⚠️ Abnormal Causes (if any)
   - 💊 Recommendations

---

## 📂 Project Structure

```
medical_report_api/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── config/
│   │   ├── config.py              # Configuration loader
│   │   ├── logger.py              # Logging setup
│   │   ├── reference_ranges.json  # 70+ test definitions
│   │   └── explanation_templates.json
│   └── modules/
│       ├── ocr.py                 # Image text extraction
│       ├── parser.py              # Test line parsing
│       ├── normalizer.py          # Test name matching
│       ├── summarizer.py          # AI summary generation
│       └── pipeline.py            # Main orchestrator
├── docs/
│   └── DOCUMENTATION.md           # Full documentation
├── frontend.html                  # Responsive Web UI
├── requirements.txt               # Python dependencies
├── run_server.py                  # Server startup script
└── README.md                      # This file
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.12** | Backend language |
| **FastAPI** | Web framework |
| **Tesseract OCR** | Image text extraction |
| **PyPDF2** | PDF processing |
| **RapidFuzz** | Fuzzy string matching |
| **OpenCV** | Image preprocessing |
| **HTML/CSS/JS** | Frontend UI |

---

## 📖 Documentation

- [📄 Full Documentation](docs/DOCUMENTATION.md)
- [🔧 API Reference](docs/API_REFERENCE.md)
- [🏗️ Architecture](docs/ARCHITECTURE.md)
- [📋 Setup Guide](docs/SETUP_GUIDE.md)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is for educational and development purposes.

---

<div align="center">

**Made with ❤️ for Healthcare**

⭐ Star this repo if you find it helpful!

</div>
