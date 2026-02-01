"""
Test script for Groq LLM integration
"""

from src.llm_service import get_llm_service

# Test metadata analysis
print("=" * 60)
print("Testing Groq LLM Integration")
print("=" * 60)

# Sample dataset metadata
test_metadata = {
    "dataset_name": "titanic.csv",
    "target_column": "Survived",
    "columns": [
        {
            "name": "PassengerId",
            "type": "numeric",
            "missing_pct": 0,
            "nunique": 891
        },
        {
            "name": "Survived",
            "type": "numeric",
            "missing_pct": 0,
            "nunique": 2
        },
        {
            "name": "Pclass",
            "type": "numeric",
            "missing_pct": 0,
            "nunique": 3
        },
        {
            "name": "Name",
            "type": "categorical",
            "missing_pct": 0,
            "nunique": 891
        },
        {
            "name": "Sex",
            "type": "categorical",
            "missing_pct": 0,
            "nunique": 2
        },
        {
            "name": "Age",
            "type": "numeric",
            "missing_pct": 19.87,
            "nunique": 88
        },
        {
            "name": "SibSp",
            "type": "numeric",
            "missing_pct": 0,
            "nunique": 7
        },
        {
            "name": "Parch",
            "type": "numeric",
            "missing_pct": 0,
            "nunique": 7
        },
        {
            "name": "Fare",
            "type": "numeric",
            "missing_pct": 0,
            "nunique": 248
        },
        {
            "name": "Cabin",
            "type": "categorical",
            "missing_pct": 77.10,
            "nunique": 147
        },
        {
            "name": "Embarked",
            "type": "categorical",
            "missing_pct": 0.22,
            "nunique": 3
        }
    ]
}

try:
    llm_service = get_llm_service()
    
    print("\n1. Testing metadata analysis...")
    print("-" * 60)
    recommendations = llm_service.analyze_dataset_metadata(test_metadata)
    
    print("\n✅ Recommendations received:")
    print(f"\nMissing Values Strategy: {recommendations['recommendations']['missing']['strategy']}")
    print(f"Explanation: {recommendations['recommendations']['missing']['explain']}")
    
    print(f"\nEncoding Strategy: {recommendations['recommendations']['encoding']['strategy']}")
    print(f"Explanation: {recommendations['recommendations']['encoding']['explain']}")
    
    print(f"\nScaling Strategy: {recommendations['recommendations']['scaling']['strategy']}")
    print(f"Explanation: {recommendations['recommendations']['scaling']['explain']}")
    
    print(f"\nModel Recommendation: {recommendations['recommendations']['model']['algorithm']}")
    print(f"Explanation: {recommendations['recommendations']['model']['explain']}")
    
    print("\n" + "=" * 60)
    print("\n2. Testing chat functionality...")
    print("-" * 60)
    
    dataset_context = {
        "dataset_name": "titanic.csv",
        "columns": test_metadata["columns"],
        "target_column": "Survived"
    }
    
    response = llm_service.chat(
        message="What preprocessing steps do you recommend for this dataset?",
        dataset_context=dataset_context
    )
    
    print("\n✅ Chat response:")
    print(response)
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! LLM integration is working.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
