# 🔍 Google Query Fan-Out Extractor

> **Free AI-Powered SEO Tool** — Discover hidden sub-queries that Google AI Overviews secretly run behind the scenes. Target these to rank in Google AIO & AI Mode.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## 🚀 What Is This?

When you search on Google, the AI Overview doesn't just answer your query directly — it secretly runs multiple **"fan-out" sub-queries** behind the scenes to gather comprehensive information. This tool extracts those hidden queries so you can:

- 🎯 **Target sub-queries** to appear in Google AI Overviews
- 📈 **Improve rankings** in Google's AI Mode
- 🔑 **Discover long-tail keywords** you'd never think of
- 🧠 **Understand Google's intent mapping** for any topic

## ✨ Features

- **Dual-Mode Extraction** — Google Search Grounding (real queries) with automatic AI Prediction fallback
- **Premium Dark UI** — Glassmorphism design with smooth animations
- **Multiple Models** — Choose from gemini-3.7-flash, gemini-3.5-flash-lite, gemini-2.5-flash, gemini-2.5-pro
- **CSV Export** — Download results as a structured CSV report
- **Secure** — API key never leaves your browser session
- **100% Free** — Deploy on Streamlit Community Cloud at zero cost

---

## 🛠️ Local Setup

### Prerequisites

- Python 3.9+
- A free [Google Gemini API Key](https://aistudio.google.com/apikey)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/amir-query-fanout-extractor.git
cd amir-query-fanout-extractor

# 2. Create virtual environment
python3 -m venv .venv

# 3. Install dependencies
.venv/bin/pip install -r requirements.txt

# 4. Run the app
.venv/bin/streamlit run app.py
```

Open `http://localhost:8501` in your browser, paste your API key in the sidebar, and start extracting!

---

## ☁️ Free Deployment on Streamlit Community Cloud

### Step 1: Push to GitHub

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit: Query Fan-Out Extractor"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/amir-query-fanout-extractor.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository: `amir-query-fanout-extractor`
5. Set **Main file path** to: `app.py`
6. Click **"Deploy!"**

### Step 3: Done! 🎉

Your app will be live at:
```
https://YOUR_USERNAME-amir-query-fanout-extractor-app-XXXXX.streamlit.app
```

> **Note:** The API key is entered by each user in the sidebar — it's never stored or logged.

---

## 📁 Project Structure

```
amir-query-fanout-extractor/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## 🔒 Security

- API keys are input via `st.text_input(type="password")` — masked in the UI
- Keys are stored only in the Streamlit session state — never persisted
- No server-side logging of API keys or queries
- `.gitignore` excludes `.streamlit/secrets.toml` and `.env` files

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<p align="center">
  Built with ❤️ by <strong>Amir</strong> • Powered by Google Gemini
</p>
