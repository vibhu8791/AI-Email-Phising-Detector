# 🛡️ AI Phishing Email Detection System

An enterprise-grade, full-stack cybersecurity application that inspects and protects against phishing attacks in real time. Features **Google OAuth 2.0** for seamless and secure Gmail mailbox ingestion, an **AI/ML detection engine** built with **Scikit-Learn (TF-IDF Vectorizer + Logistic Regression)** combined with advanced heuristic threat signals, a high-performance asynchronous **FastAPI** backend with **WebSockets**, **MongoDB** persistence, and a modern reactive **React** dashboard with high-priority threat alerts.

---

## 🌟 Key Features

- 🔐 **Zero-Password Gmail Connection**: Authenticate securely using Google OAuth 2.0 (`gmail.readonly` scope). No email passwords are ever requested, exposed, or stored.
- 📥 **Automated Gmail Ingestion**: Uses the official Gmail REST API to automatically fetch emails, parse MIME structures, and extract raw text, HTML, and embedded hyperlinks without copy-pasting.
- 🧠 **AI/ML Phishing Detection Model**:
  - **Scikit-Learn** pipeline with **TF-IDF Vectorizer** (n-grams 1-2, sublinear term frequency, English stopword filtration) and **Logistic Regression** trained on extensive phishing campaigns and legitimate emails.
  - Predicts linguistic phishing probability and identifies deceptive language patterns.
- 🔍 **Deep Rule-Based Heuristic Analysis**:
  - **URL Inspector**: Flags IP-based addresses, suspicious TLDs (`.xyz`, `.top`, `.buzz`, `.cc`, etc.), URL shortening services, and brand lookalikes.
  - **Sender Spoofing Guard**: Detects sender domain mismatches, typosquatting (e.g. `paypa1-support.com`, `m1crosoft.com`), and free webmail impersonation.
  - **Urgency & Credential Harvesting Engine**: Detects time-pressure tactics, account lockout warnings, and wire transfer lures.
- 📊 **Calibrated Phishing Risk Score (0 – 100)**:
  - Multi-tier classification:
    - `SAFE`: Risk Score `0 - 35`
    - `SUSPICIOUS`: Risk Score `36 - 69`
    - `PHISHING`: Risk Score `70 - 100`
- ⚡ **Real-Time WebSockets**: Instant push notifications to connected dashboards whenever a dangerous email is identified.
- 🚨 **High-Priority Threat Alerting**: Pulsating warning banners, audible notification chimes, and instant inspection modals.
- 🧪 **Interactive AI Sandbox Scanner**: Built-in testbed to paste custom email text or load quick attack presets to test the ML model live.
- 💾 **Dual-Mode Persistence**: Native support for **MongoDB** (via `motor`) with automatic graceful fallback to a local resilient datastore if MongoDB is not running.

---

## 📁 Project Structure

```
Ai Phising Email/
├── backend/                     # FastAPI Backend Server
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py          # Google OAuth 2.0 flow & demo mailbox
│   │   │   ├── emails.py        # Fetch, scan, inspect, sync, & simulate
│   │   │   ├── dashboard.py     # Metrics telemetry & stats
│   │   │   └── websocket.py     # Real-time WebSocket connection manager
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic Settings & environment variables
│   │   │   └── security.py      # Token encryption (Fernet / AES) at rest
│   │   ├── services/
│   │   │   ├── analyzer.py      # Hybrid ML + Heuristic scoring engine
│   │   │   ├── gmail_service.py # Gmail API ingestion & MIME decoding
│   │   │   └── heuristic.py     # URL, sender, and keyword rule extractors
│   │   └── main.py              # FastAPI app setup, CORS, & lifespan
│   ├── requirements.txt         # Python dependencies
│   ├── run.py                   # Server startup script
│   ├── .env                     # Local environment settings
│   └── .env.example
├── ml_model/                    # AI/ML Machine Learning Pipeline
│   ├── dataset/
│   │   └── phishing_dataset.csv # Curated dataset of phishing & safe emails
│   ├── feature_extractor.py     # Heuristic feature extraction routines
│   ├── train_model.py           # Model training & joblib exporter
│   └── saved_models/            # Trained TF-IDF & Logistic Regression models
│       ├── tfidf_vectorizer.joblib
│       └── phishing_model.joblib
├── database/                    # Persistence Layer
│   ├── __init__.py
│   ├── connection.py            # MongoDB Motor client + fallback store
│   └── models.py                # Pydantic and database schemas
├── frontend/                    # Modern React Dashboard (Vite + Tailwind)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx           # Top navigation with Gmail status & sync
│   │   │   ├── StatsOverview.jsx    # Metric cards & fleet threat bar
│   │   │   ├── ThreatBanner.jsx     # High-priority alert banner
│   │   │   ├── PhishingAlertModal.jsx # Instant threat popup with sound
│   │   │   ├── LiveThreatFeed.jsx   # Real-time WebSocket threat stream
│   │   │   ├── EmailList.jsx        # Scan history table with filters & search
│   │   │   ├── EmailDetailModal.jsx # In-depth email & link safety inspector
│   │   │   └── SandboxScanner.jsx   # Interactive custom email tester
│   │   ├── services/
│   │   │   ├── api.js               # Axios HTTP client
│   │   │   └── websocket.js         # WebSocket subscriber & auto-reconnect
│   │   ├── App.jsx                  # Main dashboard layout
│   │   ├── main.jsx                 # React root
│   │   └── index.css                # Tailwind CSS styling
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.10 - 3.14)
- **Node.js 18+** & **npm**
- *(Optional)* **MongoDB** (Local daemon or MongoDB Atlas free cloud cluster; the system includes an automatic resilient local fallback if MongoDB is not running).

---

### Step 1: Install Backend Dependencies & Train ML Model

1. Open a terminal in the project root:
   ```bash
   cd "d:/project/Ai Phising Email"
   ```

2. *(Recommended)* Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Train and export the Scikit-learn Phishing Detection Model:
   ```bash
   python ml_model/train_model.py
   ```
   *This trains the TF-IDF Vectorizer and Logistic Regression model on the dataset and exports them to `ml_model/saved_models/`.*

5. Launch the FastAPI backend server:
   ```bash
   python backend/run.py
   ```
   The backend will be live at **`http://127.0.0.1:8000`**.
   - Interactive API Swagger Docs: `http://127.0.0.1:8000/docs`
   - Real-time WebSocket: `ws://127.0.0.1:8000/ws/alerts`

