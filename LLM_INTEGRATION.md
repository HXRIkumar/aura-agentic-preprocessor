# LLM Integration - Groq API

## Overview
AURA Preprocessor now includes intelligent LLM-powered recommendations using Groq's API with the `llama-3.3-70b-versatile` model.

## Features Added

### 1. **Automated Dataset Analysis**
- Analyzes dataset metadata (columns, types, missing values, cardinality)
- Provides specific recommendations for:
  - Missing value handling strategies (per column)
  - Encoding methods (label vs one-hot, per column)
  - Scaling approaches (standard, minmax, robust, or none)
  - Model selection (random_forest, gradient_boosting, logistic_regression, svm)

### 2. **Interactive Chat Assistant**
- Context-aware chatbot that understands your dataset
- Answers questions about preprocessing strategies
- Provides explanations and guidance
- Maintains conversation history for better context

## Implementation Details

### New Files Created
- `src/llm_service.py` - Core LLM service with Groq integration
- `.env` - Configuration file with API key
- `test_llm.py` - Test script for LLM functionality

### Modified Files
- `api_server.py` - Integrated LLM service into chat and analysis endpoints
- `requirements.txt` - Added groq and python-dotenv dependencies

### API Endpoints

#### 1. Chat Endpoint
```
POST /api/v1/chat
```

**Request:**
```json
{
  "dataset_id": "uuid",
  "message": "What preprocessing steps do you recommend?",
  "conversation_history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response:**
```json
{
  "message": "Based on your dataset analysis...",
  "timestamp": "2025-11-04T..."
}
```

#### 2. Metadata Analysis Endpoint
```
POST /api/v1/llm/analyze-metadata
```

**Request:**
```json
{
  "dataset_id": "uuid",
  "metadata": {
    "dataset_name": "titanic.csv",
    "target_column": "Survived",
    "columns": [
      {
        "name": "Age",
        "type": "numeric",
        "missing_pct": 19.87,
        "nunique": 88
      }
    ]
  }
}
```

**Response:**
```json
{
  "recommendations": {
    "missing": {
      "strategy": "median",
      "columns": {"Age": "median", "Cabin": "drop"},
      "explain": "Age has significant missing values...",
      "risk": ["May not capture complex patterns"]
    },
    "encoding": {
      "strategy": "onehot",
      "columns": {"Sex": "onehot", "Embarked": "onehot"},
      "explain": "One-hot encoding for low-cardinality columns...",
      "risk": ["May increase dimensionality"]
    },
    "scaling": {
      "strategy": "standard",
      "explain": "StandardScaler for normally distributed features...",
      "risk": ["Sensitive to outliers"]
    },
    "model": {
      "algorithm": "random_forest",
      "explain": "Random Forest handles mixed data types well...",
      "risk": ["May require hyperparameter tuning"]
    }
  }
}
```

## Configuration

### Environment Variables
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_api_key_here
```

### Model Selection
Currently using `llama-3.3-70b-versatile` (Groq's latest powerful model).
Can be changed in `src/llm_service.py`:
```python
self.model = "llama-3.3-70b-versatile"
```

## Usage Examples

### 1. Test the Integration
```bash
python test_llm.py
```

### 2. Using in Frontend (Auto Mode)
When user selects "Auto Mode":
1. Frontend sends dataset metadata to `/api/v1/llm/analyze-metadata`
2. LLM analyzes and returns recommendations
3. Frontend displays recommendations with explanations
4. User can accept or modify recommendations

### 3. Using Chat Feature
Chat button available on any page:
1. User clicks floating chat button
2. Types question about dataset or preprocessing
3. LLM provides context-aware response
4. Conversation history maintained

## LLM Response Quality

### What the LLM Considers:
- Column data types (numeric vs categorical)
- Missing value percentages
- Cardinality (unique values) for categorical columns
- Dataset size and complexity
- Target column type (classification vs regression)
- Best practices in ML preprocessing

### Response Format:
- **Strategy**: The recommended approach
- **Columns**: Specific column-level recommendations (when applicable)
- **Explain**: Why this strategy was chosen
- **Risk**: Potential issues or considerations

## Benefits

1. **Smart Recommendations**: LLM analyzes actual dataset characteristics
2. **Educational**: Provides explanations for each recommendation
3. **Risk Awareness**: Highlights potential issues with each approach
4. **Interactive**: Users can ask questions and get guidance
5. **Context-Aware**: Chat remembers conversation history
6. **Column-Specific**: Recommendations tailored to individual columns

## Error Handling

The service includes fallback mechanisms:
- If LLM API fails, returns sensible default recommendations
- Graceful error messages in chat
- Doesn't break the pipeline if LLM is unavailable

## Future Enhancements

- [ ] Fine-tune prompts for better recommendations
- [ ] Add support for regression problems
- [ ] Include feature engineering suggestions
- [ ] Provide code snippets for manual implementation
- [ ] Add model hyperparameter recommendations
- [ ] Support multiple LLM providers (OpenAI, Anthropic, etc.)

## Testing

Run the test script to verify everything is working:
```bash
python test_llm.py
```

Expected output:
- ✅ Metadata analysis with specific recommendations
- ✅ Chat response with preprocessing guidance
- ✅ No errors in API calls

## Dependencies

New packages added:
- `groq>=0.33.0` - Groq API client
- `python-dotenv==1.0.0` - Environment variable management

Install with:
```bash
pip install -r requirements.txt
```

## Security Notes

- API key stored in `.env` file (not committed to git)
- `.env` added to `.gitignore`
- API key never exposed in frontend
- All LLM calls happen on backend

## Cost Considerations

Groq offers:
- **Free tier**: Generous rate limits for testing
- **Pay-as-you-go**: For production use
- Very fast inference times (sub-second responses)

Monitor usage at: https://console.groq.com/

---

**Status**: ✅ Fully functional and tested
**Last Updated**: November 4, 2025
