# SNCF Reliability & Delay Analytics Pipeline

[![CI Pipeline](https://github.com/Hoanghoccode2805/sncf-delay-mlops/actions/workflows/ci.yml/badge.svg)](https://github.com/Hoanghoccode2805/sncf-delay-mlops/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production_Ready-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Render](https://img.shields.io/badge/Render-Deployed-black.svg)](https://render.com/)

> An end-to-end Machine Learning Operations (MLOps) pipeline designed to predict train delays across the SNCF railway network. This project bridges the gap between raw transportation data and a production-grade, serverless API.

---

## 1. Live Demo & API Endpoint
The inference API is deployed and actively running on Render. You can interact with the machine learning model directly via the Swagger UI interface:

🔗 **[SNCF Delay Prediction API - Swagger UI](https://sncf-delay-api-ih3x.onrender.com/docs)** 
*(Note: As this is hosted on a free serverless tier, the initial cold start may take ~30-50 seconds. Subsequent requests will execute instantly).*

---

## 2. Business Impact & Real-World Value
This project goes beyond predictive modeling; it offers a scalable solution for modern transportation engineering and logistics:
* **Proactive Resource Allocation:** By forecasting delays, railway operators can dynamically adjust crew schedules, platform assignments, and maintenance tasks, minimizing cascading bottlenecks.
* **Enhanced Passenger Experience:** Integrating this API into ticketing systems allows for real-time, data-driven alerts, significantly improving customer trust and communication.
* **Strategic Route Optimization:** The pipeline isolates and analyzes the 5 most critical/optimal routes, providing stakeholders with actionable insights to optimize infrastructure investments where they matter most.

---

## 3. System Architecture & Workflow
The project was developed strictly adhering to the MLOps lifecycle, combining Data Engineering, Data Science, and Software Engineering:

1. **Data Engineering (ETL):** Extracted massive SNCF operational datasets, cleaned anomalies, and engineered features. Specifically filtered and isolated the **Top 5 optimal routes** to ensure model efficiency and high-fidelity predictions.
2. **Modeling & Experimentation:** Trained a robust **Random Forest** algorithm.
3. **Software Engineering:** Wrapped the static model artifacts (`model.pkl`) into a high-performance **FastAPI** application with built-in health checks (`/health`).
4. **Containerization:** Encapsulated the entire inference environment into a lightweight **Docker** container, completely isolating it from the host machine to guarantee the "it works on my machine" principle globally.
5. **CI/CD & Cloud Deployment:** Automated the quality control process using **GitHub Actions**. Every code commit triggers a pipeline that verifies dependencies, model artifacts, and Docker build integrity before seamlessly deploying the container to **Render**.

---

## 4. CI/CD Pipeline & Serverless Deployment
To achieve a true Enterprise-grade architecture, a fully automated Continuous Integration and Continuous Deployment (CI/CD) pipeline was established:
* **Continuous Integration (CI):** Powered by **GitHub Actions**, every code push triggers an automated workflow that sets up a virtual Ubuntu environment, installs dependencies, verifies the existence of model artifacts, and validates the Docker build process.
* **Continuous Deployment (CD):** Once the CI pipeline passes (Green Badge), **Render** automatically detects the new commit, pulls the Docker image, and deploys it with zero downtime.
* **Result:** A self-sustaining loop where new algorithm updates can be pushed to production safely and automatically within minutes.

---
## 5. Technology Stack
* **Data Science:** `Pandas`, `Scikit-learn`, `MLflow` (Experiment tracking)
* **Backend API:** `FastAPI`, `Uvicorn`, `Pydantic` (Data validation)
* **DevOps & MLOps:** `Docker`, `GitHub Actions`, `Render` (PaaS)
* **Testing:** `Pytest`

---

## 6. Local Setup & Development

If you wish to run this architecture locally on your machine, ensure you have Docker installed.

**Step 1: Clone the repository**
```bash
git clone https://github.com/Hoanghoccode2805/sncf-delay-mlops.git
cd sncf-delay-mlops
```

**Step 2: Build the Docker Image**
```bash
docker build -t sncf-delay-api:local .
```

**Step 3: Run the Container**
```bash
docker run -p 8000:8000 sncf-delay-api:local
```

**Step 4: Access the Local API**
Navigate to `http://localhost:8000/docs` in your web browser to test the endpoints.

---

## Author

**Nhat Hoang BUI**

*Student in Mathematics at Paris Cité | Aspiring Data Scientist / ML Engineer / AI Engineer*

* Passionate about Data Engineering, Applied Mathematics, and building scalable, data-driven architectures that solve complex real-world problems. 
* Constantly exploring the intersection of Software Engineering and Machine Learning.