"""
Test Normalization Module
Normalizes test names, corrects spelling errors, and computes status
"""
from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process

from app.config.logger import setup_logger
from app.config.config import ConfigLoader
from app.modules.parser import ParsedTest

logger = setup_logger(__name__)


class TestNormalizer:
    """Normalize and standardize test data"""
    
    def __init__(self, fuzzy_threshold: int = 80):
        """
        Initialize normalizer
        Args:
            fuzzy_threshold: Minimum fuzzy match score for accepting corrections
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.config_loader = ConfigLoader()
        self.alias_map = self.config_loader.get_all_aliases()
        self.canonical_names = self.config_loader.get_all_test_names()
    
    def normalize_test(self, parsed_test: ParsedTest) -> Dict:
        """
        Normalize a parsed test
        Args:
            parsed_test: ParsedTest object from parser
        Returns:
            Dictionary with normalized test data
        """
        try:
            # Try exact match first in alias map
            normalized_name = self._find_canonical_name(parsed_test.name)
            
            if not normalized_name:
                logger.warning(f"Could not normalize test name: {parsed_test.name}")
                return {
                    "status": "failed",
                    "reason": f"Unknown test: {parsed_test.name}",
                    "normalization_confidence": 0.0
                }
            
            # Get test configuration
            test_config = self.config_loader.get_test_by_name(normalized_name)
            
            if not test_config:
                logger.warning(f"No configuration found for: {normalized_name}")
                return {
                    "status": "failed",
                    "reason": f"No reference data for: {normalized_name}",
                    "normalization_confidence": 0.0
                }
            
            # Normalize unit
            normalized_unit = test_config.get('unit', parsed_test.unit)
            
            # Compute status
            status, status_confidence = self._compute_status(
                parsed_test.value,
                test_config.get('reference_range', {})
            )
            
            # Calculate overall confidence
            name_confidence = self._calculate_name_confidence(parsed_test.name, normalized_name)
            overall_confidence = (name_confidence + parsed_test.confidence + status_confidence) / 3
            
            logger.debug(f"Normalized {parsed_test.name} -> {normalized_name} (confidence: {overall_confidence:.2f})")
            
            return {
                "status": "ok",
                "name": normalized_name,
                "value": parsed_test.value,
                "unit": normalized_unit,
                "test_status": status,
                "ref_range": {
                    "low": test_config['reference_range']['low'],
                    "high": test_config['reference_range']['high']
                },
                "category": test_config.get('category', 'other'),
                "normalization_confidence": round(overall_confidence, 2),
                "parse_confidence": round(parsed_test.confidence, 2)
            }
            
        except Exception as e:
            import traceback
            logger.error(f"Error normalizing test '{parsed_test.name}': {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "error": str(e),
                "reason": f"Exception: {str(e)}",
                "normalization_confidence": 0.0
            }
    
    def normalize_multiple_tests(self, parsed_tests: List[ParsedTest]) -> Dict:
        """
        Normalize multiple parsed tests
        Args:
            parsed_tests: List of ParsedTest objects
        Returns:
            Dictionary with normalized tests and confidence
        """
        normalized = []
        failed_tests = []
        total_confidence = 0.0
        
        for parsed_test in parsed_tests:
            result = self.normalize_test(parsed_test)
            logger.debug(f"normalize_multiple_tests result for '{parsed_test.raw_line}': {result}")
            
            if result['status'] == 'ok':
                normalized.append(result)
                total_confidence += result['normalization_confidence']
            else:
                failed_tests.append({
                    'raw_line': parsed_test.raw_line,
                    'reason': result.get('reason', result.get('error', 'Unknown error')),
                    'confidence': result['normalization_confidence']
                })
        
        # Calculate average confidence
        avg_confidence = (total_confidence / len(normalized)) if normalized else 0.0
        
        logger.info(f"Normalized {len(normalized)} tests, failed: {len(failed_tests)}")
        
        return {
            "status": "ok" if normalized else "failed",
            "tests": normalized,
            "failed_tests": failed_tests,
            "normalization_confidence": round(avg_confidence, 2),
            "total_tests": len(parsed_tests),
            "successful_tests": len(normalized),
            "failed_count": len(failed_tests)
        }
    
    def _find_canonical_name(self, test_name: Optional[str]) -> Optional[str]:
        """
        Find canonical test name from various forms
        Uses exact match, alias lookup, and fuzzy matching
        Args:
            test_name: Test name to normalize
        Returns:
            Canonical test name or None
        """
        if not test_name:
            return None
        
        # Clean input
        test_name_clean = test_name.strip().lower()
        
        # Check direct match in canonical names
        for canonical in self.canonical_names:
            if canonical.lower() == test_name_clean:
                return canonical
        
        # Check alias map
        if test_name_clean in self.alias_map:
            return self.alias_map[test_name_clean]
        
        # Try fuzzy matching
        best_match = process.extractOne(
            test_name_clean,
            self.canonical_names,
            scorer=fuzz.token_set_ratio
        )
        
        if best_match and best_match[1] >= self.fuzzy_threshold:
            logger.debug(f"Fuzzy match: {test_name} -> {best_match[0]} (score: {best_match[1]})")
            return best_match[0]
        
        # Try fuzzy matching on aliases
        best_alias_match = process.extractOne(
            test_name_clean,
            list(self.alias_map.keys()),
            scorer=fuzz.token_set_ratio
        )
        
        if best_alias_match and best_alias_match[1] >= self.fuzzy_threshold:
            canonical = self.alias_map[best_alias_match[0]]
            logger.debug(f"Fuzzy alias match: {test_name} -> {canonical} (score: {best_alias_match[1]})")
            return canonical
        
        return None
    
    def _compute_status(self, value: Optional[float], ref_range: Dict) -> Tuple[Optional[str], float]:
        """
        Compute test status (Low/High/Normal) based on reference range
        Args:
            value: Numeric value
            ref_range: Reference range with 'low' and 'high' keys
        Returns:
            Tuple of (status, confidence)
        """
        if value is None:
            return None, 0.0
        
        low = ref_range.get('low')
        high = ref_range.get('high')
        
        if low is None or high is None:
            return None, 0.0
        
        # Determine status
        if value < low:
            status = 'low'
        elif value > high:
            status = 'high'
        else:
            status = 'normal'
        
        # Calculate confidence based on proximity to boundary
        if status == 'normal':
            # Calculate distance from boundaries
            lower_dist = abs(value - low) / (high - low)
            upper_dist = abs(high - value) / (high - low)
            min_dist = min(lower_dist, upper_dist)
            # Closer to boundaries = less confident
            confidence = 0.7 + (min_dist * 0.3)
        else:
            # For abnormal values, confidence is high if clearly outside
            range_size = high - low
            distance_from_range = min(abs(value - low), abs(value - high))
            confidence = min(0.95, 0.7 + (distance_from_range / range_size) * 0.25)
        
        return status, round(confidence, 2)
    
    def _calculate_name_confidence(self, original: str, normalized: str) -> float:
        """
        Calculate confidence in name normalization
        Args:
            original: Original test name
            normalized: Normalized test name
        Returns:
            Confidence score between 0 and 1
        """
        if not original or not normalized:
            return 0.0
        
        # Exact match
        if original.lower() == normalized.lower():
            return 1.0
        
        # Check if in alias map
        if original.lower() in self.alias_map:
            if self.alias_map[original.lower()] == normalized:
                return 0.95
        
        # Use fuzzy matching score
        score = fuzz.token_set_ratio(original.lower(), normalized.lower())
        return min(score / 100.0, 1.0)
