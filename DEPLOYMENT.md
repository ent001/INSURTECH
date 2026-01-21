# InsurTech Analyzer - Streamlit Deployment

## 🚀 Deployment Instructions

This app is designed to run on **Streamlit Cloud**.

### Required Secrets

Add this to your Streamlit Cloud **Secrets** (Settings → Secrets):

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

### Main File

- **Main file path:** `app_redesign.py`
- **Python version:** 3.9+

### Dependencies

All dependencies are listed in `requirements.txt` and will be installed automatically.

## 📝 Usage

1. Upload CSV or Excel file with company data
2. Map columns (Company Name, Description)
3. Enable AI Expert Mode (optional, uses OpenAI)
4. Click "START ANALYSIS"
5. View results in the interactive dashboard

## 🔐 Security

- Never commit `.env` file (already in `.gitignore`)
- Use Streamlit Secrets for API keys in production
- API key is loaded from environment variables or Streamlit secrets

## 📊 Features

- AI-powered classification using Sosa & Sosa 2025 Framework
- Real-time progress tracking
- Cost estimation and tracking
- Checkpoint system (auto-save every 5 companies)
- Interactive dashboard with multiple visualization tabs
- Export results to Excel
