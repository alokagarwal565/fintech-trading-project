# AI-Powered Risk & Scenario Advisor for Retail Investors

A comprehensive Streamlit web application that helps retail investors understand their risk tolerance, analyze their portfolios, and get AI-powered insights on market scenarios using Google Gemini and yFinance APIs.

## 🚀 Features

### 🎯 Risk Profiling
- Interactive 6-question questionnaire to assess investment risk tolerance
- Classification into Conservative, Moderate, or Aggressive investor profiles
- Personalized recommendations based on risk assessment

### 💼 Portfolio Analysis
- Natural language portfolio input (e.g., "TCS: 10, HDFC Bank: 5 shares")
- Real-time stock price fetching using yFinance
- Portfolio visualization with interactive charts
- Sector allocation and concentration analysis
- Indian stock market focus with comprehensive symbol mapping

### 🔮 AI-Powered Scenario Analysis
- Custom scenario analysis using Google Gemini AI
- Predefined market scenarios relevant to Indian markets
- Personalized insights based on portfolio composition and risk profile
- Actionable recommendations and risk assessments

### 📊 Data Visualization
- Portfolio composition pie charts
- Sector allocation bar charts
- Individual holdings value visualization
- Interactive Plotly charts

### 📋 Export Capabilities
- Export analysis results as text files
- Generate comprehensive PDF reports
- Download reports with complete analysis history

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.10+
- **AI Integration**: Google Gemini API via google-genai
- **Market Data**: yFinance
- **Visualization**: Plotly
- **Environment Management**: python-dotenv
- **PDF Generation**: ReportLab

## 📦 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Google Gemini API key

### Environment Setup

1. **Clone or create the project structure**:
```bash
mkdir risk-scenario-advisor
cd risk-scenario-advisor
