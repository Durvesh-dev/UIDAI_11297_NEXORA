# 🆔 UIDAI Aadhaar Analytics Dashboard

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini_AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

**AI-Powered Analytics Platform for UIDAI Aadhaar Data with Predictive Insights**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Team](#-team)

</div>

---

## 📋 Overview

UIDAI Aadhaar Analytics is an intelligent dashboard designed for analyzing Aadhaar enrollment and update data across India. The platform combines **Machine Learning predictions** with **Google Gemini AI** to provide actionable insights for decision-makers at UIDAI.

## ✨ Features

### 📊 Interactive Dashboard
- Real-time visualization of Aadhaar statistics
- State-wise and district-wise analytics
- Trend analysis with interactive charts (Plotly)
- Dark/Light theme support

### 🤖 Predictive Analytics
- **ML Model**: Random Forest Regressor for demand prediction
- Model persistence (`.pkl` format) for reuse
- Prediction statistics with state-wise breakdown
- R² score and MAE metrics display

### 💬 AI-Powered Insight Chat
- Natural language query interface
- **Dynamic Insights**: Finding → Impact → Recommendation format
- Powered by **Google Gemini AI**
- Actionable suggestions generation

### 🎯 Smart Features
- Intent classification for relevant responses
- Auto-generated insights from predictions
- Context-aware AI analysis
- Responsive and modern UI

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- Google Gemini API Key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Durvesh-dev/UIDAI_11297_NEXORA.git
   cd UIDAI_11297_NEXORA
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   Windows:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Gemini API Key**
   
   Windows PowerShell:
   ```powershell
   $env:GEMINI_API_KEY = "your-api-key-here"
   ```
   
   Linux/Mac:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📖 Usage

### Getting Started

1. **Upload Dataset**: Use the sidebar to upload your Aadhaar CSV file
2. **Explore Dashboard**: View interactive visualizations and statistics
3. **Train Model**: Navigate to "Predictive Model" page and click "Train Prediction Model"
4. **Generate Predictions**: Click "Generate Predictions" to see forecasts
5. **Chat with AI**: Ask questions in the "Insight Chat" page

### Sample Questions for AI Chat
- "What do predictions show for high-activity states?"
- "What trends are predicted for next quarter?"
- "Which states need more enrollment centers?"
- "Analyze the update patterns in southern states"

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      STREAMLIT APP (app.py)                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│  DASHBOARD   │    │ PREDICTIVE MODEL │    │ INSIGHT CHAT │
└──────────────┘    └──────────────────┘    └──────────────┘
                            │                      │
                            ▼                      ▼
                    ┌───────────────┐      ┌───────────────┐
                    │ model_utils.py│      │chat_engine.py │
                    └───────────────┘      └───────────────┘
                            │                      │
                            └──────────┬───────────┘
                                       ▼
                            ┌──────────────────────┐
                            │  gemini_helper.py    │
                            │    (Gemini AI)       │
                            └──────────────────────┘
```

## 📁 Project Structure

```
UIDAI_11297_NEXORA/
├── app.py                    # Main Streamlit application
├── model_utils.py            # ML model training & predictions
├── chat_engine.py            # AI chat query handler
├── gemini_helper.py          # Gemini AI integration
├── insights.py               # Analytics & insight generation
├── requirements.txt          # Python dependencies
├── ARCHITECTURE.md           # Detailed architecture docs
├── IMPLEMENTATION_SUMMARY.md # Implementation details
├── QUICK_START.md            # Quick start guide
└── README.md                 # This file
```

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Visualization | Plotly |
| ML Model | scikit-learn (RandomForest) |
| AI Engine | Google Gemini AI |
| Data Processing | Pandas, NumPy |

## 👥 Team NEXORA

**Team ID:** 11297

| Contributor | Role |
|-------------|------|
| [Durvesh Bhadgaonkar](https://github.com/Durvesh-dev) | Developer |
| [Swapnil Surendra Kasare](https://github.com/MarkSpectre) | Developer |
| [Hassaan Tole](https://github.com/HuNTer8272) | Developer |
| [Vansh Jindam](https://github.com/Vansh940) | Developer |
| [Sarvesh Deshmukh](https://github.com/Hacker10250) | Developer |


