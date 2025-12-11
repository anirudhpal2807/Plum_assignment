"""
Main Pipeline Orchestrator
Coordinates all modules to process medical reports
"""
from typing import Dict, Optional
import os

from app.config.logger import setup_logger
from app.modules.ocr import OCRProcessor
from app.modules.parser import TestLineParser
from app.modules.normalizer import TestNormalizer
from app.modules.summarizer import SummaryGenerator

logger = setup_logger(__name__)


class MedicalReportPipeline:
    """Main pipeline for processing medical reports"""
    
    def __init__(self):
        """Initialize all pipeline components"""
        self.ocr_processor = OCRProcessor()
        self.parser = TestLineParser()
        self.normalizer = TestNormalizer()
        self.summary_generator = SummaryGenerator()
    
    def process_image(self, image_path: str) -> Dict:
        """
        Process a medical report image
        Args:
            image_path: Path to image file
        Returns:
            Final processed output
        """
        logger.info(f"Starting pipeline for image: {image_path}")
        
        # Step 1: OCR extraction
        ocr_result = self.ocr_processor.extract_from_image(image_path)
        
        if ocr_result['status'] != 'ok':
            logger.error(f"OCR failed: {ocr_result.get('error', 'Unknown error')}")
            return {
                "status": "error",
                "error": ocr_result.get('error', 'OCR extraction failed'),
                "step": "ocr"
            }
        
        return self._process_tests(ocr_result)
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Process a medical report PDF
        Args:
            pdf_path: Path to PDF file
        Returns:
            Final processed output
        """
        try:
            import PyPDF2
            
            logger.info(f"Starting PDF extraction: {pdf_path}")
            
            # Extract text from PDF
            extracted_text = ""
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                logger.info(f"PDF has {num_pages} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        extracted_text += page_text + "\n"
                        logger.debug(f"Extracted text from page {page_num + 1}")
                    except Exception as e:
                        logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
            
            if not extracted_text.strip():
                logger.warning("No text could be extracted from PDF")
                return {
                    "status": "error",
                    "error": "Could not extract text from PDF",
                    "tests": []
                }
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
            
            # Process extracted text using the standard text processing pipeline
            return self.process_text(extracted_text)
            
        except ImportError:
            logger.error("PyPDF2 not installed. Cannot process PDF files.")
            return {
                "status": "error",
                "error": "PDF support not installed. Install PyPDF2: pip install PyPDF2",
                "tests": []
            }
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return {
                "status": "error",
                "error": f"PDF processing failed: {str(e)}",
                "tests": []
            }
    
    def process_text(self, text: str) -> Dict:
        """
        Process plain text medical report
        Args:
            text: Plain text input
        Returns:
            Final processed output
        """
        logger.info("Starting pipeline for text input")
        
        # Step 1: Text extraction (just parsing)
        ocr_result = self.ocr_processor.extract_from_text(text)
        
        if ocr_result['status'] != 'ok':
            logger.error(f"Text extraction failed: {ocr_result.get('error', 'Unknown error')}")
            return {
                "status": "error",
                "error": ocr_result.get('error', 'Text extraction failed'),
                "step": "extraction"
            }
        
        return self._process_tests(ocr_result)
    
    def _process_tests(self, extraction_result: Dict) -> Dict:
        """
        Process extracted tests through normalization and summarization
        Args:
            extraction_result: Result from OCR/text extraction
        Returns:
            Final processed output
        """
        try:
            tests_raw = extraction_result.get('tests_raw', [])
            extraction_confidence = extraction_result.get('confidence', 0)
            
            if not tests_raw:
                logger.warning("No tests extracted from input")
                return {
                    "status": "no_tests_found",
                    "tests": [],
                    "summary": "No test results were found in the provided input.",
                    "extraction_confidence": extraction_confidence,
                    "step": "extraction"
                }
            
            # Step 2: Parse test lines
            logger.info(f"Parsing {len(tests_raw)} test lines")
            parsed_tests = self.parser.parse_multiple_lines(tests_raw)
            
            # Filter out unparsed tests
            valid_parsed_tests = [t for t in parsed_tests if t.value is not None]
            
            if not valid_parsed_tests:
                logger.warning("No valid tests parsed")
                return {
                    "status": "parse_failed",
                    "tests": [],
                    "summary": "Could not parse any valid tests from the input.",
                    "extraction_confidence": extraction_confidence,
                    "step": "parser"
                }
            
            logger.info(f"Successfully parsed {len(valid_parsed_tests)} tests")
            
            # Step 3: Normalize tests
            logger.info("Normalizing test data")
            normalization_result = self.normalizer.normalize_multiple_tests(valid_parsed_tests)
            
            if normalization_result['status'] != 'ok' or not normalization_result.get('tests'):
                logger.warning(f"Normalization failed or no tests normalized: {normalization_result}")
                return {
                    "status": "normalization_failed",
                    "tests": normalization_result.get('tests', []),
                    "failed_tests": normalization_result.get('failed_tests', []),
                    "summary": "Could not normalize any tests.",
                    "normalization_confidence": normalization_result.get('normalization_confidence', 0),
                    "step": "normalizer"
                }
            
            normalized_tests = normalization_result.get('tests', [])
            logger.info(f"Successfully normalized {len(normalized_tests)} tests")
            
            # Map test_status to status for summarizer compatibility
            # Always use test_status (low/high/normal) as the status field for summarizer
            for test in normalized_tests:
                if 'test_status' in test:
                    test['status'] = test['test_status']
            
            # Step 4: Guardrail check for hallucinated tests
            logger.info("Running guardrail checks")
            guardrail_result = self.summary_generator.guardrail_check(tests_raw, normalized_tests)
            
            if guardrail_result.get('hallucinated_tests'):
                logger.warning(f"Hallucinated tests detected: {guardrail_result['hallucinated_tests']}")
                # Filter out hallucinated tests
                normalized_tests = [
                    t for t in normalized_tests 
                    if t['name'] not in guardrail_result['hallucinated_tests']
                ]
            
            # Step 5: Generate summary
            logger.info("Generating patient-friendly summary")
            summary_result = self.summary_generator.generate_summary(normalized_tests)
            
            # Build final output
            final_output = {
                "status": "ok",
                "tests": normalized_tests,
                "summary": summary_result.get('summary', ''),
                "explanations": summary_result.get('explanations', []),
                "tests_summary": summary_result.get('tests_summary', []),
                "metadata": {
                    "extraction_confidence": round(extraction_confidence, 2),
                    "normalization_confidence": round(
                        normalization_result.get('normalization_confidence', 0), 2
                    ),
                    "total_tests_extracted": len(tests_raw),
                    "total_tests_parsed": len(valid_parsed_tests),
                    "total_tests_normalized": len(normalized_tests),
                    "failed_tests": normalization_result.get('failed_tests', []),
                    "guardrail_warnings": guardrail_result.get('hallucinated_tests', [])
                }
            }
            
            logger.info(f"Pipeline completed successfully. Processed {len(normalized_tests)} tests")
            
            return final_output
            
        except Exception as e:
            logger.error(f"Error in pipeline: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "tests": [],
                "summary": ""
            }
    
    def process_file(self, file_path: str) -> Dict:
        """
        Process any file (image, PDF, or text)
        Args:
            file_path: Path to file
        Returns:
            Final processed output
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {
                "status": "error",
                "error": "File not found",
                "tests": []
            }
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Handle image files
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return self.process_image(file_path)
        
        # Handle PDF files
        elif ext in ['.pdf']:
            return self.process_pdf(file_path)
        
        # Handle text files
        elif ext in ['.txt']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                return self.process_text(text)
            except Exception as e:
                logger.error(f"Error reading text file: {str(e)}")
                return {
                    "status": "error",
                    "error": f"Could not read text file: {str(e)}",
                    "tests": []
                }
        
        else:
            return {
                "status": "error",
                "error": f"Unsupported file type: {ext}",
                "tests": []
            }
