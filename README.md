# ShopAI - Hyper-Intelligence Shopping Assistant

**ShopAI** is a "Next Level" multimodal e-commerce platform powered by **Gemini 1.5 Pro**. It transcends traditional shopping by integrating expert-level AI roles—from Wall Street analysts to Environmental Auditors—into a single, hyper-premium interface.

![UI](https://img.shields.io/badge/UI-Hyper--Premium-8A2BE2)
![AI](https://img.shields.io/badge/AI-Gemini%201.5%20Pro-4285F4)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

## 🚀 Key Features

### 1. Visual & Semantic Search

- **Visual Search:** Upload any image to find visually similar products using vector embeddings.
- **Smart Text Search:** Search using natural language (e.g., "shoes for a wedding in winter").

### 2. "Deep Seek" Video Diagnostics

- **Problem:** Have a broken appliance?
- **Solution:** Upload a video of the malfunction.
- **AI Protocol:** The **"Deep Seek" Engine** (Chain-of-Thought) scans the video frame-by-frame, analyzes audio patterns, and generates a professional repair plan with confidence scores.

### 3. Market Analyst AI

- **Real-Time Forecasting:** The built-in **Senior Market Analyst** predicts price trends based on seasonality, product lifecycle, and upcoming sales events.
- **Verdict:** Tells you decisively to "BUY NOW" or "WAIT".

### 4. Eco-Auditor Engine

- **Greenwashing Detection:** Visual analysis of packaging vs. marketing claims.
- **Cradle-to-Grave:** Estimates carbon footprint and water usage.
- **Score:** Gives a strict 0-100 Sustainability Rating.

### 5. Admin & Comparisons

- **Auto-Cataloging:** Upload a raw product image, and the **Catalog Specialist** writes SEO-optimized copy instantly.
- **Decisive Comparisons:** The **Consumer Research Expert** declares a "Winner" and "Runner-up" for any product comparison.

---

## 🛠️ Architecture

ShopAI runs on a split-stack architecture to ensure maximum performance and separation of concerns.

| Component     | Tech Stack            | Role                                               |
| :------------ | :-------------------- | :------------------------------------------------- |
| **Frontend**  | Streamlit, Custom CSS | "Hyper-Premium" Glassmorphic UI, User Interactions |
| **Backend**   | FastAPI, Uvicorn      | AI Orchestration, Vector DB (Chroma), RAG Logic    |
| **AI Driver** | Google Gemini 1.5 Pro | The "Brain" behind every service                   |
| **Vector DB** | ChromaDB              | Semantic Indexing for Products & Manuals           |

---

## 💻 Installation

### Prerequisites

- Python 3.10+
- Google Cloud API Key (Gemini)

### 1. Clone & Install

```bash
git clone https://github.com/jayesh3103/ShopAI.git
cd ShopAI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```ini
GOOGLE_API_KEY=your_gemini_api_key
# Optional:
SERPAPI_KEY=your_serpapi_key # For live Google Shopping results
```

### 3. Ingest Data (First Run Only)

Populate the local Vector Database with sample data:

```bash
python3 scripts/download_data.py  # Download datasets
python3 scripts/process_data.py   # Normalize data
python3 scripts/ingest_root.py    # Generate embeddings
```

---

## 🏃‍♂️ Usage

### Start the System (Local)

**Terminal 1: Start Backend (The Brain)**

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

_Backend runs at: `http://127.0.0.1:8000`_

**Terminal 2: Start Frontend (The Face)**

```bash
streamlit run frontend/app.py
```

_Frontend runs at: `http://localhost:8501`_

---

## ☁️ Deployment Guide

Since ShopAI uses a split architecture, you should deploy the Backend and Frontend separately for stability.

### Part A: Deploy Backend (Render)

1.  **Repo:** Push this code to GitHub.
2.  **Platform:** Create a new Web Service on [Render](https://render.com).
3.  **Build Command:** `pip install -r requirements.txt`
4.  **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5.  **Env:** Add your `GOOGLE_API_KEY` in the platform's Environment Variables.
6.  **URL:** Save your deployed URL (e.g., `https://shopai-backend.onrender.com`).

### Part B: Deploy Frontend (Streamlit Cloud)

1.  **Platform:** Go to [Streamlit Community Cloud](https://streamlit.io/cloud).
2.  **App:** Connect your GitHub repo and select `frontend/app.py` as the entry point.
3.  **Secrets:** In the App Settings > Secrets, add:
    ```toml
    [general]
    BACKEND_URL = "https://shopai-backend.onrender.com"
    ```
    _(Note: You will need to update `frontend/app.py` to read this secret instead of `localhost` if deploying remotely.)_

---

## 🤝 Contributing

Contributions to improve the "Deep Seek" protocol or UI animations are welcome!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

_Built with ❤️ by the Jayesh Muley_
