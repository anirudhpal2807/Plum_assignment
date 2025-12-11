#!/usr/bin/env python3
"""
Quick test script to verify the API is working
Run this after starting the server: python tests/quick_test.py
"""

import requests
import json
import sys
from pathlib import Path

API_BASE = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def test_health():
    """Test API health endpoint"""
    print_header("Testing API Health")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print_success("API is healthy and responding!")
            return True
        else:
            print_error(f"API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {API_BASE}")
        print_info("Make sure the server is running: python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_text_simplification():
    """Test text report simplification"""
    print_header("Testing Text Report Simplification")
    
    report = """Hemoglobin 10.2 g/dL (Low)
WBC 7.5 K/µL
RBC 4.2 M/µL
Platelets 250 K/µL
Glucose 120 mg/dL (High)
Total Cholesterol 220 mg/dL (High)"""
    
    print_info(f"Input Report:\n{report}\n")
    
    try:
        response = requests.post(
            f"{API_BASE}/simplify-report",
            data={"text": report},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print_success("Report simplified successfully!")
            print(f"\n{Colors.BOLD}Results:{Colors.END}")
            print(f"Status: {data.get('status')}")
            print(f"Summary: {data.get('summary')}")
            
            tests = data.get('tests', [])
            print(f"\nFound {len(tests)} tests:")
            for test in tests:
                status_color = Colors.GREEN if test.get('status') == 'normal' else Colors.YELLOW
                print(f"  • {test.get('name')}: {test.get('value')} {test.get('unit')} [{status_color}{test.get('status')}{Colors.END}]")
            
            return True
        else:
            print_error(f"API returned status {response.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_supported_tests():
    """Test getting supported tests"""
    print_header("Testing Supported Tests Endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/supported-tests", timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            tests = data.get('tests', [])
            print_success(f"Retrieved {len(tests)} supported blood tests!")
            
            print(f"\n{Colors.BOLD}Sample Tests:{Colors.END}")
            for test in tests[:5]:
                print(f"  • {test.get('name')} ({test.get('unit')})")
                print(f"    Range: {test.get('reference_range', {}).get('min')} - {test.get('reference_range', {}).get('max')}")
            
            if len(tests) > 5:
                print(f"  ... and {len(tests) - 5} more")
            
            return True
        else:
            print_error(f"API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_batch_processing():
    """Test batch report processing"""
    print_header("Testing Batch Processing")
    
    reports = [
        "Hemoglobin 10.2 g/dL (Low)",
        "WBC 7.5 K/µL Glucose 120 mg/dL (High)",
        "Platelets 250 K/µL RBC 4.2 M/µL"
    ]
    
    print_info(f"Processing {len(reports)} reports in batch\n")
    
    try:
        response = requests.post(
            f"{API_BASE}/batch-simplify",
            json={"reports": reports},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print_success(f"Batch processed successfully!")
            
            results = data.get('results', [])
            print(f"\n{Colors.BOLD}Results:{Colors.END}")
            for i, result in enumerate(results, 1):
                status = result.get('status', 'unknown')
                test_count = len(result.get('tests', []))
                status_symbol = Colors.GREEN + "✓" + Colors.END if status == 'ok' else Colors.RED + "✗" + Colors.END
                print(f"  {i}. Report {status_symbol} - {test_count} tests found")
            
            return True
        else:
            print_error(f"API returned status {response.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🏥 Medical Report Simplifier - Quick Test Suite{Colors.END}\n")
    print_info(f"Testing API at: {API_BASE}")
    
    results = {
        "Health Check": test_health(),
        "Text Simplification": test_text_simplification(),
        "Supported Tests": test_supported_tests(),
        "Batch Processing": test_batch_processing(),
    }
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"{Colors.BOLD}Results:{Colors.END}")
    for test_name, result in results.items():
        symbol = Colors.GREEN + "✅" + Colors.END if result else Colors.RED + "❌" + Colors.END
        print(f"  {symbol} {test_name}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print_success("All tests passed! 🎉")
        print_info("Your API is working correctly.")
        print_info("Open frontend.html in a browser to test the UI: file:///C:/MERN_project/PLUm/medical_report_api/frontend.html")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        print_info("Check if the server is running and accessible")
        return 1

if __name__ == "__main__":
    sys.exit(main())
