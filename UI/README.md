# WAF Admin Dashboard

## Problem Statement
Security analysts are often overwhelmed by raw logs and black-box alerts. They lack a visual interface to simulate traffic, understand why a specific request was blocked, and provide feedback to the system.

## Solution Overview
This directory contains the **Streamlit Frontend**, a lightweight, interactive dashboard designed for SecOps professionals. It connects to the backend API to provide:
*   Real-time Traffic Simulation.
*   Visual Risk Assessment (Speedometers/Gauges).
*   Detailed Attack Attribution & Explainability.

## Architecture Diagram
```mermaid
graph TD
    User --> Sidebar[Simulation Sidebar]
    Sidebar --> API[Call Backend API]
    API --> Main[Main Dashboard]
    Main --> Cards[Metric Cards]
    Main --> Charts[Visualization/SHAP]
    Main --> Rules[Rule Logic]
```

## Dataset Used
*   `../data/test_samples_final.csv`: Used to populate the "Traffic Simulator" dropdown for testing purposes.

## How to Run the Project
Navigate to the project root and run:
```bash
streamlit run UI/waf_gui.py
```
*Note: Ensure the backend API is running on port 8000 first.*

## Results / Metrics
*   **User Experience**: "Dark Mode" aesthetic for reduced eye strain in SOC environments.
*   **Interactivity**: Instant feedback loop (Simulation -> Result).

## Innovation / Future Scope
*   **No-Code Interface**: Allows non-technical users to inspect ML model behavior.
*   **Rule Engine**: Translates ML probability into human-readable action (BLOCK/ALLOW).
