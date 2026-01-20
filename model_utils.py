import os
import pickle
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score

MODEL_PATH = "aadhaar_model.pkl"

def preprocess_data(df):
    """Preprocess dataframe with feature engineering"""
    df = df.copy()
    
    # Date features
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.month.astype('int8')
        df['year'] = df['date'].dt.year.astype('int16')
    else:
        # If no date column, use defaults
        df['month'] = 1
        df['year'] = 2024
    
    # Ensure pincode is string
    if 'pincode' in df.columns:
        df['pincode'] = df['pincode'].astype(str)
        df = df.sort_values(['pincode', 'date'] if 'date' in df.columns else ['pincode'])
        
        # LAG 1 (Previous Month)
        df['lag_1m'] = df['total_activity'].shift(1)
        mask_1 = df['pincode'] == df['pincode'].shift(1)
        df.loc[~mask_1, 'lag_1m'] = 0
        
        # LAG 12 (Seasonality - Last Year)
        df['lag_12m'] = df['total_activity'].shift(12)
        mask_12 = df['pincode'] == df['pincode'].shift(12)
        df.loc[~mask_12, 'lag_12m'] = 0
        
        # ROLLING 3 MONTHS (Trend)
        v1 = df['total_activity'].shift(1)
        v2 = df['total_activity'].shift(2)
        v3 = df['total_activity'].shift(3)
        mask_roll = (df['pincode'] == df['pincode'].shift(1)) & \
                    (df['pincode'] == df['pincode'].shift(2)) & \
                    (df['pincode'] == df['pincode'].shift(3))
        df['rolling_3m'] = (v1 + v2 + v3) / 3
        df.loc[~mask_roll, 'rolling_3m'] = 0
    else:
        df['lag_1m'] = 0
        df['lag_12m'] = 0
        df['rolling_3m'] = 0
    
    # Fill NaNs
    df.fillna(0, inplace=True)
    
    # Clustering
    cluster_cols = ['age_0_5', 'age_5_17', 'age_18_greater',
                    'demo_age_5_17', 'demo_age_18_greater',
                    'bio_age_5_17', 'bio_age_18_greater']
    valid_cols = [c for c in cluster_cols if c in df.columns]
    
    if valid_cols and len(df) >= 3:
        kmeans = KMeans(n_clusters=min(3, len(df)), random_state=42, n_init=10)
        df['cluster_label'] = kmeans.fit_predict(df[valid_cols])
    else:
        df['cluster_label'] = 0
    
    # Encode categorical columns
    le_state = LabelEncoder()
    le_dist = LabelEncoder()
    
    if 'state' in df.columns:
        df['state_code'] = le_state.fit_transform(df['state'].astype(str))
    else:
        df['state_code'] = 0
        
    if 'district' in df.columns:
        df['district_code'] = le_dist.fit_transform(df['district'].astype(str))
    else:
        df['district_code'] = 0
    
    return df, le_state, le_dist

def run_model_pipeline(df):
    """Train model with full pipeline and save as .pkl file"""
    print("⚙️ Preprocessing data...")
    df_clean, le_state, le_dist = preprocess_data(df)
    
    # Log transform target
    y_target_log = np.log1p(df_clean['total_activity'])
    
    # Features
    X_features = [
        'state_code', 'district_code', 'month', 'year', 'cluster_label',
        'lag_1m', 'rolling_3m', 'lag_12m'
    ]
    
    # Ensure all features exist
    for feat in X_features:
        if feat not in df_clean.columns:
            df_clean[feat] = 0
    
    X = df_clean[X_features]
    y = y_target_log
    
    X_train, X_test, y_train_log, y_test_log = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("🚀 Training RandomForest model...")
    rf_model = RandomForestRegressor(
        n_estimators=100, 
        max_depth=25, 
        random_state=42, 
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train_log)
    print("✅ Model trained!")
    
    # Evaluate
    y_pred_log = rf_model.predict(X_test)
    y_pred_real = np.expm1(y_pred_log)
    y_test_real = np.expm1(y_test_log)
    
    mae = mean_absolute_error(y_test_real, y_pred_real)
    r2 = r2_score(y_test_real, y_pred_real)
    
    # Save model and encoders
    model_data = {
        'model': rf_model,
        'le_state': le_state,
        'le_dist': le_dist,
        'features': X_features,
        'r2_score': r2,
        'mae': mae
    }
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"💾 Model saved to {MODEL_PATH}")
    print(f"📊 R² Score: {r2:.5f}, MAE: {mae:.1f}")
    
    return r2, mae

def load_model():
    """Load the trained model from .pkl file"""
    if not os.path.exists(MODEL_PATH):
        return None
    
    try:
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        # If model is corrupted or incompatible, delete it and return None
        try:
            os.remove(MODEL_PATH)
        except:
            pass
        return None

def make_predictions(df, feature_subset=None):
    """Make predictions using the loaded model"""
    model_data = load_model()
    
    if model_data is None:
        raise ValueError("Model not found. Please train the model first.")
    
    rf_model = model_data['model']
    features = model_data['features']
    
    # Preprocess input data
    df_processed, _, _ = preprocess_data(df)
    
    # Ensure all features exist
    for feat in features:
        if feat not in df_processed.columns:
            df_processed[feat] = 0
    
    X = df_processed[features]
    
    # Predict (model outputs log-transformed values)
    predictions_log = rf_model.predict(X)
    
    # Convert back from log scale
    predictions = np.expm1(predictions_log)
    
    # Return predictions with metadata
    result_df = df.copy()
    result_df['predicted_activity'] = predictions
    
    return result_df, predictions

def get_prediction_summary(df, predictions):
    """Generate summary statistics from predictions"""
    summary = {
        "total_predicted": float(predictions.sum()),
        "mean_predicted": float(predictions.mean()),
        "max_predicted": float(predictions.max()),
        "min_predicted": float(predictions.min()),
        "std_predicted": float(predictions.std())
    }
    
    # Add state-wise predictions if state column exists
    if 'state' in df.columns:
        state_predictions = df.copy()
        state_predictions['predicted_activity'] = predictions
        state_summary = state_predictions.groupby('state')['predicted_activity'].agg(['sum', 'mean']).to_dict()
        summary['by_state'] = state_summary
    
    return summary

def get_model_metrics():
    """Get stored model metrics from .pkl file"""
    model_data = load_model()
    if model_data and 'r2_score' in model_data and 'mae' in model_data:
        return model_data['r2_score'], model_data['mae']
    return None, None
