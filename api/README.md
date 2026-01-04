# WAF Inference API

## Problem Statement
Deploying heavy Machine Learning models directly within a consumer application (like a web dashboard) causes scalability issues, high latency, and blocks the main application thread. A dedicated inference service is needed to handle compute-intensive tasks independently.

## Solution Overview
This directory contains the **FastAPI Backend**, a high-performance, asynchronous web server that acts as the brain of the ML-WAF. It handles:
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
The API serves the following serialized models loaded from `../models/`:
*   `isolation_forest.pkl`
*   `autoencoder.keras`
*   `xgboost.pkl`
*   `scaler.pkl` (Preprocessing)

## Dataset Used
N/A - This component is for **Inference** only. It consumes live JSON payloads matching the feature structure of the training dataset.

## How to Run the Project
Navigate to the project root and run:
```bash
uvicorn api.app:app --port 8000 --reload
```
*   **Swagger Docs**: Access at `http://localhost:8000/docs`
*   **Health Check**: `http://localhost:8000/health`

## Results / Metrics
*   **Throughput**: Handles concurrent requests via `async` processing.
*   **Response Format**: standardized JSON with `decision`, `risk_score`, `latency_ms`, and `shap_values`.

## Innovation / Future Scope
*   **Decoupled Design**: Allows the backend to be scaled horizontally (e.g., multiple API workers) independent of the frontend.
*   **Future Scope**:
    *   Redis Caching for frequent requests.
    *   API Key Authentication.
    *   gRPC support for ultra-low latency.
