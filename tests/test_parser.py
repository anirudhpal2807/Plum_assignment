"""
Unit tests for the parser module
"""
import pytest
from app.modules.parser import TestLineParser, ParsedTest


class TestLineParserTest:
    """Test cases for TestLineParser"""
    
    def setup_method(self):
        """Setup parser instance"""
        self.parser = TestLineParser()
    
    def test_parse_valid_line(self):
        """Test parsing a valid test line"""
        line = "Hemoglobin 10.2 g/dL (Low)"
        result = self.parser.parse_line(line)
        
        assert result.name == "Hemoglobin"
        assert result.value == 10.2
        assert result.unit == "g/dL"
        assert result.status == "low"
        assert result.confidence > 0.5
    
    def test_parse_line_without_status(self):
        """Test parsing line without status indicator"""
        line = "WBC 11200 /uL"
        result = self.parser.parse_line(line)
        
        assert result.name == "WBC"
        assert result.value == 11200
        assert result.unit == "/uL"
        assert result.status is None
    
    def test_parse_line_with_high_status(self):
        """Test parsing line with HIGH status"""
        line = "Glucose 125 mg/dL (High)"
        result = self.parser.parse_line(line)
        
        assert result.name == "Glucose"
        assert result.value == 125
        assert result.status == "high"
    
    def test_parse_invalid_line(self):
        """Test parsing invalid line"""
        line = "This is not a valid test line"
        result = self.parser.parse_line(line)
        
        assert result.name is None
        assert result.value is None
        assert result.confidence == 0.0
    
    def test_parse_multiple_lines(self):
        """Test parsing multiple lines"""
        lines = [
            "Hemoglobin 10.2 g/dL (Low)",
            "WBC 11200 /uL (High)",
            "Glucose 125 mg/dL"
        ]
        
        results = self.parser.parse_multiple_lines(lines)
        
        assert len(results) == 3
        assert results[0].name == "Hemoglobin"
        assert results[1].name == "WBC"
        assert results[2].name == "Glucose"
    
    def test_extract_numeric_value(self):
        """Test numeric value extraction"""
        # Standard format
        value = self.parser.extract_numeric_value("10.2")
        assert value == 10.2
        
        # Comma separator
        value = self.parser.extract_numeric_value("1,200")
        assert value == 1200.0
        
        # With text
        value = self.parser.extract_numeric_value("Value: 99.5")
        assert value == 99.5
    
    def test_confidence_calculation(self):
        """Test confidence calculation"""
        confidence = self.parser._calculate_confidence(
            "Hemoglobin",
            10.2,
            "g/dL",
            "low"
        )
        
        assert 0.5 <= confidence <= 1.0
    
    def test_parse_empty_line(self):
        """Test parsing empty line"""
        result = self.parser.parse_line("")
        
        assert result.name is None
        assert result.value is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
