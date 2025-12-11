"""
OCR and Text Extraction Module
Handles text extraction from images and PDFs
"""
import os
import re
from typing import Dict, List, Optional
import cv2
import numpy as np
from PIL import Image

from app.config.logger import setup_logger

logger = setup_logger(__name__)

try:
    import pytesseract
    import shutil

    # Allow user to specify Tesseract location via environment variables
    env_tesseract = (
        os.environ.get('TESSERACT_CMD') or
        os.environ.get('TESSERACT_PATH') or
        os.environ.get('TESSERACT')
    )

    # Common installation paths for Windows (can be extended)
    possible_paths = [
        env_tesseract,
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\DELL\AppData\Local\Tesseract-OCR\tesseract.exe',
        r'C:\Users\DELL\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
        r'C:\Users\DELL\AppData\Local\Programs\tesseract-ocr-w64-setup-5.5.0.20241111\tesseract.exe',
    ]

    tesseract_found = False
    for path in possible_paths:
        if not path:
            continue
        if os.path.exists(path):
            # Set the command correctly (pytesseract.pytesseract_cmd)
            try:
                pytesseract.pytesseract_cmd = path
            except Exception:
                # Backwards-compatible fallback
                try:
                    pytesseract.pytesseract.pytesseract_cmd = path
                except Exception:
                    pass
            tesseract_found = True
            logger.info(f"Tesseract found at: {path}")
            TESSERACT_AVAILABLE = True
            break

    if not tesseract_found:
        # Try to find tesseract in PATH
        tesseract_in_path = shutil.which('tesseract') or shutil.which('tesseract.exe')
        if tesseract_in_path:
            try:
                pytesseract.pytesseract_cmd = tesseract_in_path
            except Exception:
                try:
                    pytesseract.pytesseract.pytesseract_cmd = tesseract_in_path
                except Exception:
                    pass
            tesseract_found = True
            logger.info(f"Tesseract found in PATH: {tesseract_in_path}")
            TESSERACT_AVAILABLE = True

    # Verify with pytesseract that the binary is usable
    if tesseract_found:
        try:
            _ = pytesseract.get_tesseract_version()
            logger.info(f"Confirmed Tesseract version: {_}")
            TESSERACT_AVAILABLE = True
        except Exception as ex:
            logger.warning(f"pytesseract cannot access tesseract binary: {ex}")
            TESSERACT_AVAILABLE = False
    else:
        logger.warning("Tesseract executable not found in common paths. OCR may not work.")
        logger.warning("If you installed Tesseract, set the path manually or check installation directory.")
        TESSERACT_AVAILABLE = False

except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available. OCR from images will be limited.")


