# 🤖 Personal Hedge Fund (Autonomous AI Agent Team)

> An autonomous, self-improving trading system that costs $0 to run.

![Agent Architecture](https://img.shields.io/badge/Architecture-Decoupled%20Agents-blue)
![Cost](https://img.shields.io/badge/Cost-%240%2Fmonth-green)
![Status](https://img.shields.io/badge/Status-Active-success)

## 📖 Overview

This project implements a **Personal Hedge Fund** using a team of decoupled AI agents. The system runs entirely on **GitHub Actions** (serverless compute) and stores data in **Supabase** (PostgreSQL), ensuring it remains free to operate while respecting strict API rate limits.

The system features two distinct trading teams and a self-improvement loop:

### 1. 📈 The Stock Team (Paper Trading)
*   **Goal**: Long-term technical analysis on US Equities.
*   **The Scout**: Fetches OHLCV data ($0 cost via `yfinance`) and technical indicators (RSI, MACD via Alpha Vantage). *Engineered to sleep and batch requests to stay within 25 calls/day limits.*
*   **The Analyst**: Analyzes technical signals and generates Buy/Sell/Hold recommendations.
*   **The Portfolio Manager**: Simulates trades, manages a virtual cash ledger, and tracks portfolio performance.

### 2. ₿ The Crypto Team (Active Trading)
*   **Goal**: Experimental high-frequency Bitcoin trading based on alternative data.
*   **The Scout**: Fetches real-time Bitcoin pricing (Luno) and **Weather Data** (OpenWeatherMap) for Johannesburg.
*   **The Analyst**: Implements a "Weather Sentiment" strategy (e.g., "Good weather = Bullish").
*   **The Risk Manager**: Enforces position limits and checks account balances before authorizing trades.
*   **The Trader**: Executes orders on the Luno Exchange API.

### 3. 🧠 The Coach (Self-Improvement Loop)
*   **Goal**: Infinite continuous improvement.
*   **Trigger**: Runs weekly on Sundays.
*   **Function**: Analyzes past trade logs, calculates win rates, and **dynamically updates** the system's parameters (e.g., changing RSI thresholds or position sizes) in the database. The other agents read these new rules instantly.

### 4. 📊 The Dashboard
*   A **Streamlit** web app to visualize portfolio value, real-time crypto-weather correlations, and the Coach's decision logs.

---

## 🛠 Tech Stack

*   **Language**: Python 3.9
*   **Database**: Supabase (PostgreSQL)
*   **Compute/Scheduling**: GitHub Actions (Cron)
*   **Frontend**: Streamlit
*   **APIs**: yfinance, Alpha Vantage, Finnhub, Luno, OpenWeatherMap

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.9+
*   A Supabase Project (Free Tier)
*   API Keys (Alpha Vantage, Luno, OpenWeather)

### Local Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/StartYourWay/personal-hedge-fund.git
    cd personal-hedge-fund
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_anon_key
    ALPHA_VANTAGE_KEY=your_key
    FINNHUB_KEY=your_key
    LUNO_API_KEY_ID=your_id
    LUNO_API_KEY_SECRET=your_secret
    OPENWEATHER_API_KEY=your_key
    ```

4.  **Initialize Database**:
    Copy the SQL commands from `setup_schema.sql` and run them in your Supabase SQL Editor.

5.  **Run an Agent**:
    ```bash
    export PYTHONPATH=$PYTHONPATH:.
    python agents/stocks/scout.py
    ```

6.  **Launch Dashboard**:
    ```bash
    streamlit run dashboard.py
    ```

---

## ☁️ Deployment

### 1. Agents (GitHub Actions)
The system is pre-configured with workflows in `.github/workflows/`.
*   `stocks_daily.yml`: Runs daily at 23:00 UTC.
*   `crypto_hourly.yml`: Runs every hour.
*   `coach_weekly.yml`: Runs every Sunday at 00:00.

**To Activate**:
Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions** and add all the keys from your `.env` file as Repository Secrets.

### 2. Dashboard (Streamlit Cloud)
1.  Go to [Streamlit Community Cloud](https://streamlit.io/cloud).
2.  Connect your GitHub repository.
3.  Select `dashboard.py` as the entry point.
4.  In **Advanced Settings**, paste your `SUPABASE_URL` and `SUPABASE_KEY` into the Secrets section.

---

## 📂 Project Structure

```
├── agents/
│   ├── common/           # Shared utilities (DB, logging)
│   ├── stocks/           # Stock agent team (Scout, Analyst, PM)
│   ├── crypto/           # Crypto agent team (Scout, Analyst, Risk, Trader)
│   └── coach.py          # The Coach (Meta-agent)
├── .github/workflows/    # Automation schedules
├── dashboard.py          # Streamlit GUI
├── setup_db.py           # Database helper script
└── requirements.txt      # Dependencies
```

---

## ⚠️ Disclaimer
This is an experimental project for educational purposes. The "Weather Strategy" is a demonstration of alternative data correlation and should not be used for financial advice. **Trading crypto involves risk.**
