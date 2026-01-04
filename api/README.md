# WAF Inference API

## Problem Statement
Deploying heavy Machine Learning models directly within a consumer application (like a web dashboard) blocks the main thread, causing scalability issues and high latency. A dedicated, asynchronous inference service is needed to handle compute-intensive security tasks independently.

## Solution Overview
This directory contains the **FastAPI Backend**, a high-performance web server that acts as the brain of the ML-WAF. It handles:
*   Model Lifecycle Management (Loading/Unloading).
*   Request Validation (Pydantic).
*   Real-time Inference.
*   Feature Extraction & Scaling.

## Architecture Diagram
```mermaid
graph TD
    Client[Client Request] --> Docs[/docs Swagger UI]
    Client --> Health[/health Endpoint]
    Client --> Inspect[/api/v1/inspect Endpoint]
    Inspect --> Pre[Preprocessing]
    Pre --> Models[ML Models]
    Models --> JSON[JSON Response]
```

## ML Models Used
The API loads serialized models from `../models/`:
*   `isolation_forest.pkl` (Anomaly Score)
*   `autoencoder.keras` (Reconstruction Error)
*   `xgboost.pkl` (Attack Classification)
*   `scaler.pkl` (Feature Normalization)

## How to Run the Project
Navigate to the project root and run:
```bash
uvicorn api.app:app --port 8000 --reload
```
*   **Swagger Docs**: Access at `http://localhost:8000/docs`
*   **Health Check**: `http://localhost:8000/health`

## Results / Metrics
*   **Throughput**: Optimized for concurrent requests via `async` processing.
*   **Response Format**: Standardized JSON with `decision`, `risk_score`, `latency_ms`, and `shap_values`.

## Innovation / Future Scope
*   **Decoupled Design**: Scaling the ML layer independently of the frontend.
*   **Smart Loading**: Automatically handles compressed model files (`.pkl.gz`) to bypass GitHub file size limits.
