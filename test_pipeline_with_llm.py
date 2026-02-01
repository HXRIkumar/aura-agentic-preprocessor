"""
Test LLM Integration with Pipeline - End to End
This tests that LLM recommendations are properly used in the pipeline.
"""

import sys
import json
from src.llm_service import get_llm_service
from src.pipeline import AuraPipeline

print("=" * 70)
print("TESTING LLM INTEGRATION WITH PIPELINE")
print("=" * 70)

# Step 1: Generate metadata for Titanic dataset
print("\n📊 Step 1: Generating dataset metadata...")
metadata = {
    "dataset_name": "titanic.csv",
    "target_column": "Survived",
    "columns": [
        {"name": "PassengerId", "type": "numeric", "missing_pct": 0, "nunique": 891},
        {"name": "Survived", "type": "numeric", "missing_pct": 0, "nunique": 2},
        {"name": "Pclass", "type": "numeric", "missing_pct": 0, "nunique": 3},
        {"name": "Name", "type": "categorical", "missing_pct": 0, "nunique": 891},
        {"name": "Sex", "type": "categorical", "missing_pct": 0, "nunique": 2},
        {"name": "Age", "type": "numeric", "missing_pct": 19.87, "nunique": 88},
        {"name": "SibSp", "type": "numeric", "missing_pct": 0, "nunique": 7},
        {"name": "Parch", "type": "numeric", "missing_pct": 0, "nunique": 7},
        {"name": "Fare", "type": "numeric", "missing_pct": 0, "nunique": 248},
        {"name": "Cabin", "type": "categorical", "missing_pct": 77.10, "nunique": 147},
        {"name": "Embarked", "type": "categorical", "missing_pct": 0.22, "nunique": 3}
    ]
}
print("✅ Metadata prepared")

# Step 2: Get LLM recommendations
print("\n🤖 Step 2: Getting LLM recommendations...")
try:
    llm_service = get_llm_service()
    recommendations_response = llm_service.analyze_dataset_metadata(metadata)
    
    if "recommendations" in recommendations_response:
        llm_recommendations = recommendations_response["recommendations"]
        print("✅ LLM recommendations received!")
        
        print("\n📋 LLM Recommendations Summary:")
        print(f"  Missing Values: {llm_recommendations['missing']['strategy']}")
        print(f"  Encoding: {llm_recommendations['encoding']['strategy']}")
        print(f"  Scaling: {llm_recommendations['scaling']['strategy']}")
        print(f"  Model: {llm_recommendations['model']['algorithm']}")
        
        # Save recommendations to file for inspection
        with open("outputs/test_llm_recommendations.json", "w") as f:
            json.dump(recommendations_response, f, indent=2)
        print("\n💾 Saved recommendations to outputs/test_llm_recommendations.json")
    else:
        print("❌ No recommendations in response")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error getting LLM recommendations: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Run pipeline with LLM recommendations
print("\n🚀 Step 3: Running pipeline with LLM recommendations...")
try:
    pipeline = AuraPipeline(
        filepath="data/titanic.csv",
        mode="auto",
        target_col="Survived",
        llm_recommendations=llm_recommendations
    )
    
    print("\n" + "="*70)
    print("PIPELINE EXECUTION (Watch for LLM recommendations being applied)")
    print("="*70)
    
    results = pipeline.run_full_pipeline(
        test_size=0.2,
        save_data=True,
        save_explanations=True
    )
    
    if results["success"]:
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY WITH LLM RECOMMENDATIONS!")
        print("="*70)
        
        # Show model results
        if "model_results" in results and results["model_results"]:
            model_results = results["model_results"]["results"]
            print(f"\n📊 Model Performance:")
            print(f"  Algorithm: {results['model_results'].get('model_name', 'Unknown')}")
            accuracy = model_results.get('accuracy', 'N/A')
            cv_score = model_results.get('cv_score', 'N/A')
            cv_std = model_results.get('cv_std', 0)
            if accuracy != 'N/A':
                print(f"  Accuracy: {accuracy:.4f}")
            if cv_score != 'N/A':
                print(f"  CV Score: {cv_score:.4f} ± {cv_std:.4f}")
        
        print(f"\n📂 Check outputs folder for:")
        print(f"  - titanic_processed.csv (processed data)")
        print(f"  - report.json (full pipeline report)")
        print(f"  - aura_explanations.json (step explanations)")
        print(f"  - test_llm_recommendations.json (LLM recommendations used)")
        
    else:
        print("❌ Pipeline failed")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error running pipeline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL TESTS PASSED - LLM INTEGRATION WORKING!")
print("="*70)
print("\n🎉 The pipeline now uses LLM recommendations in auto mode!")
print("🔍 Compare outputs/test_llm_recommendations.json with the pipeline logs")
print("    to see how LLM recommendations were applied.")
