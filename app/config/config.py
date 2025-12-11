import json
import os

CONFIG_PATH = os.path.dirname(__file__)

class ConfigLoader:
    """Load configuration and reference data"""
    
    _reference_ranges = None
    _explanation_templates = None
    
    @classmethod
    def get_reference_ranges(cls):
        """Load reference ranges for blood tests"""
        if cls._reference_ranges is None:
            with open(os.path.join(CONFIG_PATH, 'reference_ranges.json'), 'r') as f:
                cls._reference_ranges = json.load(f)
        return cls._reference_ranges
    
    @classmethod
    def get_explanation_templates(cls):
        """Load explanation templates"""
        if cls._explanation_templates is None:
            with open(os.path.join(CONFIG_PATH, 'explanation_templates.json'), 'r') as f:
                cls._explanation_templates = json.load(f)
        return cls._explanation_templates
    
    @classmethod
    def get_test_by_name(cls, test_name: str) -> dict:
        """Get test configuration by name"""
        ranges = cls.get_reference_ranges()
        return ranges['blood_tests'].get(test_name)
    
    @classmethod
    def get_all_test_names(cls) -> list:
        """Get all canonical test names"""
        ranges = cls.get_reference_ranges()
        return list(ranges['blood_tests'].keys())
    
    @classmethod
    def get_all_aliases(cls) -> dict:
        """Build a mapping of all aliases to canonical names"""
        ranges = cls.get_reference_ranges()
        alias_map = {}
        for test_name, test_data in ranges['blood_tests'].items():
            for alias in test_data.get('aliases', []):
                alias_map[alias.lower()] = test_name
        return alias_map
