# ML-WAF Module: Technical Description Document
**Project:** Swavlamban 2025 Hackathon Challenge 3  
**Module:** Machine Learning Enabled Network Anomaly Detection

---

## 1. Executive Summary
This project delivers a **Hybrid Machine Learning WAF Module** designed to augment traditional firewall capabilities. By acting as an intelligent sidecar, it inspects network traffic in real-time, detecting both known signatures (via XGBoost) and zero-day anomalies (via Isolation Forests and Autoencoders). The system includes a secure FastAPI backend and a "Dark Mode" Streamlit dashboard for Security Operations Centers (SOC).

## 2. System Architecture
The solution follows a decoupled **Client-Server Architecture** to ensure high availability and scalability (Requirement 3.4).

### 2.1 Backend (Inference Engine)
*   **Framework**: FastAPI (Python).
*   **Concurrency**: Uses `async/await` for non-blocking I/O, capable of handling high-throughput traffic logs.
*   **Endpoints**:
    *   `POST /api/v1/inspect`: The primary entry point. Receives raw JSON flow identifiers (70+ features) and returns a normalized risk object.
    *   `GET /health`: Kubernetes-ready health checks.

### 2.2 Frontend (Visualization)
*   **Framework**: Streamlit.
*   **Role**: Serves as the "Administrator GUI" (Requirement 3.1).
*   **Key Features**:
    *   Traffic Simulation Controls.
    *   Real-time Risk Gauges (Safe/Suspicious/Critical).
    *   Explainability Panel (Why was this blocked?).

## 3. Machine Learning Methodology (Requirement 3.2)
We employ a **Stacked Ensemble** approach to minimize False Positives while maximizing detection coverage.

### 3.1 The "Hybrid" Decision Logic
A request is only flagged if it violates one of the tiered security layers:
1.  **Layer 1: Global Anomaly Detection (Isolation Forest)**
    *   Unsupervised model.
    *   Detects statistical outliers in high-dimensional space (e.g., massive flow duration deviations).
2.  **Layer 2: Deep Pattern Anomaly (Autoencoder)**
    *   Semi-supervised Deep Learning (TensorFlow/Keras).
    *   Trained *only* on benign traffic.
    *   Traffic with high **Reconstruction Error** (> 99th percentile) is flagged as a potential Zero-Day attack.
3.  **Layer 3: Attack Classification (XGBoost)**
    *   Supervised Gradient Boosting.
    *   Classifies specific signatures: `SQL Injection`, `DDoS`, `XSS`, `Brute Force`.
    *   Uses **Class Weights** to handle imbalanced training data.

### 3.2 Explainable AI (XAI)
To combat "Black Box" fatigue (Requirement 5.1), we utilize **SHAP (SHapley Additive exPlanations)**. Every high-risk decision is accompanied by:
*   The Top 3 contributing features.
*   Direction of impact (e.g., "High Packet Rate increased risk by 40%").

## 4. Performance & Scalability
*   **Serialization**: Models are pre-loaded into RAM on startup (lazy loading disabled) to ensure sub-15ms inference latencies.
*   **Batching**: The API design supports batched inference for future high-volume log ingestion.

## 5. Integration Strategy
This module is designed to integrate with open-source WAFs (e.g., ModSecurity, Coraza) via **Asynchronous Audit Logging**:
1.  **WAF** processes request -> Logs metadata to Queue (Kafka/Redis).
2.  **ML-WAF** consumes log -> Computes Risk Score.
3.  **Feedback**: If Risk > Threshold, ML-WAF pushes a dynamic rule update to the WAF edge.

## 6. How to Build & Run
**(See README.md for detailed steps)**
1.  **Prerequisites**: Python 3.10+, pip.
2.  **One-Click Launch**: Run `run_app.bat` (Windows).
3.  **Manual**:
    ```bash
    uvicorn api.app:app --port 8000
    streamlit run UI/waf_gui.py
    ```

## 7. Future Roadmap
*   **Active Learning**: Automate the feedback loop where "False Positives" marked in the UI automatically retrain the Autoencoder.
*   **Encrypted Traffic**: Integration with TLS termination proxies (e.g., Nginx) to inspect decrypted payloads before re-encryption.
