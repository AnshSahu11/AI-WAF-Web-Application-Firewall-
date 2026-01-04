from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
import shap
import time
from typing import Dict, Any, List, Optional
import os

app = FastAPI(title="ML-WAF Engine")

# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------
IF_HIGH = 0.05
AE_HIGH = 0.05
XGB_HIGH = 0.5

FEATURE_COLS = [
    'Flow Duration', 'Flow Bytes/s', 'Flow Packets/s', 'Down/Up Ratio', 
    'Total Fwd Packets', 'Total Backward Packets', 'Fwd Packets/s', 'Bwd Packets/s', 
    'Min Packet Length', 'Max Packet Length', 'Packet Length Mean', 'Packet Length Std', 
    'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 
    'Bwd Packet Length Std', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 
    'Fwd IAT Mean', 'Fwd IAT Std', 'Bwd IAT Mean', 'Bwd IAT Std', 'SYN Flag Count', 
    'ACK Flag Count', 'RST Flag Count', 'PSH Flag Count', 'Fwd Header Length', 
    'Bwd Header Length', 'Avg Fwd Segment Size', 'Avg Bwd Segment Size', 'Active Mean', 
    'Idle Mean', 'Packet Rate Intensity', 'Byte Efficiency Ratio', 
    'Directional Asymmetry Score', 'Flag Aggression Index', 'Burstiness Score', 
    'Packet Size Variance Ratio', 'Flow Stability Index'
]

# ---------------------------------------------------------
# GLOBAL STATE
# ---------------------------------------------------------
models = {
    "scaler": None,
    "iso": None,
    "xgb": None,
    "autoencoder": None,
    "explainer": None
}
loading_error = None

# ---------------------------------------------------------
# LOADMODELS
# ---------------------------------------------------------
@app.on_event("startup")
def load_models():
    global loading_error
    print("Loading models...")
    try:
        # Models are in 'models/' directory based on current structure
        models["scaler"] = joblib.load("models/scaler.pkl")
        models["iso"] = joblib.load("models/isolation_forest.pkl")
        models["xgb"] = joblib.load("models/xgboost.pkl")
        models["autoencoder"] = load_model("models/autoencoder.keras")
        
        # Initialize SHAP
        try:
            models["explainer"] = shap.TreeExplainer(models["xgb"])
            print("SHAP explainer loaded.")
        except Exception as e:
            print(f"SHAP failed: {e}")
            
        print("All models loaded successfully.")
    except Exception as e:
        loading_error = str(e)
        print(f"CRITICAL: Failed to load models: {e}")

# ---------------------------------------------------------
# LOGIC
# ---------------------------------------------------------
def prepare_input(payload):
    row_values = []
    for feature in FEATURE_COLS:
        val = payload.get(feature, 0.0)
        try:
            val = float(val)
        except (ValueError, TypeError):
            val = 0.0
        row_values.append(val)

    X_arr = np.array([row_values], dtype=np.float32)
    df = pd.DataFrame(X_arr, columns=FEATURE_COLS)
    
    scaler = models["scaler"]
    if scaler:
        X_scaled = scaler.transform(df).astype(np.float32)
    else:
        X_scaled = X_arr # Fallback/Error state

    return df, X_scaled

def hybrid_decision_state(if_score, ae_score, xgb_score):
    if if_score >= IF_HIGH and ae_score >= AE_HIGH:
        return "REVIEW_REQUIRED", "Behavioral anomaly detected (IF + AE high) → possible zero-day"
    elif xgb_score >= XGB_HIGH:
        return "REVIEW_REQUIRED", "Known attack signature detected (XGBoost high confidence)"
    elif if_score >= IF_HIGH and ae_score < AE_HIGH:
        return "NORMAL", "Benign traffic burst or noise (IF high, AE low)"
    else:
        return "NORMAL", "No behavioral or signature-based anomaly detected"

# ---------------------------------------------------------
# API
# ---------------------------------------------------------
class InspectRequest(BaseModel):
    # Allow flexible dict input to match current behavior
    features: Dict[str, Any]