class OCRProcessor:
    """Process images and extract text using OCR"""
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize OCR processor
        Args:
            confidence_threshold: Minimum confidence level for extracted text
        """
        self.confidence_threshold = confidence_threshold
        self.pytesseract_config = r'--oem 3 --psm 6'
    
    def extract_from_image(self, image_path: str) -> Dict:
        """
        Extract text from image file
        Args:
            image_path: Path to image file
        Returns:
            Dictionary with extracted text and confidence
        """
        try:
            logger.info(f"Extracting text from image: {image_path}")
            
            # Read image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return {
                    "status": "error",
                    "error": "Image file not found",
                    "tests_raw": [],
                    "confidence": 0
                }
            
            # Preprocess image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return {
                    "status": "error",
                    "error": "Failed to read image",
                    "tests_raw": [],
                    "confidence": 0
                }
            
            processed_image = self._preprocess_image(image)
            
            # Extract text
            if not TESSERACT_AVAILABLE:
                logger.warning("Tesseract not available. Install via: https://github.com/UB-Mannheim/tesseract/wiki")
                return {
                    "status": "error",
                    "error": "Tesseract OCR not installed or not found. Please install from https://github.com/UB-Mannheim/tesseract/wiki or set the environment variable TESSERACT_CMD to the path of tesseract.exe",
                    "tests_raw": [],
                    "confidence": 0
                }
            
            try:
                raw_text = pytesseract.image_to_string(
                    processed_image,
                    config=self.pytesseract_config
                )
            except Exception as e:
                logger.error(f"Tesseract error: {str(e)}")
                return {
                    "status": "error",
                    "error": f"Tesseract error: {str(e)}. Install from: https://github.com/UB-Mannheim/tesseract/wiki",
                    "tests_raw": [],
                    "confidence": 0
                }
            
            # Parse test lines
            test_lines = self._parse_test_lines(raw_text)
            
            # Estimate confidence based on text quality
            confidence = self._estimate_confidence(raw_text)
            
            logger.info(f"Extracted {len(test_lines)} test lines with confidence {confidence:.2f}")
            
            return {
                "status": "ok",
                "tests_raw": test_lines,
                "confidence": confidence,
                "raw_text": raw_text
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "tests_raw": [],
                "confidence": 0
            }
    
    def extract_from_text(self, text: str) -> Dict:
        """
        Extract structured test data from plain text
        Args:
            text: Plain text input
        Returns:
            Dictionary with extracted tests and confidence
        """
        try:
            logger.info("Extracting tests from plain text input")
            
            # Parse test lines
            test_lines = self._parse_test_lines(text)
            
            # Confidence is higher for direct text input
            confidence = 0.95 if test_lines else 0.5
            
            logger.info(f"Extracted {len(test_lines)} test lines from text")
            
            return {
                "status": "ok",
                "tests_raw": test_lines,
                "confidence": confidence,
                "raw_text": text
            }
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "tests_raw": [],
                "confidence": 0
            }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        Args:
            image: Input image as numpy array
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE for contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Apply thresholding
            _, thresh = cv2.threshold(enhanced, 150, 255, cv2.THRESH_BINARY)
            
            # Apply morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(processed, None, 10, 10, 21)
            
            logger.debug("Image preprocessing completed")
            return denoised
            
        except Exception as e:
            logger.warning(f"Error in image preprocessing: {str(e)}. Using original image.")
            return image
    
    def _parse_test_lines(self, text: str) -> List[str]:
        """
        Parse test lines from raw text
        Identifies lines containing test results
        Args:
            text: Raw text
        Returns:
            List of parsed test lines
        """
        lines = text.split('\n')
        test_lines = []

        # Skip metadata/header keywords
        non_test_keywords = [
            'address', 'phone', 'ph', 'contact', 'mobile', 'clinic', 'doctor',
            'patient', 'name', 'age', 'sex', 'id', 'invoice', 'bill', 'report',
            'email', 'dob', 'lab', 'registration', 'regno'
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # Skip lines that are clearly metadata/headers
            lower_line = line.lower()
            if any(re.search(rf'\b{re.escape(kw)}\b', lower_line) for kw in non_test_keywords):
                logger.debug(f"Skipping metadata line in OCR extraction: {line}")
                continue
            
            # More flexible approach: look for lines with letters AND numbers
            # This allows the parser module to handle the actual pattern matching
            has_letters = any(c.isalpha() for c in line)
            has_numbers = any(c.isdigit() for c in line)
            
            # If line has both letters and numbers, it might be a test result
            if has_letters and has_numbers:
                cleaned_line = self._clean_ocr_line(line)
                if cleaned_line:
                    test_lines.append(cleaned_line)
        
        return test_lines
    
    def _clean_ocr_line(self, line: str) -> Optional[str]:
        """
        Clean OCR artifacts from a line
        Args:
            line: Raw OCR line
        Returns:
            Cleaned line or None if invalid
        """
        # Remove extra whitespace
        line = ' '.join(line.split())
        
        # Remove common OCR artifacts
        artifacts = ['|', '`', '~', '^', '°']
        for artifact in artifacts:
            line = line.replace(artifact, '')
        
        # Check if line has meaningful content (test + number + unit)
        if any(char.isdigit() for char in line) and len(line) > 5:
            return line
        
        return None
    
    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate confidence of OCR extraction
        Args:
            text: Extracted text
        Returns:
            Confidence score between 0 and 1
        """
        if not text:
            return 0.0
        
        # Check text length
        if len(text) < 20:
            return 0.3
        
        # Check for common medical terms
        medical_keywords = ['hemoglobin', 'wbc', 'glucose', 'cholesterol', 'test', 'blood', 'count']
        text_lower = text.lower()
        
        keyword_count = sum(1 for keyword in medical_keywords if keyword in text_lower)
        
        # Base confidence
        confidence = 0.5
        
        # Increase if medical keywords found
        if keyword_count > 0:
            confidence += (keyword_count / len(medical_keywords)) * 0.3
        
        # Check for numbers
        if any(char.isdigit() for char in text):
            confidence += 0.1
        
        return min(confidence, 1.0)
