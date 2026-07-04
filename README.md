# 🇹🇼 Taiwan Weather Intelligence & Machine Learning Analytics Portal

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Plotly Charts](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-1D89D1?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io)

[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Folium Maps](https://img.shields.io/badge/Leaflet-folium-green?style=flat&logo=leaflet&logoColor=white)](https://github.com/python-visualization/folium)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](https://opensource.org/licenses/MIT)
[![Streamlit Cloud Deployment](https://img.shields.io/badge/Streamlit%20Cloud-Deployed-success?style=flat&logo=streamlit)](https://my-learning-journey-cusqcaxngwy92twlrrtpfw.streamlit.app)

</div>

---

## 🚀 Live Demo

### 🌐 Streamlit Cloud

👉 **[Open Streamlit App](https://my-learning-journey-cusqcaxngwy92twlrrtpfw.streamlit.app)**

---

### 📂 GitHub Repository

👉 **[GitHub Repository](https://github.com/robinrobinlin-bit/HW11)**

---

## 📖 Project Overview

This repository hosts a production-grade, end-to-end meteorological data intelligence platform. The portal automatically ingests hourly weather station readings and weekly sea forecast updates directly from Taiwan's **Central Weather Administration (CWA)** Open Data REST APIs, persists records in a transaction-safe SQLite database, fits parallel **RandomForest** and **XGBoost** regressor models in memory, and exposes a high-fidelity data explorer alongside interactive analytics dashboards.

Optimized with dual-level caching (`@st.cache_data` for API payloads, `@st.cache_resource` for deserialized regressor models), this portal achieves sub-10ms query times on warm runs, making it an excellent showcase portfolio piece for recruiters and academic instructors.

---