@app.post("/api/v1/inspect")
def inspect_traffic(request: InspectRequest):
    if not models["scaler"]:
        error_msg = f"Models not loaded. Error: {loading_error}" if loading_error else "Models not loaded (Unknown reason)"
        raise HTTPException(status_code=503, detail=error_msg)
        
    start_time = time.time()
    payload = request.features
    
    # Preprocess
    df_input, X_scaled = prepare_input(payload)
    
    # 1. Isolation Forest
    t1 = time.time()
    raw_if = models["iso"].decision_function(X_scaled)[0]
    if_score = float(-raw_if)
    t2 = time.time()
    
    # 2. Autoencoder
    # Using Call for speed
    X_recon = models["autoencoder"](X_scaled, training=False).numpy()
    ae_score = float(np.mean(np.power(X_scaled - X_recon, 2)))
    t3 = time.time()
    
    # 3. XGBoost
    probs = models["xgb"].predict_proba(X_scaled)[0]
    xgb_prob = float(1.0 - probs[0]) # Prob of being attack (class 1+)
    pred_class = int(models["xgb"].predict(X_scaled)[0])
    t4 = time.time()
    
    # Decision
    decision, reason = hybrid_decision_state(if_score, ae_score, xgb_prob)
    final_risk = float(max(if_score, ae_score, xgb_prob))
    
    # Rule Recommendation
    action = "BLOCK" if decision == "REVIEW_REQUIRED" else "ALLOW"
    confidence = "Low"
    if final_risk > 0.8: confidence = "High"
    elif final_risk > 0.5: confidence = "Moderate"
    
    # Metrics
    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000
    
    # SHAP
    shap_data = []
    shap_latency_ms = 0
    if final_risk > 0.3 and models["explainer"]:
        try:
            t0_shap = time.time()
            shap_values_raw = models["explainer"].shap_values(X_scaled)
            
            # Target Class Logic
            target_class = 1
            if pred_class != 0:
                target_class = pred_class
            else:
                target_class = np.argmax(probs[1:]) + 1
            
            # Extract
            if isinstance(shap_values_raw, list):
                vals = shap_values_raw[target_class][0]
            elif len(shap_values_raw.shape) == 3:
                vals = shap_values_raw[0, :, target_class]
            else:
                vals = shap_values_raw[0]
                
            # Process Top Contributors
            pos_indices = [i for i in range(len(vals)) if vals[i] > 0]
            pos_indices.sort(key=lambda i: vals[i], reverse=True)
            top5 = pos_indices[:5]
            
            if top5:
                max_shap = vals[top5[0]]
                for i in top5:
                    current_shap = vals[i]
                    impact = "Moderate Impact"
                    if max_shap > 0:
                        ratio = current_shap / max_shap
                        if ratio > 0.75: impact = "Very High Impact"
                        elif ratio > 0.4: impact = "High Impact"
                        
                    shap_data.append({
                        "feature": FEATURE_COLS[i],
                        "impact_label": impact,
                        "value": float(X_scaled[0, i]),
                        "shap_value": float(current_shap)
                    })
                    
            t1_shap = time.time()
            shap_latency_ms = (t1_shap - t0_shap) * 1000
            
        except Exception as e:
            print(f"SHAP Error: {e}")

    return {
        "status": "success",
        "decision": decision,
        "risk_score": final_risk,
        "reason": reason,
        "action": action,
        "confidence": confidence,
        "metrics": {
            "if_score": if_score,
            "ae_score": ae_score,
            "xgb_prob": xgb_prob,
            "pred_class": pred_class
        },
        "latency": {
            "total_ms": latency_ms,
            "shap_ms": shap_latency_ms,
            "breakdown": {
                "iso_ms": (t2-t1)*1000,
                "ae_ms": (t3-t2)*1000,
                "xgb_ms": (t4-t3)*1000
            }
        },
        "shap": shap_data
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "models_loaded": models["scaler"] is not None}
