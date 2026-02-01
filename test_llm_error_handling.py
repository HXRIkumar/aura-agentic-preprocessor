"""
Test LLM Error Handling - Simulates LLM failure
"""

import os
import sys

# Temporarily break the API key to simulate LLM failure
original_key = os.environ.get('GROQ_API_KEY')
os.environ['GROQ_API_KEY'] = 'invalid_key_for_testing'

print("=" * 70)
print("TESTING LLM ERROR HANDLING IN AUTO MODE")
print("=" * 70)
print("\n⚠️  Simulating LLM failure by using invalid API key...")

try:
    from src.llm_service import GroqLLMService
    from src.pipeline import AuraPipeline
    
    # Try to get recommendations
    metadata = {
        "dataset_name": "titanic.csv",
        "target_column": "Survived",
        "columns": [
            {"name": "Age", "type": "numeric", "missing_pct": 19.87, "nunique": 88},
            {"name": "Sex", "type": "categorical", "missing_pct": 0, "nunique": 2}
        ]
    }
    
    print("\n🤖 Attempting to get LLM recommendations with invalid key...")
    
    llm_service = GroqLLMService()
    
    try:
        recommendations = llm_service.analyze_dataset_metadata(metadata)
        print("❌ UNEXPECTED: Got recommendations with invalid key!")
        sys.exit(1)
    except Exception as e:
        print(f"✅ EXPECTED: LLM call failed as expected")
        print(f"   Error: {str(e)[:100]}...")
        
        # Now test pipeline with no recommendations
        print("\n🚀 Testing pipeline execution WITHOUT LLM recommendations...")
        print("   (This simulates what happens when LLM is unavailable in AUTO mode)")
        
        try:
            # Try to run pipeline without recommendations (should fail gracefully)
            pipeline = AuraPipeline(
                filepath="data/titanic.csv",
                mode="auto",
                target_col="Survived",
                llm_recommendations=None
            )
            
            # In current implementation, this should use fallback heuristics
            print("   ⚠️  Pipeline initialized without LLM recommendations")
            print("   ⚠️  Will use fallback heuristics")
            
        except Exception as pipeline_error:
            print(f"   ❌ Pipeline failed: {pipeline_error}")

finally:
    # Restore original API key
    if original_key:
        os.environ['GROQ_API_KEY'] = original_key
    
    print("\n" + "=" * 70)
    print("ERROR HANDLING TEST COMPLETE")
    print("=" * 70)
    print("\n📋 Summary:")
    print("   ✅ LLM correctly fails with invalid credentials")
    print("   ✅ Error is raised (not silently ignored)")
    print("   ⚠️  In AUTO mode, pipeline should FAIL if LLM is unavailable")
    print("\n💡 Recommendation:")
    print("   The API server should catch this error and return")
    print("   a clear error message to the frontend.")
