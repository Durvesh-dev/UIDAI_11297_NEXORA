from gemini_helper import (
    generate_insight_from_data,
    generate_suggestions_from_insight,
    answer_general_question,
    get_simple_answer
)
from model_utils import make_predictions, get_prediction_summary, load_model
import numpy as np

def get_data_summary(df):
    """Generate comprehensive data summary for Gemini context"""
    summary = {}
    
    # Basic stats
    summary['total_rows'] = len(df)
    
    if 'total_activity' in df.columns:
        summary['total_activity'] = int(df['total_activity'].sum())
        summary['avg_activity'] = float(df['total_activity'].mean())
        summary['max_activity'] = float(df['total_activity'].max())
        summary['min_activity'] = float(df['total_activity'].min())
    
    # State-wise stats
    if 'state' in df.columns:
        state_activity = df.groupby('state')['total_activity'].sum().sort_values(ascending=False)
        summary['top_5_states'] = state_activity.head(5).to_dict()
        summary['bottom_5_states'] = state_activity.tail(5).to_dict()
        summary['total_states'] = df['state'].nunique()
        summary['highest_state'] = state_activity.idxmax()
        summary['lowest_state'] = state_activity.idxmin()
    
    # District-wise stats
    if 'district' in df.columns:
        summary['total_districts'] = df['district'].nunique()
    
    # Age group stats
    age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    age_data = {}
    for col in age_cols:
        if col in df.columns:
            age_data[col] = int(df[col].sum())
    if age_data:
        summary['age_groups'] = age_data
        summary['highest_age_group'] = max(age_data, key=age_data.get)
    
    # Demographic vs Biometric
    demo_cols = ['demo_age_5_17', 'demo_age_18_greater']
    bio_cols = ['bio_age_5_17', 'bio_age_18_greater']
    
    demo_total = sum(df[col].sum() for col in demo_cols if col in df.columns)
    bio_total = sum(df[col].sum() for col in bio_cols if col in df.columns)
    
    if demo_total > 0 or bio_total > 0:
        summary['demographic_updates'] = int(demo_total)
        summary['biometric_updates'] = int(bio_total)
    
    return summary

def is_data_question(query):
    """Check if the question requires data analysis"""
    data_keywords = [
        'state', 'district', 'highest', 'lowest', 'most', 'least',
        'predict', 'trend', 'activity', 'total', 'average', 'mean',
        'maximum', 'minimum', 'data', 'statistics', 'stats', 'analysis',
        'demographic', 'biometric', 'age group', 'region', 'compare',
        'which', 'how many', 'how much', 'count', 'number'
    ]
    q_lower = query.lower()
    return any(kw in q_lower for kw in data_keywords)

def respond_to_query(query, df, model_metrics=None, use_dynamic_insights=True):
    """
    Respond to user queries using Gemini API with data context
    """
    # Get data summary for context
    data_summary = get_data_summary(df)
    
    # Check if model is available for predictions
    model_data = load_model()
    prediction_summary = None
    
    if model_data is not None:
        try:
            predictions_df, predictions = make_predictions(df)
            prediction_summary = get_prediction_summary(df, predictions)
        except Exception as e:
            print(f"Prediction error: {e}")
            prediction_summary = None
    
    # Check if this is a data-specific question or general question
    if is_data_question(query):
        # Use data + predictions + Gemini for data questions
        insight = generate_insight_from_data(data_summary, prediction_summary, query)
    else:
        # Use Gemini for general Aadhaar questions
        insight = answer_general_question(query, data_summary)
    
    return insight

def get_dynamic_suggestions(query, df):
    """
    Get both insights and suggestions dynamically
    Works with or without trained model
    """
    # Get data summary
    data_summary = get_data_summary(df)
    
    # Try to get predictions if model exists
    model_data = load_model()
    prediction_summary = None
    
    if model_data is not None:
        try:
            predictions_df, predictions = make_predictions(df)
            prediction_summary = get_prediction_summary(df, predictions)
        except Exception as e:
            print(f"Prediction error: {e}")
    
    # Generate insight based on question type
    if is_data_question(query):
        insight = generate_insight_from_data(data_summary, prediction_summary, query)
    else:
        insight = answer_general_question(query, data_summary)
    
    # Generate suggestions
    suggestions = generate_suggestions_from_insight(insight, data_summary)
    
    return insight, suggestions

def get_auto_insights(df):
    """
    Generate automatic insights when CSV is uploaded
    Works with or without trained model
    """
    data_summary = get_data_summary(df)
    
    # Try predictions if model exists
    model_data = load_model()
    prediction_summary = None
    
    if model_data is not None:
        try:
            predictions_df, predictions = make_predictions(df)
            prediction_summary = get_prediction_summary(df, predictions)
        except:
            pass
    
    # Generate comprehensive insight
    auto_query = "Provide a comprehensive analysis of the Aadhaar data including state-wise activity, demographic patterns, and key trends."
    insight = generate_insight_from_data(data_summary, prediction_summary, auto_query)
    suggestions = generate_suggestions_from_insight(insight, data_summary)
    
    return insight, suggestions

def get_chat_answer(query, df):
    """
    Get a simple, direct answer to a chat question.
    Returns just the answer text (no insights/suggestions format).
    """
    # Get data summary for context
    data_summary = get_data_summary(df)
    
    # Try to get predictions if model exists
    model_data = load_model()
    prediction_summary = None
    
    if model_data is not None:
        try:
            predictions_df, predictions = make_predictions(df)
            prediction_summary = get_prediction_summary(df, predictions)
        except Exception as e:
            print(f"Prediction error: {e}")
    
    # Get simple answer
    answer = get_simple_answer(data_summary, prediction_summary, query)
    return answer