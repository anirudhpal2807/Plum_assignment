"""
Patient-Friendly Summary Generator Module
Generates comprehensive, AI-style medical report summaries
"""
from typing import Dict, List, Optional
from datetime import datetime
import json

from app.config.logger import setup_logger
from app.config.config import ConfigLoader

logger = setup_logger(__name__)


class SummaryGenerator:
    """Generate patient-friendly summaries of test results"""
    
    def __init__(self):
        """Initialize summary generator"""
        self.config_loader = ConfigLoader()
        self.explanations = self.config_loader.get_explanation_templates()
        self.reference_ranges = self.config_loader.get_reference_ranges()
    
    def generate_summary(self, normalized_tests: List[Dict], patient_info: Dict = None) -> Dict:
        """
        Generate comprehensive patient-friendly summary
        Args:
            normalized_tests: List of normalized test dictionaries
            patient_info: Optional patient information extracted from report
        Returns:
            Dictionary with rich summary data
        """
        try:
            if not normalized_tests:
                logger.warning("No normalized tests provided for summary generation")
                return {
                    "status": "empty",
                    "summary": "No test results were found to summarize.",
                    "explanations": [],
                    "tests_summary": [],
                    "report": None
                }
            
            # Group tests by status and category
            abnormal_tests = [t for t in normalized_tests if t.get('status') != 'normal']
            normal_tests = [t for t in normalized_tests if t.get('status') == 'normal']
            
            # Group by category
            categories = self._group_by_category(normalized_tests)
            
            # Generate rich report
            report = self._generate_rich_report(
                normalized_tests, 
                abnormal_tests, 
                normal_tests,
                categories,
                patient_info
            )
            
            # Generate individual explanations
            explanations = self._generate_explanations(normalized_tests)
            
            # Create test summary for quick reference
            tests_summary = self._create_tests_summary(normalized_tests)
            
            # Generate summary text
            summary_text = self._generate_summary_text(abnormal_tests, normal_tests)
            
            logger.info(f"Generated rich summary for {len(normalized_tests)} tests")
            
            return {
                "status": "ok",
                "summary": summary_text,
                "explanations": explanations,
                "tests_summary": tests_summary,
                "abnormal_count": len(abnormal_tests),
                "normal_count": len(normal_tests),
                "report": report
            }
            
        except Exception as e:
            import traceback
            logger.error(f"Error generating summary: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "error": str(e),
                "summary": "",
                "explanations": [],
                "tests_summary": [],
                "report": None
            }
    
    def _group_by_category(self, tests: List[Dict]) -> Dict[str, List[Dict]]:
        """Group tests by their medical category"""
        categories = {}
        for test in tests:
            category = test.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(test)
        return categories
    
    def _generate_rich_report(self, all_tests: List[Dict], abnormal: List[Dict], 
                              normal: List[Dict], categories: Dict, 
                              patient_info: Dict = None) -> Dict:
        """
        Generate comprehensive AI-style report
        """
        # Determine primary test category
        primary_category = max(categories.keys(), key=lambda k: len(categories[k])) if categories else "General"
        
        # Get category display name
        category_names = {
            "hematology": "Complete Blood Count (CBC)",
            "lipid": "Lipid Profile",
            "diabetes": "Diabetes Panel",
            "liver": "Liver Function Test (LFT)",
            "kidney": "Kidney Function Test (KFT)",
            "thyroid": "Thyroid Panel",
            "cardiac": "Cardiac Markers",
            "vitamins": "Vitamins & Minerals",
            "electrolytes": "Electrolyte Panel",
            "urine": "Urine Analysis",
            "hormones": "Hormone Panel",
            "inflammatory": "Inflammatory Markers"
        }
        
        report_title = category_names.get(primary_category.lower(), f"{primary_category.title()} Test Report")
        
        # Build patient info section
        patient_section = {
            "name": patient_info.get('name', 'Patient') if patient_info else 'Patient',
            "age": patient_info.get('age', 'N/A') if patient_info else 'N/A',
            "sex": patient_info.get('sex', 'N/A') if patient_info else 'N/A',
            "date": datetime.now().strftime("%d %b %Y"),
            "referred_by": patient_info.get('referred_by', 'N/A') if patient_info else 'N/A'
        }
        
        # Build test overview section
        test_overviews = []
        for test in all_tests:
            test_name = test.get('name', '')
            test_config = self.reference_ranges.get('blood_tests', {}).get(test_name, {})
            overview = {
                "name": test_name,
                "description": test_config.get('explanation', f"This test measures {test_name} levels in your blood."),
                "importance": self._get_test_importance(test_name)
            }
            test_overviews.append(overview)
        
        # Build interpretations
        interpretations = []
        for test in all_tests:
            status = test.get('status', 'normal')
            value = test.get('value', 0)
            ref_range = test.get('ref_range', {})
            
            interpretation = self._generate_interpretation(
                test.get('name', ''),
                value,
                status,
                ref_range,
                patient_section.get('name', 'Patient')
            )
            interpretations.append({
                "test_name": test.get('name', ''),
                "status": status,
                "interpretation": interpretation
            })
        
        # Build key concepts
        key_concepts = self._generate_key_concepts(all_tests)
        
        # Build possible causes for abnormal tests
        abnormal_causes = []
        for test in abnormal:
            causes = self._get_abnormal_causes(test.get('name', ''), test.get('status', ''))
            if causes:
                abnormal_causes.append({
                    "test_name": test.get('name', ''),
                    "status": test.get('status', ''),
                    "causes": causes
                })
        
        # Build recommendations
        recommendations = self._generate_recommendations(abnormal, normal)
        
        # Overall summary
        if not abnormal:
            overall_status = "All Clear"
            overall_message = f"All {len(all_tests)} test(s) are within normal ranges. Your results indicate healthy levels."
        elif len(abnormal) == 1:
            overall_status = "Attention Needed"
            overall_message = f"{abnormal[0]['name']} requires attention. {len(normal)} other test(s) are normal."
        else:
            overall_status = "Review Recommended"
            overall_message = f"{len(abnormal)} test(s) show abnormal values and should be reviewed with your doctor."
        
        return {
            "title": report_title,
            "generated_at": datetime.now().isoformat(),
            "patient_info": patient_section,
            "overall_status": overall_status,
            "overall_message": overall_message,
            "test_overviews": test_overviews,
            "results_by_category": {cat: [
                {
                    "name": t.get('name'),
                    "value": t.get('value'),
                    "unit": t.get('unit'),
                    "ref_low": t.get('ref_range', {}).get('low'),
                    "ref_high": t.get('ref_range', {}).get('high'),
                    "status": t.get('status')
                } for t in tests
            ] for cat, tests in categories.items()},
            "interpretations": interpretations,
            "key_concepts": key_concepts,
            "abnormal_causes": abnormal_causes,
            "recommendations": recommendations,
            "summary_stats": {
                "total_tests": len(all_tests),
                "normal_count": len(normal),
                "abnormal_count": len(abnormal),
                "categories_tested": list(categories.keys())
            }
        }
    
    def _get_test_importance(self, test_name: str) -> str:
        """Get importance/purpose of a test"""
        importance_map = {
            "Hemoglobin": "Essential for measuring oxygen-carrying capacity of blood",
            "Red Blood Cell Count": "Indicates the number of RBCs which carry oxygen throughout the body",
            "White Blood Cell Count": "Measures immune system cells that fight infection",
            "Platelet Count": "Important for blood clotting ability",
            "Fasting Blood Sugar": "Key indicator for diabetes screening and monitoring",
            "HbA1c": "Shows average blood sugar control over 2-3 months",
            "Total Cholesterol": "Assesses cardiovascular disease risk",
            "LDL Cholesterol": "Bad cholesterol - high levels increase heart disease risk",
            "HDL Cholesterol": "Good cholesterol - helps remove bad cholesterol",
            "Triglycerides": "Type of fat in blood - high levels increase heart disease risk",
            "Creatinine": "Measures kidney function and filtration ability",
            "Blood Urea Nitrogen": "Indicates kidney health and protein metabolism",
            "TSH": "Thyroid stimulating hormone - indicates thyroid function",
            "SGPT": "Liver enzyme - indicates liver health",
            "SGOT": "Liver enzyme - indicates liver and heart health",
            "Vitamin D": "Essential for bone health and immune function",
            "Vitamin B12": "Important for nerve function and red blood cell formation"
        }
        return importance_map.get(test_name, f"Measures {test_name} levels in your body")
    
    def _generate_interpretation(self, test_name: str, value: float, status: str, 
                                  ref_range: Dict, patient_name: str) -> str:
        """Generate patient-specific interpretation"""
        if status == 'normal':
            return f"{patient_name}'s {test_name} ({value}) is within the normal reference range ({ref_range.get('low', 'N/A')} - {ref_range.get('high', 'N/A')}), indicating healthy levels."
        elif status == 'low':
            return f"{patient_name}'s {test_name} ({value}) is below the normal range ({ref_range.get('low', 'N/A')} - {ref_range.get('high', 'N/A')}). This may need further evaluation."
        elif status == 'high':
            return f"{patient_name}'s {test_name} ({value}) is above the normal range ({ref_range.get('low', 'N/A')} - {ref_range.get('high', 'N/A')}). This should be discussed with your doctor."
        return f"{test_name} result: {value}"
    
    def _generate_key_concepts(self, tests: List[Dict]) -> List[Dict]:
        """Generate key medical concepts explanation"""
        concepts = []
        seen = set()
        
        concept_definitions = {
            "Red Blood Cell Count": {
                "term": "Red Blood Cells (RBCs)",
                "definition": "Cells that carry oxygen from the lungs to the rest of the body and return carbon dioxide for exhalation."
            },
            "White Blood Cell Count": {
                "term": "White Blood Cells (WBCs)",
                "definition": "Immune system cells that help fight infections, bacteria, and viruses."
            },
            "Hemoglobin": {
                "term": "Hemoglobin (Hb)",
                "definition": "The protein in red blood cells that carries oxygen. Low levels may indicate anemia."
            },
            "Platelet Count": {
                "term": "Platelets",
                "definition": "Cell fragments that help blood clot and stop bleeding when you're injured."
            },
            "PDW": {
                "term": "Platelet Distribution Width",
                "definition": "Measures variation in platelet size. Useful for distinguishing different platelet disorders."
            },
            "MPV": {
                "term": "Mean Platelet Volume",
                "definition": "Average size of platelets. Larger platelets are often younger and more active."
            },
            "Fasting Blood Sugar": {
                "term": "Blood Glucose",
                "definition": "Sugar in your blood that provides energy. High levels may indicate diabetes."
            },
            "HbA1c": {
                "term": "Glycated Hemoglobin",
                "definition": "Shows your average blood sugar over the past 2-3 months. Used for diabetes monitoring."
            },
            "Total Cholesterol": {
                "term": "Cholesterol",
                "definition": "A fatty substance in blood. High levels can lead to plaque buildup in arteries."
            },
            "Creatinine": {
                "term": "Creatinine",
                "definition": "A waste product from muscle metabolism. High levels may indicate kidney problems."
            },
            "TSH": {
                "term": "Thyroid Stimulating Hormone",
                "definition": "Hormone that controls thyroid gland activity. Abnormal levels affect metabolism."
            }
        }
        
        for test in tests:
            test_name = test.get('name', '')
            if test_name in concept_definitions and test_name not in seen:
                concepts.append(concept_definitions[test_name])
                seen.add(test_name)
        
        return concepts
    
    def _get_abnormal_causes(self, test_name: str, status: str) -> Dict:
        """Get possible causes for abnormal test results"""
        causes_data = {
            "Red Blood Cell Count": {
                "low": {
                    "title": "Low RBC Count (Anemia & Related Causes)",
                    "causes": [
                        "Iron deficiency, chronic diseases",
                        "Blood loss (trauma, ulcers, heavy menstruation)",
                        "Bone marrow disorders (e.g., leukemia)",
                        "Nutritional deficiencies (vitamin B12, folate)",
                        "Kidney disease (reduced hormone production)",
                        "Certain medications (chemotherapy)"
                    ]
                },
                "high": {
                    "title": "High RBC Count (Polycythemia & Related Causes)",
                    "causes": [
                        "Increased RBC production (polycythemia)",
                        "Dehydration (concentrated blood)",
                        "Chronic lung diseases (COPD)",
                        "Kidney disease (increased hormone production)",
                        "Living at high altitude",
                        "Certain medications (steroids, diuretics)"
                    ]
                }
            },
            "Hemoglobin": {
                "low": {
                    "title": "Low Hemoglobin (Anemia Causes)",
                    "causes": [
                        "Iron deficiency anemia",
                        "Vitamin B12 or folate deficiency",
                        "Chronic kidney disease",
                        "Blood loss (menstruation, injury, GI bleeding)",
                        "Bone marrow problems",
                        "Chronic diseases (cancer, autoimmune disorders)"
                    ]
                },
                "high": {
                    "title": "High Hemoglobin Causes",
                    "causes": [
                        "Dehydration",
                        "Polycythemia vera",
                        "Lung diseases",
                        "Heart disease",
                        "Smoking",
                        "Living at high altitude"
                    ]
                }
            },
            "Fasting Blood Sugar": {
                "low": {
                    "title": "Low Blood Sugar (Hypoglycemia) Causes",
                    "causes": [
                        "Excess insulin or diabetes medication",
                        "Skipping meals or fasting too long",
                        "Excessive alcohol consumption",
                        "Hormonal deficiencies",
                        "Certain medical conditions"
                    ]
                },
                "high": {
                    "title": "High Blood Sugar (Hyperglycemia) Causes",
                    "causes": [
                        "Diabetes mellitus (Type 1 or Type 2)",
                        "Prediabetes",
                        "Stress or illness",
                        "Certain medications (steroids)",
                        "Pancreatitis",
                        "Hormonal disorders (Cushing's syndrome)"
                    ]
                }
            },
            "Total Cholesterol": {
                "high": {
                    "title": "High Cholesterol Causes",
                    "causes": [
                        "Poor diet (high in saturated fats)",
                        "Lack of physical activity",
                        "Obesity",
                        "Genetic factors (familial hypercholesterolemia)",
                        "Diabetes",
                        "Hypothyroidism",
                        "Smoking"
                    ]
                }
            },
            "Triglycerides": {
                "high": {
                    "title": "High Triglycerides Causes",
                    "causes": [
                        "Obesity or overweight",
                        "High sugar/carbohydrate diet",
                        "Excessive alcohol consumption",
                        "Uncontrolled diabetes",
                        "Hypothyroidism",
                        "Certain medications",
                        "Genetic factors"
                    ]
                }
            },
            "Creatinine": {
                "high": {
                    "title": "High Creatinine Causes",
                    "causes": [
                        "Kidney disease or kidney damage",
                        "Dehydration",
                        "High protein diet",
                        "Intense exercise",
                        "Certain medications",
                        "Muscle disorders"
                    ]
                }
            },
            "TSH": {
                "low": {
                    "title": "Low TSH (Hyperthyroidism) Causes",
                    "causes": [
                        "Overactive thyroid (Graves' disease)",
                        "Excess thyroid medication",
                        "Thyroid nodules",
                        "Thyroiditis"
                    ]
                },
                "high": {
                    "title": "High TSH (Hypothyroidism) Causes",
                    "causes": [
                        "Underactive thyroid (Hashimoto's thyroiditis)",
                        "Iodine deficiency",
                        "Pituitary gland problems",
                        "Thyroid surgery or radiation",
                        "Certain medications"
                    ]
                }
            },
            "White Blood Cell Count": {
                "low": {
                    "title": "Low WBC Count (Leukopenia) Causes",
                    "causes": [
                        "Bone marrow disorders",
                        "Autoimmune diseases",
                        "Viral infections",
                        "Certain medications (chemotherapy)",
                        "Severe infections",
                        "Nutritional deficiencies"
                    ]
                },
                "high": {
                    "title": "High WBC Count (Leukocytosis) Causes",
                    "causes": [
                        "Bacterial infections",
                        "Inflammation",
                        "Allergic reactions",
                        "Leukemia",
                        "Stress response",
                        "Certain medications (steroids)"
                    ]
                }
            },
            "Platelet Count": {
                "low": {
                    "title": "Low Platelet Count (Thrombocytopenia) Causes",
                    "causes": [
                        "Bone marrow disorders",
                        "Viral infections",
                        "Autoimmune conditions",
                        "Certain medications",
                        "Liver disease",
                        "Pregnancy complications"
                    ]
                },
                "high": {
                    "title": "High Platelet Count (Thrombocytosis) Causes",
                    "causes": [
                        "Infection or inflammation",
                        "Iron deficiency",
                        "Cancer",
                        "Bone marrow disorders",
                        "Post-surgery recovery",
                        "Chronic diseases"
                    ]
                }
            },
            "PDW": {
                "low": {
                    "title": "Low PDW Causes",
                    "causes": [
                        "Iron deficiency",
                        "Vitamin B12 deficiency",
                        "Bone marrow disorders",
                        "Certain chronic conditions"
                    ]
                },
                "high": {
                    "title": "High PDW Causes",
                    "causes": [
                        "Platelet activation disorders",
                        "Liver disease",
                        "Bone marrow disorders",
                        "Immune thrombocytopenia",
                        "Inflammatory conditions",
                        "Recent blood loss"
                    ]
                }
            },
            "MPV": {
                "low": {
                    "title": "Low MPV Causes",
                    "causes": [
                        "Bone marrow suppression",
                        "Inflammatory conditions",
                        "Certain medications",
                        "Aplastic anemia"
                    ]
                },
                "high": {
                    "title": "High MPV Causes",
                    "causes": [
                        "Increased platelet destruction",
                        "Immune thrombocytopenic purpura (ITP)",
                        "Vitamin B12 deficiency",
                        "Hyperthyroidism",
                        "Diabetes",
                        "Cardiovascular disease risk"
                    ]
                }
            }
        }
        
        if test_name in causes_data and status in causes_data[test_name]:
            return causes_data[test_name][status]
        return None
    
    def _generate_recommendations(self, abnormal: List[Dict], normal: List[Dict]) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        if not abnormal:
            recommendations.append("Continue maintaining your healthy lifestyle.")
            recommendations.append("Schedule regular health check-ups as recommended by your doctor.")
        else:
            recommendations.append("Consult with your healthcare provider to discuss these results.")
            recommendations.append("Do not self-diagnose or self-medicate based on these results.")
            
            for test in abnormal:
                name = test.get('name', '')
                status = test.get('status', '')
                
                if 'Cholesterol' in name or 'Triglycerides' in name:
                    recommendations.append("Consider dietary changes: reduce saturated fats, increase fiber intake.")
                    recommendations.append("Regular physical activity can help improve lipid levels.")
                elif 'Sugar' in name or 'Glucose' in name or 'HbA1c' in name:
                    recommendations.append("Monitor your carbohydrate intake and maintain healthy eating habits.")
                    recommendations.append("Regular exercise helps control blood sugar levels.")
                elif 'Hemoglobin' in name and status == 'low':
                    recommendations.append("Include iron-rich foods like spinach, lentils, and lean meats in your diet.")
                elif 'Creatinine' in name:
                    recommendations.append("Stay well hydrated and limit high-protein foods temporarily.")
                elif 'TSH' in name:
                    recommendations.append("Follow up with an endocrinologist for thyroid evaluation.")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:5]  # Max 5 recommendations
    
    def _generate_summary_text(self, abnormal_tests: List[Dict], normal_tests: List[Dict]) -> str:
        """Generate overall summary text"""
        if not abnormal_tests and not normal_tests:
            return "No test results to summarize."
        
        if not abnormal_tests:
            return f"All {len(normal_tests)} test result(s) are within normal ranges. Your health indicators look good!"
        
        # Build summary from abnormal tests
        abnormal_names = [f"{t['status'].capitalize()} {t['name']}" for t in abnormal_tests]
        
        if len(abnormal_names) == 1:
            summary = f"{abnormal_names[0]}."
        elif len(abnormal_names) == 2:
            summary = f"{abnormal_names[0]} and {abnormal_names[1]}."
        else:
            summary = f"{', '.join(abnormal_names[:-1])}, and {abnormal_names[-1]}."
        
        if normal_tests:
            summary += f" {len(normal_tests)} other test(s) are within normal range."
        
        return summary
    
    def _generate_explanations(self, normalized_tests: List[Dict]) -> List[Dict]:
        """Generate individual explanations for each test"""
        explanations = []
        
        for test in normalized_tests:
            explanation = self._get_explanation_for_test(test)
            
            explanations.append({
                "test_name": test.get('name', ''),
                "status": test.get('status', 'normal'),
                "value": test.get('value'),
                "unit": test.get('unit', ''),
                "reference_range": test.get('ref_range', {}),
                "explanation": explanation
            })
        
        return explanations
    
    def _get_explanation_for_test(self, test: Dict) -> str:
        """Get patient-friendly explanation for a test result"""
        test_name = test.get('name', '')
        status = test.get('status', 'normal')
        
        # Get explanation templates
        templates = self.explanations.get('explanations', {})
        
        # Try to get specific explanation
        status_templates = templates.get(status, {})
        explanation = status_templates.get(test_name)
        
        if explanation:
            return explanation
        
        # Fallback to generic explanation
        if status == 'normal':
            return f"Your {test_name} is within the normal range, indicating healthy levels."
        elif status == 'low':
            return f"Your {test_name} is below the normal range. Please consult your doctor for advice."
        elif status == 'high':
            return f"Your {test_name} is above the normal range. Please discuss with your healthcare provider."
        
        return f"{test_name} result has been recorded."
    
    def _create_tests_summary(self, normalized_tests: List[Dict]) -> List[Dict]:
        """Create quick-reference test summary"""
        summary = []
        
        for test in normalized_tests:
            summary.append({
                "name": test.get('name', ''),
                "value": test.get('value'),
                "unit": test.get('unit', ''),
                "status": test.get('status', 'normal'),
                "reference_low": test.get('ref_range', {}).get('low'),
                "reference_high": test.get('ref_range', {}).get('high'),
                "category": test.get('category', 'other')
            })
        
        return summary
    
    def guardrail_check(self, input_tests_raw: List[str], normalized_tests: List[Dict]) -> Dict:
        """
        Check for hallucinated tests (tests in output not present in input)
        """
        try:
            # Combine all raw input into one string for easier matching
            combined_input = ' '.join(input_tests_raw).lower()
            
            # Get all aliases from config for better matching
            all_aliases = self.config_loader.get_all_aliases()
            
            # Check if all normalized tests are traceable to input
            hallucinated = []
            for test in normalized_tests:
                test_name = test.get('name', '')
                test_name_lower = test_name.lower()
                
                # Check if canonical name or any of its aliases are in input
                found = False
                
                # Check canonical name
                if test_name_lower in combined_input:
                    found = True
                
                # Check aliases
                if not found:
                    for alias, canonical in all_aliases.items():
                        if canonical == test_name and alias in combined_input:
                            found = True
                            break
                
                # Additional fuzzy check - look for key words
                if not found:
                    key_words = test_name_lower.split()
                    if len(key_words) >= 2:
                        matches = sum(1 for word in key_words if word in combined_input and len(word) > 2)
                        if matches >= 2:
                            found = True
                    elif len(key_words) == 1 and key_words[0] in combined_input:
                        found = True
                
                if not found:
                    hallucinated.append(test_name)
            
            if hallucinated:
                logger.warning(f"Potential hallucinated tests detected: {hallucinated}")
                return {
                    "status": "warning",
                    "hallucinated_tests": hallucinated,
                    "message": f"Found {len(hallucinated)} test(s) not clearly present in input"
                }
            
            return {
                "status": "ok",
                "hallucinated_tests": [],
                "message": "No hallucinated tests detected"
            }
            
        except Exception as e:
            logger.error(f"Error in guardrail check: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
