# Serialized Model Artifacts

## Problem Statement
Training ML models is computationally expensive and slow. To enable real-time inference, models must be "frozen" or serialized into a format that can be quickly loaded into memory by the API.

## Solution Overview
This directory contains the **pickled (.pkl)** and **HDF5 (.keras)** files that represent the trained state of the Hybrid WAF engine. These are the "brains" of the system.

## Architecture Diagram
N/A - Storage for binaries.

## ML Models Used
### 1. `scaler.pkl`
*   **Type**: `sklearn.preprocessing.StandardScaler`
*   **Role**: Normalizes validation data to mean=0, std=1 (same as training data).

### 2. `isolation_forest.pkl`
*   **Type**: `sklearn.ensemble.IsolationForest`
*   **Role**: Anomaly Scoring (Outlier detection).

### 3. `autoencoder.keras`
*   **Type**: TensorFlow/Keras Functional Model
*   **Role**: Reconstruction Error (Deep Anomaly detection).

### 4. `xgboost.pkl`
*   **Type**: `xgboost.XGBClassifier`
*   **Role**: Multi-class classification (Signature detection).

## Dataset Used
Trained on the data described in `../model_train/README.md`.

## How to Run the Project
These files are **read-only** by the `api/app.py`. do NOT edit them manually.
To regenerate them, run the Training Pipeline in `../model_train/`.

## Results / Metrics
See `../model_train/README.md` for the performance metrics of these specific binaries.

## Innovation / Future Scope
*   **Model Versioning**: Currently supports one version. Future scope includes folder-based versioning (v1, v2) for A/B testing.
*   **Format**: Moving to ONNX format for cross-platform interoperability.
