def generate_insights(df):
    """Generate basic statistical insights from dataframe"""
    insights = {
        "total_activity": int(df["total_activity"].sum())
    }
    
    if "state" in df.columns:
        insights["top_state"] = df.groupby("state")["total_activity"].sum().idxmax()
        insights["state_count"] = df["state"].nunique()
    
    return insights

def generate_prediction_insights(predictions_df):
    """Generate insights specifically from prediction results"""
    insights = {}
    
    if 'predicted_activity' in predictions_df.columns:
        insights['total_predicted'] = float(predictions_df['predicted_activity'].sum())
        insights['mean_predicted'] = float(predictions_df['predicted_activity'].mean())
        insights['max_predicted'] = float(predictions_df['predicted_activity'].max())
        insights['min_predicted'] = float(predictions_df['predicted_activity'].min())
        
        if 'state' in predictions_df.columns:
            state_pred = predictions_df.groupby('state')['predicted_activity'].sum()
            insights['top_predicted_state'] = state_pred.idxmax()
            insights['top_predicted_value'] = float(state_pred.max())
    
    return insights
