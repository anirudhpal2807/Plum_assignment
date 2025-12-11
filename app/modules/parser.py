"""
Test Line Parser Module
Parses individual test lines to extract name, value, unit, and status
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.config.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ParsedTest:
    """Represents a parsed test line"""
    name: Optional[str]
    value: Optional[float]
    unit: Optional[str]
    status: Optional[str]  # 'low', 'high', 'normal', or None
    raw_line: str
    confidence: float


class TestLineParser:
    """Parse individual test lines"""
    
    def __init__(self):
        """Initialize parser with regex patterns"""
        # Blacklist for common header/metadata lines that shouldn't be parsed as tests
        self.non_test_keywords = [
            'address', 'phone', 'contact', 'mobile', 'clinic', 'doctor', 'dr.',
            'patient', 'name', 'age', 'sex', 'gender', 'id', 'invoice', 'bill', 
            'report', 'email', 'dob', 'lab', 'registration', 'regno', 'date',
            'page', 'generated', 'printed', 'collected', 'reported', 'registered',
            'sample', 'specimen', 'pid', 'visit', 'ref no', 'number',
            'hospital', 'center', 'centre', 'healthcare', 'diagnostic', 'pathology',
            'time', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 
            'aug', 'sep', 'oct', 'nov', 'dec', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday', 'road', 'street', 'avenue',
            'city', 'state', 'pin', 'zip', 'complex', 'bungalow', 'floor', 'building',
            'deficiency', 'deficiencies', 'instrument', 'method', 'methodology',
            'technician', 'pathologist', 'signature', 'verified', 'approved'
        ]
        
        # Valid medical test units
        self.valid_units = [
            'g/dl', 'g/l', 'mg/dl', 'mg/l', 'ug/dl', 'ng/dl', 'pg/ml', 'ng/ml',
            'mmol/l', 'umol/l', 'meq/l', 'iu/l', 'u/l', 'iu/ml', 'miu/ml',
            '%', 'mm/hr', 'sec', 'seconds', 'minutes', 'fl', 'pg',
            '/ul', '/cumm', '/mm3', 'cells/ul', 'cells/cumm', 
            'mill/cumm', 'million/ul', 'million/cumm', 'lac/cumm', 'lakh/cumm',
            'thou/ul', 'thousand/ul', 'k/ul', 'x10^3/ul', 'x10^6/ul', 'x10^9/l',
            'ratio', 'index', 'score'
        ]
        
        # Known medical test name patterns
        self.known_test_patterns = [
            r'hemoglobin|haemoglobin|hgb|hb\b',
            r'wbc|white\s*blood\s*cell|leukocyte|leucocyte',
            r'rbc|red\s*blood\s*cell|erythrocyte',
            r'platelet|plt|thrombocyte',
            r'hematocrit|haematocrit|hct|pcv',
            r'mcv|mch|mchc|rdw|mpv|pdw|pct|p-lcr|plcr',
            r'neutrophil|lymphocyte|monocyte|eosinophil|basophil',
            r'glucose|sugar|fbs|fasting|ppbs|random',
            r'cholesterol|triglyceride|ldl|hdl|vldl',
            r'creatinine|urea|bun|blood\s*urea',
            r'bilirubin|sgpt|sgot|alt|ast|alp|alkaline\s*phosphatase',
            r'protein|albumin|globulin',
            r'sodium|potassium|chloride|calcium|magnesium|phosphorus',
            r'tsh|t3|t4|thyroid',
            r'uric\s*acid|urate',
            r'iron|ferritin|tibc',
            r'vitamin|folate|folic',
            r'hba1c|glycated|glycosylated',
            r'esr|sed\s*rate|sedimentation',
            r'psa|prostate',
            r'ck|cpk|ldh|troponin',
            r'amylase|lipase',
            r'ggt|gamma',
            r'inr|pt|ptt|aptt|prothrombin',
            r'total\s*count|differential\s*count|dc\b|tc\b'
        ]
    
    def _is_likely_test_line(self, line: str) -> bool:
        """Check if a line is likely to contain a medical test"""
        lower = line.lower().strip()
        
        # Skip very short or very long lines
        if len(lower) < 5 or len(lower) > 200:
            return False
        
        # Skip lines that are primarily numeric (like phone numbers, dates)
        digit_ratio = sum(c.isdigit() for c in line) / len(line) if line else 0
        if digit_ratio > 0.6:
            return False
        
        # Skip lines containing blacklisted keywords
        for kw in self.non_test_keywords:
            if re.search(rf'\b{re.escape(kw)}\b', lower):
                logger.debug(f"Skipping line with keyword '{kw}': {line[:50]}")
                return False
        
        # Check if line contains known test patterns
        for pattern in self.known_test_patterns:
            if re.search(pattern, lower):
                return True
        
        # Check if line contains valid units
        for unit in self.valid_units:
            if unit.lower() in lower:
                return True
        
        # Check if line has the structure: text + number + optional unit
        if re.search(r'[a-zA-Z]+\s+[\d.]+', line):
            return True
        
        return False
    
    def parse_line(self, line: str) -> ParsedTest:
        """
        Parse a single test line
        Args:
            line: Test line to parse
        Returns:
            ParsedTest object with extracted information
        """
        line = line.strip()
        logger.debug(f"Parsing line: {line}")
        
        # First check if this is likely a test line
        if not self._is_likely_test_line(line):
            logger.debug(f"Skipping non-test line: {line[:50]}")
            return ParsedTest(None, None, None, None, line, 0.0)
        
        # Try multiple parsing strategies
        result = self._try_parse_standard_format(line)
        if result and result.value is not None:
            return result
        
        result = self._try_parse_with_reference(line)
        if result and result.value is not None:
            return result
        
        result = self._try_parse_colon_format(line)
        if result and result.value is not None:
            return result
        
        logger.debug(f"Could not parse line: {line}")
        return ParsedTest(None, None, None, None, line, 0.0)
    
    def _try_parse_standard_format(self, line: str) -> Optional[ParsedTest]:
        """Parse: Test Name Value Unit (Status)"""
        # Clean line - replace comma separators in test names
        clean_line = re.sub(r',\s*', ' ', line)
        
        # Pattern: Test name followed by value, optional unit, optional status
        pattern = r'^([A-Za-z][A-Za-z\s\(\)\-]+?)\s+([\d.,]+)\s*([a-zA-Z%/\-\s\^0-9]*?)(?:\s*[\(\[]?(Low|High|Normal|low|high|normal|LOW|HIGH|NORMAL)[\)\]]?)?$'
        
        match = re.search(pattern, clean_line)
        if match:
            test_name = match.group(1).strip()
            value_str = match.group(2).strip().replace(',', '')
            unit = match.group(3).strip() if match.group(3) else ""
            status = match.group(4).lower() if match.group(4) else None
            
            # Clean up unit - remove trailing numbers that might be reference range
            unit = re.sub(r'\s*[\d.-]+\s*-?\s*[\d.]*$', '', unit).strip()
            
            try:
                value = float(value_str)
                confidence = self._calculate_confidence(test_name, value, unit, status)
                logger.debug(f"Parsed (standard): {test_name} = {value} {unit} ({status})")
                return ParsedTest(test_name, value, unit, status, line, confidence)
            except ValueError:
                pass
        return None
    
    def _try_parse_with_reference(self, line: str) -> Optional[ParsedTest]:
        """Parse: Test Name Value RefLow - RefHigh Unit"""
        # Clean line - replace comma separators in test names
        clean_line = re.sub(r',\s*', ' ', line)
        
        # Pattern for lines like: "Total RBC count 5.2 4.5 - 5.5 mill/cumm"
        pattern = r'^([A-Za-z][A-Za-z\s\(\)\-]+?)\s+([\d.,]+)\s+[\d.,]+\s*[-–]\s*[\d.,]+\s+([a-zA-Z%/\-\s\^0-9]+)$'
        
        match = re.search(pattern, clean_line)
        if match:
            test_name = match.group(1).strip()
            value_str = match.group(2).strip().replace(',', '')
            unit = match.group(3).strip()
            
            try:
                value = float(value_str)
                confidence = self._calculate_confidence(test_name, value, unit, None)
                logger.debug(f"Parsed (with ref): {test_name} = {value} {unit}")
                return ParsedTest(test_name, value, unit, None, line, confidence)
            except ValueError:
                pass
        return None
    
    def _try_parse_colon_format(self, line: str) -> Optional[ParsedTest]:
        """Parse: Test Name: Value Unit"""
        pattern = r'^([A-Za-z][A-Za-z\s\(\)]+?):\s*([\d.,]+)\s*([a-zA-Z%/\-\s\^0-9]*)$'
        
        match = re.search(pattern, line)
        if match:
            test_name = match.group(1).strip()
            value_str = match.group(2).strip().replace(',', '')
            unit = match.group(3).strip() if match.group(3) else ""
            
            try:
                value = float(value_str)
                confidence = self._calculate_confidence(test_name, value, unit, None)
                logger.debug(f"Parsed (colon): {test_name} = {value} {unit}")
                return ParsedTest(test_name, value, unit, None, line, confidence)
            except ValueError:
                pass
        return None
    
    def parse_multiple_lines(self, lines: List[str]) -> List[ParsedTest]:
        """
        Parse multiple test lines
        Args:
            lines: List of test lines
        Returns:
            List of ParsedTest objects
        """
        parsed_tests = []
        
        for line in lines:
            line = line.strip()
            if line:
                parsed = self.parse_line(line)
                if parsed.value is not None:  # Only add successfully parsed tests
                    parsed_tests.append(parsed)
        
        logger.info(f"Parsed {len(parsed_tests)} valid test lines")
        return parsed_tests
    
    def _calculate_confidence(
        self, 
        test_name: str, 
        value: Optional[float], 
        unit: str, 
        status: Optional[str]
    ) -> float:
        """
        Calculate confidence score for parsed test
        """
        confidence = 0.5
        
        # Check if test name matches known patterns
        lower_name = test_name.lower()
        for pattern in self.known_test_patterns:
            if re.search(pattern, lower_name):
                confidence += 0.2
                break
        
        # Check if unit is valid
        if unit:
            for valid_unit in self.valid_units:
                if valid_unit.lower() in unit.lower():
                    confidence += 0.15
                    break
        
        # Increase confidence if value is in reasonable range
        if value is not None:
            if 0 < value < 100000:
                confidence += 0.1
        
        # Increase confidence if status is present
        if status:
            confidence += 0.05
        
        return min(confidence, 1.0)
