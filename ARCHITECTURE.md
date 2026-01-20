# Technical Architecture - Dynamic Insights System

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         STREAMLIT APP                        │
│                          (app.py)                            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│  DASHBOARD   │    │ PREDICTIVE MODEL │    │ INSIGHT CHAT │
│    PAGE      │    │      PAGE        │    │     PAGE     │
└──────────────┘    └──────────────────┘    └──────────────┘
                            │                      │
                            │                      │
                            ▼                      ▼
                    ┌───────────────┐      ┌───────────────┐
                    │ model_utils.py│      │chat_engine.py │
                    │               │      │               │
                    │ - Train Model │      │ - Query Router│
                    │ - Save .pkl   │      │ - Get Insights│
                    │ - Load .pkl   │      │ - Get Suggest.│
                    │ - Predict     │      └───────┬───────┘
                    └───────┬───────┘              │
                            │                      │
                            └──────────┬───────────┘
                                       │
                                       ▼
                            ┌──────────────────────┐
                            │  gemini_helper.py    │
                            │                      │
                            │ - Classify Intent    │
                            │ - Generate Insights  │
                            │ - Generate Suggest.  │
                            └──────────┬───────────┘
                                       │
                                       ▼
                            ┌──────────────────────┐
                            │   GEMINI API         │
                            │ (google.genai)       │
                            └──────────────────────┘
```

## Data Flow

### Training Flow
```
1. User uploads CSV
2. app.py → model_utils.run_model_pipeline(df)
3. Train RandomForestRegressor
4. Save model → aadhaar_model.pkl
5. Return R² and MAE metrics
6. Display to user
```

### Prediction Flow
```
1. User clicks "Generate Predictions"
2. app.py → model_utils.load_model()
3. Load from aadhaar_model.pkl
4. app.py → model_utils.make_predictions(df)
5. model.predict(X)
6. Return predictions + statistics
7. Display table and metrics
```

### Dynamic Insight Flow
```
1. User asks question in chat
2. app.py → chat_engine.respond_to_query(query, df)
3. chat_engine → gemini_helper.classify_intent(query)
4. Gemini API validates question is Aadhaar-related
5. chat_engine → model_utils.make_predictions(df)
6. Get prediction statistics
7. chat_engine → gemini_helper.generate_insight_from_predictions(stats, query)
8. Gemini API analyzes data + generates Finding/Impact/Recommendation
9. Return formatted insight
10. app.py → render_insight_card(insight)
```

### Dynamic Suggestions Flow
```
1. User clicks "Get Insight + Suggestions"
2. app.py → chat_engine.get_dynamic_suggestions(query, df)
3. Generate predictions and insight (as above)
4. chat_engine → gemini_helper.generate_suggestions_from_insight(insight)
5. Gemini API analyzes insight + creates 3-5 actionable suggestions
6. Return both insight and suggestions
7. app.py → render_insight_card(insight) + render_suggestions_card(suggestions)
```

## Component Responsibilities

### `app.py` (Frontend/Orchestration)
- Streamlit UI components
- Page routing (Dashboard, Model, Chat)
- File upload handling
- Session state management
- Rendering insights/suggestions
- Calling backend functions

### `model_utils.py` (ML Pipeline)
- Model training (RandomForest)
- Model persistence (pickle save/load)
- Prediction generation
- Statistical summary computation
- Feature engineering

### `chat_engine.py` (Business Logic)
- Query routing
- Intent validation
- Prediction-based response generation
- Fallback handling for untrained models
- Combining predictions + Gemini insights

### `gemini_helper.py` (AI Integration)
- Gemini API client setup
- Intent classification prompts
- Insight generation prompts
- Suggestion generation prompts
- Error handling with fallbacks

### `insights.py` (Analytics)
- Basic statistical insights
- Prediction-specific analytics
- Data aggregation helpers

## Key Design Patterns

### 1. **Separation of Concerns**
- UI (app.py) separate from logic (chat_engine.py)
- ML operations isolated in model_utils.py
- AI calls centralized in gemini_helper.py

### 2. **Fallback Strategy**
- Model not found → Static responses
- Gemini API fails → Hardcoded fallbacks
- Invalid question → Clear user guidance

### 3. **State Management**
- Model persisted to disk (.pkl)
- Chat history in st.session_state
- Model metrics cached in session

### 4. **Prompt Engineering**
- Specific formats enforced (Finding/Impact/Recommendation)
- Context-rich prompts to Gemini
- Clear instructions for output format

## API Integration

### Gemini API Calls

**Function: `classify_intent`**
- Purpose: Validate question relevance
- Input: User question string
- Output: Boolean (YES/NO)
- Fallback: Return False on error

**Function: `generate_insight_from_predictions`**
- Purpose: Generate structured insight
- Input: Prediction statistics + user question
- Output: Finding/Impact/Recommendation text
- Fallback: Generic formatted response

**Function: `generate_suggestions_from_insight`**
- Purpose: Create actionable suggestions
- Input: Generated insight
- Output: Numbered list of 3-5 suggestions
- Fallback: Generic suggestion list

## Model Format

### Input Features (Example)
```python
X = [
    'age_0_5',
    'age_5_17', 
    'age_18_greater',
    'male_updates',
    'female_updates',
    # ... other numeric features
]
```

### Target Variable
```python
y = 'total_activity'
```

### Model File
```
aadhaar_model.pkl
- Format: pickle
- Contains: Trained RandomForestRegressor
- Size: ~few MB depending on data
- Location: Project root directory
```

## Error Handling Matrix

| Error Condition | Handler | User Experience |
|----------------|---------|-----------------|
| No dataset uploaded | app.py check | "Upload dataset" info message |
| Model not trained | load_model() returns None | Warning + "Train model" prompt |
| Gemini API failure | Try/except in gemini_helper | Fallback to static responses |
| Invalid prediction | Exception in make_predictions | Error message displayed |
| Non-Aadhaar question | classify_intent returns False | Polite redirect message |

## Performance Considerations

1. **Model Loading**: Lazy load (on-demand, not at startup)
2. **Predictions**: Computed on button click, not auto
3. **API Calls**: Only when user explicitly requests
4. **Caching**: Model stays in memory once loaded
5. **Session State**: Chat history grows but cleared on refresh

## Security

- API key in environment variables (not hardcoded)
- No user data sent to Gemini (only aggregated statistics)
- Model file stored locally (not exposed)
- No authentication required (prototype mode)

## Extension Points

1. **Add more models**: Modify model_utils.py
2. **New insight types**: Add functions to gemini_helper.py
3. **Custom visualizations**: Extend Dashboard page
4. **Advanced prompts**: Update prompt templates in gemini_helper.py
5. **Export results**: Add download buttons in app.py
