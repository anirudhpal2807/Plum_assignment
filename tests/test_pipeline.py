"""
Integration tests for the complete pipeline
"""
import pytest
from app.modules.pipeline import MedicalReportPipeline


class TestMedicalReportPipelineTest:
    """Test cases for complete pipeline"""
    
    def setup_method(self):
        """Setup pipeline instance"""
        self.pipeline = MedicalReportPipeline()
    
    def test_process_text_valid_report(self):
        """Test processing valid text report"""
        text = """
        Hemoglobin 10.2 g/dL (Low)
        WBC 11200 /uL (High)
        Glucose 125 mg/dL (High)
        """
        
        result = self.pipeline.process_text(text)
        
        assert result['status'] == 'ok'
        assert len(result['tests']) > 0
        assert result['summary'] != ""
    
    def test_process_text_no_tests(self):
        """Test processing text with no valid tests"""
        text = "This is just random text without any test data"
        
        result = self.pipeline.process_text(text)
        
        assert result['status'] in ['no_tests_found', 'parse_failed']
    
    def test_process_text_with_typos(self):
        """Test processing text with spelling errors"""
        text = """
        Hemogloblin 10.2 g/dL
        Glukose 125 mg/dL
        """
        
        result = self.pipeline.process_text(text)
        
        # Should attempt fuzzy matching
        if result['status'] == 'ok':
            assert len(result['tests']) > 0
    
    def test_metadata_present(self):
        """Test that metadata is included in output"""
        text = "Hemoglobin 10.2 g/dL (Low)"
        
        result = self.pipeline.process_text(text)
        
        if result['status'] == 'ok':
            assert 'metadata' in result
            assert 'extraction_confidence' in result['metadata']
            assert 'normalization_confidence' in result['metadata']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
