"""
Test to verify LLM is only called once per pipeline run.
This test checks that the duplicate logging issue has been fixed.
"""

import sys
import os
from io import StringIO
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.llm_service import get_llm_service

def test_single_llm_call():
    """Test that LLM service only logs once per call"""
    print("\n" + "=" * 70)
    print("TEST: Verify LLM Service Logs Only Once")
    print("=" * 70)
    
    # Set up logging capture
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.INFO)
    
    logger = logging.getLogger('src.llm_service')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Create test metadata
    metadata = {
        "dataset_name": "test.csv",
        "target_column": "Survived",
        "columns": [
            {"name": "Age", "type": "numeric", "missing_pct": 20.0, "nunique": 50},
            {"name": "Sex", "type": "categorical", "missing_pct": 0.0, "nunique": 2},
            {"name": "Survived", "type": "numeric", "missing_pct": 0.0, "nunique": 2}
        ]
    }
    
    try:
        # Call LLM service
        print("\n🤖 Calling LLM service once...")
        llm_service = get_llm_service()
        recommendations = llm_service.analyze_dataset_metadata(metadata)
        
        # Get the log output
        log_output = log_capture.getvalue()
        
        # Count how many times "LLM RECOMMENDATIONS RECEIVED" appears
        count = log_output.count("LLM RECOMMENDATIONS RECEIVED")
        
        print(f"\n📊 Results:")
        print(f"   'LLM RECOMMENDATIONS RECEIVED' appears {count} time(s)")
        
        if count == 1:
            print("   ✅ PASS: LLM service logged exactly once")
        else:
            print(f"   ❌ FAIL: Expected 1 occurrence, found {count}")
            print("\n📝 Log output:")
            print(log_output)
            return False
        
        # Verify recommendations were received
        if "recommendations" in recommendations:
            print("   ✅ PASS: Recommendations received successfully")
        else:
            print("   ❌ FAIL: No recommendations in response")
            return False
        
        print("\n✅ All tests passed! LLM is called only once.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    
    finally:
        logger.removeHandler(handler)


if __name__ == "__main__":
    print("\n🧪 Testing LLM Duplicate Call Fix")
    print("=" * 70)
    
    success = test_single_llm_call()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ TEST SUITE PASSED")
    else:
        print("❌ TEST SUITE FAILED")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
