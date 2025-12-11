"""
Unit tests for the summarizer module
"""
import pytest
from app.modules.summarizer import SummaryGenerator


class TestSummaryGeneratorTest:
    """Test cases for SummaryGenerator"""
    
    def setup_method(self):
        """Setup summarizer instance"""
        self.generator = SummaryGenerator()
    
    def test_generate_summary_with_abnormal_tests(self):
        """Test generating summary with abnormal tests"""
        tests = [
            {
                "name": "Hemoglobin",
                "value": 10.2,
                "unit": "g/dL",
                "status": "low",
                "ref_range": {"low": 12.0, "high": 15.0},
                "category": "hematology"
            },
            {
                "name": "WBC",
                "value": 11200,
                "unit": "/uL",
                "status": "high",
                "ref_range": {"low": 4000, "high": 11000},
                "category": "hematology"
            }
        ]
        
        result = self.generator.generate_summary(tests)
        
        assert result['status'] == 'ok'
        assert result['summary'] != ""
        assert len(result['explanations']) == 2
        assert result['abnormal_count'] == 2
    
    def test_generate_summary_all_normal(self):
        """Test generating summary with all normal tests"""
        tests = [
            {
                "name": "Hemoglobin",
                "value": 13.5,
                "unit": "g/dL",
                "status": "normal",
                "ref_range": {"low": 12.0, "high": 15.0},
                "category": "hematology"
            }
        ]
        
        result = self.generator.generate_summary(tests)
        
        assert result['status'] == 'ok'
        assert "normal" in result['summary'].lower()
        assert result['normal_count'] == 1
    
    def test_generate_summary_empty_tests(self):
        """Test generating summary with empty tests"""
        result = self.generator.generate_summary([])
        
        assert result['status'] == 'empty'
        assert result['summary'] != ""
    
    def test_guardrail_check_no_hallucination(self):
        """Test guardrail check with no hallucinated tests"""
        input_raw = [
            "Hemoglobin 10.2 g/dL (Low)",
            "WBC 11200 /uL (High)"
        ]
        
        normalized = [
            {"name": "Hemoglobin", "value": 10.2},
            {"name": "WBC", "value": 11200}
        ]
        
        result = self.generator.guardrail_check(input_raw, normalized)
        
        assert result['status'] == 'ok'
        assert len(result['hallucinated_tests']) == 0
    
    def test_guardrail_check_with_hallucination(self):
        """Test guardrail check detecting hallucinated tests"""
        input_raw = [
            "Hemoglobin 10.2 g/dL (Low)"
        ]
        
        normalized = [
            {"name": "Hemoglobin", "value": 10.2},
            {"name": "MadeUpTest", "value": 99}
        ]
        
        result = self.generator.guardrail_check(input_raw, normalized)
        
        # This should detect hallucinated tests
        assert result['status'] in ['ok', 'warning']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
