"""
Unit tests for the normalizer module
"""
import pytest
from app.modules.normalizer import TestNormalizer
from app.modules.parser import ParsedTest


class TestNormalizerTest:
    """Test cases for TestNormalizer"""
    
    def setup_method(self):
        """Setup normalizer instance"""
        self.normalizer = TestNormalizer()
    
    def test_find_canonical_name_exact_match(self):
        """Test finding canonical name with exact match"""
        name = self.normalizer._find_canonical_name("Hemoglobin")
        assert name == "Hemoglobin"
    
    def test_find_canonical_name_alias_match(self):
        """Test finding canonical name from alias"""
        name = self.normalizer._find_canonical_name("hb")
        assert name == "Hemoglobin"
    
    def test_find_canonical_name_fuzzy_match(self):
        """Test finding canonical name with fuzzy matching"""
        # Slight typo
        name = self.normalizer._find_canonical_name("hemoglobbin")
        assert name is not None  # Should fuzzy match to Hemoglobin
    
    def test_compute_status_low(self):
        """Test status computation for low value"""
        status, confidence = self.normalizer._compute_status(
            10.0,
            {"low": 12.0, "high": 15.0}
        )
        
        assert status == "low"
        assert confidence > 0.5
    
    def test_compute_status_high(self):
        """Test status computation for high value"""
        status, confidence = self.normalizer._compute_status(
            16.0,
            {"low": 12.0, "high": 15.0}
        )
        
        assert status == "high"
        assert confidence > 0.5
    
    def test_compute_status_normal(self):
        """Test status computation for normal value"""
        status, confidence = self.normalizer._compute_status(
            13.5,
            {"low": 12.0, "high": 15.0}
        )
        
        assert status == "normal"
        assert confidence > 0.5
    
    def test_compute_status_none_value(self):
        """Test status computation with None value"""
        status, confidence = self.normalizer._compute_status(
            None,
            {"low": 12.0, "high": 15.0}
        )
        
        assert status is None
        assert confidence == 0.0
    
    def test_normalize_test_valid(self):
        """Test normalizing a valid parsed test"""
        parsed = ParsedTest(
            name="Hemoglobin",
            value=10.2,
            unit="g/dL",
            status="low",
            raw_line="Hemoglobin 10.2 g/dL (Low)",
            confidence=0.85
        )
        
        result = self.normalizer.normalize_test(parsed)
        
        assert result['status'] == 'ok'
        assert result['name'] == 'Hemoglobin'
        assert result['value'] == 10.2
        assert result['status'] == 'low'
    
    def test_normalize_test_unknown_name(self):
        """Test normalizing test with unknown name"""
        parsed = ParsedTest(
            name="UnknownTest123",
            value=100,
            unit="unit",
            status=None,
            raw_line="UnknownTest123 100 unit",
            confidence=0.5
        )
        
        result = self.normalizer.normalize_test(parsed)
        
        assert result['status'] == 'failed'
        assert result['normalization_confidence'] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