---

### Step 2: Install Frontend Dependencies & Start Dashboard

1. Open a second terminal window:
   ```bash
   cd "d:/project/Ai Phising Email/frontend"
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5173
   ```

---

## 🔑 Google Cloud Platform (OAuth 2.0) Setup

To connect live Gmail mailboxes:

1. Visit the **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Create a new project (e.g. `AI Phishing Shield`).
3. Navigate to **APIs & Services > Library** and search for **Gmail API**. Click **Enable**.
4. Configure the **OAuth Consent Screen**:
   - User Type: **External** (or Internal if using Google Workspace).
   - App Name: `AI Phishing Detector`.
   - Scopes: Add `https://www.googleapis.com/auth/gmail.readonly` and `.../auth/userinfo.email`.
   - Test Users: Add your personal Gmail account while the app is in testing mode.
5. Create Credentials:
   - Navigate to **APIs & Services > Credentials**.
   - Click **Create Credentials > OAuth client ID**.
   - Application type: **Web application**.
   - Name: `Phishing Detector Web Client`.
   - **Authorized redirect URIs**:
     ```
     http://localhost:8000/api/auth/google/callback
     ```
   - Click **Create** and copy your **Client ID** and **Client Secret**.
6. Paste your credentials into `backend/.env`:
   ```env
   GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   ```
7. Restart the backend server. You can now click **"Connect Gmail"** in the top navbar to authenticate securely!

> [!TIP]
> **Instant Testing Without Google Cloud:**
> If you have not created Google Cloud credentials yet, click **"Connect Instant Demo Mailbox"** or **"Simulate Attack"** in the dashboard. The system will immediately ingest realistic simulated emails across all risk tiers to demonstrate real-time alerts, risk scoring, and table metrics.

---

## 🧪 Testing the AI Model Interactively

1. In the top navbar, click the **"AI Sandbox Scanner"** tab.
2. Select any quick preset (e.g., *PayPal Account Locked*, *CEO Urgent Wire Transfer*, or *Google Cloud Invoice*).
3. Click **"Analyze with AI"**.
4. Observe the live detection telemetry:
   - Calibrated Risk Score (`0-100`)
   - Scikit-Learn Logistic Regression linguistic probability
   - Extracted URL security verdicts (raw IP address checks, suspicious TLDs)
   - Triggered security rules and urgency flags

---

## 🛡️ Phishing Classification Thresholds

| Classification | Risk Score | Recommended Action | Typical Indicators |
| :--- | :---: | :--- | :--- |
| **SAFE** | 0 – 35 | Normal delivery | Verified domains, standard business or newsletter language, benign HTTPS links. |
| **SUSPICIOUS** | 36 – 69 | Caution advised | External survey links, minor urgency phrases, generic sender addresses. |
| **PHISHING** | 70 – 100 | **Quarantine / High Alert** | Raw IP addresses in URLs, lookalike sender domains, account suspension threats, wire transfer requests. |

---

## 📄 License
This project is open-source and available under the MIT License.
