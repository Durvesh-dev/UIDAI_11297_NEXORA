# Quick Start Guide - Dynamic Insights System

## 🚀 Quick Setup

1. **Install dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Gemini API Key** (already done):
   ```powershell
   setx GEMINI_API_KEY "AIzaSyAZbZ_uj_SBb_m3xXFwYnTnhddUiO6eW7U"
   ```

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## 📊 Usage Flow

### First Time Setup
1. **Upload Dataset**: Use sidebar to upload your Aadhaar CSV file
2. **Train Model**: 
   - Go to "Predictive Model" page
   - Click "Train Prediction Model"
   - Wait for training (saves as `aadhaar_model.pkl`)
3. **Generate Predictions**:
   - Click "Generate Predictions"
   - View prediction statistics

### Using Dynamic Insights

#### Option 1: Get AI Insight Only
1. Go to "Insight Chat" page
2. Ask a question like:
   - "What do predictions show for high-activity states?"
   - "What trends are predicted for next quarter?"
3. Click **"Get Insight"**
4. Receive AI-generated Finding/Impact/Recommendation

#### Option 2: Get Insight + Suggestions
1. Ask your question
2. Click **"Get Insight + Suggestions"**
3. Receive:
   - **Insight Card**: Analysis with Finding/Impact/Recommendation
   - **Suggestions Card**: 3-5 actionable next steps

## 🔄 How Dynamic Generation Works

```
Your Question
    ↓
Load .pkl Model
    ↓
Generate Predictions on Data
    ↓
Compute Statistics (total, mean, state-wise)
    ↓
Send to Gemini API with your question
    ↓
Gemini analyzes predictions + question
    ↓
Returns custom Finding/Impact/Recommendation
    ↓
(Optional) Gemini generates specific suggestions
    ↓
Display formatted results
```

## 💡 Example Questions for Best Results

**Good Questions** (specific, prediction-focused):
- ✅ "What are the predicted activity levels by state?"
- ✅ "Which regions need more resources based on forecasts?"
- ✅ "What demographic patterns do predictions reveal?"
- ✅ "How accurate are our predictions?"

**Basic Questions** (still work, may use static responses):
- ⚠️ "Tell me about age groups"
- ⚠️ "Which state has most activity?"

## 🎯 Features Summary

| Feature | Description |
|---------|-------------|
| **Model Persistence** | Train once, model saved as `.pkl` for reuse |
| **Dynamic Predictions** | Real-time predictions on your data |
| **AI Insights** | Gemini analyzes predictions and generates insights |
| **AI Suggestions** | Gemini creates actionable recommendations |
| **Smart Filtering** | Automatically detects non-Aadhaar questions |
| **Fallback Mode** | Works even if model not trained (static responses) |

## 🔧 Troubleshooting

**"Model not found" error:**
- Go to Predictive Model page
- Click "Train Prediction Model"
- Model will save as `aadhaar_model.pkl`

**Static insights instead of dynamic:**
- Train the model first (see above)
- Model must exist for dynamic predictions

**Gemini API errors:**
- Check API key is set correctly
- Verify internet connection
- System falls back to default responses if API fails

## 📁 Files Generated

- `aadhaar_model.pkl` - Trained Random Forest model (created after training)
- Chat history stored in session state (resets on page refresh)

## 🔐 Security Note

Your API key is stored in environment variables and not exposed in the code. The current key in your terminal will work for this session.
