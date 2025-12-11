"""
FastAPI Application for Medical Report Simplifier
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from typing import Optional

from app.config.logger import setup_logger
from app.modules.pipeline import MedicalReportPipeline

logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Medical Report Simplifier",
    description="Convert medical lab reports into patient-friendly JSON summaries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = MedicalReportPipeline()

# Log Tesseract availability for debugging
try:
    from app.modules import ocr as ocr_module
    try:
        tesseract_path = None
        import pytesseract
        tesseract_path = getattr(pytesseract, 'pytesseract_cmd', None)
    except Exception:
        tesseract_path = None
    logger.info(f"TESSERACT_AVAILABLE={getattr(ocr_module, 'TESSERACT_AVAILABLE', False)}, TESSERACT_PATH={tesseract_path}")
except Exception:
    logger.debug("Could not determine Tesseract availability at startup")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Medical Report Simplifier API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.modules import ocr as ocr_module
    try:
        tesseract_available = getattr(ocr_module, 'TESSERACT_AVAILABLE', False)
    except Exception:
        tesseract_available = False
    return {
        "status": "healthy",
        "service": "Medical Report Simplifier API",
        "tesseract_available": tesseract_available
    }


@app.post("/simplify-report-text")
async def simplify_report_text(
    text: str = Form(...)
):
    """
    Simplify medical report from text
    
    Args:
        text: Plain text medical report
    
    Returns:
        JSON with normalized tests and patient-friendly summary
    """
    try:
        if not text:
            raise HTTPException(
                status_code=400,
                detail="Text must be provided"
            )
        
        logger.info(f"Processing text input (length: {len(text)})")
        result = pipeline.process_text(text)
        
        # Always return 200 for successful processing, even if no tests found
        # The 'status' field in the response indicates the processing result
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in /simplify-report-text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/simplify-report")
async def simplify_report(
    file: UploadFile = File(...)
):
    """
    Simplify medical report from image or text file
    
    Args:
        file: Image or text file of medical report
    
    Returns:
        JSON with normalized tests and patient-friendly summary
    """
    try:
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.txt', '.pdf']
        _, ext = os.path.splitext(file.filename)
        
        if ext.lower() not in allowed_extensions:
            logger.warning(f"Unsupported file type: {ext}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save temporary file and process
        logger.info(f"Processing file: {file.filename}")
        
        with tempfile.NamedTemporaryFile(
            suffix=ext,
            delete=False
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            temp_path = temp_file.name
        
        try:
            result = pipeline.process_file(temp_path)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        logger.info(f"Request completed with status: {result.get('status')}")
        
        # Always return 200 for successful processing, even if no tests found
        # The 'status' field in the response indicates the processing result
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in /simplify-report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/supported-tests")
async def get_supported_tests():
    """Get list of supported medical tests with reference ranges"""
    try:
        from app.config.config import ConfigLoader
        
        config = ConfigLoader()
        ranges = config.get_reference_ranges()
        
        # Format response as array for frontend compatibility
        tests = []
        for test_name, test_data in ranges['blood_tests'].items():
            tests.append({
                "name": test_name,
                "unit": test_data['unit'],
                "reference_range": test_data['reference_range'],
                "category": test_data.get('category', 'other'),
                "explanation": test_data.get('explanation', ''),
                "aliases": test_data.get('aliases', [])
            })
        
        return {
            "status": "ok",
            "tests": tests,
            "total_tests": len(tests)
        }
        
    except Exception as e:
        logger.error(f"Error fetching supported tests: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching supported tests: {str(e)}"
        )


@app.post("/batch-simplify")
async def batch_simplify(reports: list):
    """
    Process multiple reports in batch
    
    Args:
        reports: List of report text strings
    
    Returns:
        List of processed reports
    """
    try:
        if not reports or not isinstance(reports, list):
            raise HTTPException(
                status_code=400,
                detail="'reports' must be a non-empty list"
            )
        
        if len(reports) > 100:
            raise HTTPException(
                status_code=400,
                detail="Maximum 100 reports per batch"
            )
        
        logger.info(f"Processing batch of {len(reports)} reports")
        
        results = []
        for i, report_text in enumerate(reports):
            try:
                result = pipeline.process_text(report_text)
                result['batch_index'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing batch item {i}: {str(e)}")
                results.append({
                    "batch_index": i,
                    "status": "error",
                    "error": str(e)
                })
        
        logger.info(f"Batch processing completed. Processed {len(results)} reports")
        
        return {
            "status": "ok",
            "total_reports": len(reports),
            "results": results
        }
        
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch processing: {str(e)}"
        )


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
