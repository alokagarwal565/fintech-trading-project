# 🚀 AI-Powered Risk & Scenario Advisor

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

> **Professional-grade investment risk assessment and scenario analysis platform powered by AI**

## 📖 Overview

The **AI-Powered Risk & Scenario Advisor** is a comprehensive financial technology application designed for retail investors. It combines advanced AI analysis with traditional financial modeling to provide personalized investment insights, risk assessments, and market scenario analysis.

### 🎯 **What It Does**

- **🔒 Risk Profiling**: Comprehensive risk assessment questionnaires with AI-powered analysis
- **📊 Portfolio Analysis**: Real-time portfolio evaluation with sector diversification insights
- **🤖 AI Scenario Analysis**: Market scenario impact analysis using Google Gemini AI
- **📈 Dynamic Visualizations**: Interactive charts and graphs for portfolio insights
- **📋 Export Capabilities**: Generate detailed reports in PDF and text formats
- **👥 User Management**: Secure authentication with role-based access control
- **📊 Admin Dashboard**: Comprehensive system monitoring and user management

### 🚀 **Key Features**

- **AI-Powered Analysis**: Leverages Google Gemini AI for intelligent financial insights
- **Real-time Data**: Live stock data integration via Yahoo Finance API
- **Responsive UI**: Modern, intuitive interface built with Streamlit
- **Secure Backend**: FastAPI-based REST API with JWT authentication
- **Database Persistence**: SQLite database with SQLModel ORM
- **Rate Limiting**: Redis-based API protection and caching
- **Comprehensive Testing**: 100% test coverage with automated test suite

## 🏗️ Architecture & Tech Stack

### **Backend (FastAPI)**
- **Framework**: FastAPI 0.104+
- **Database**: SQLite with SQLModel ORM
- **Authentication**: JWT with bcrypt password hashing
- **AI Integration**: Google Gemini AI API
- **Caching**: Redis for rate limiting and performance
- **Security**: CORS, rate limiting, input validation

### **Frontend (Streamlit)**
- **Framework**: Streamlit 1.28+
- **Charts**: Plotly for interactive visualizations
- **Data Processing**: Pandas for financial data manipulation
- **Real-time Data**: Yahoo Finance integration via yfinance

### **Infrastructure**
- **Database**: SQLite with automatic migrations
- **File Storage**: Local file system with export management
- **Logging**: Structured logging with configurable levels
- **Environment**: Python 3.10+ with virtual environment

## 🛠️ Installation & Setup

### **Prerequisites**

- **Python**: 3.10 or higher
- **Git**: For cloning the repository
- **Redis**: Optional (for enhanced rate limiting)

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/alokagarwal565/fintech-trading-project.git
cd fintech-trading-project
```

### **Step 2: Environment Setup**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 3: Configuration**

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# Required: GEMINI_API_KEY, SECRET_KEY
# Optional: REDIS_URL, CORS_ORIGINS, etc.
```

#### **Required Environment Variables**

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini AI API key | `AIzaSyC...` |
| `SECRET_KEY` | JWT secret key | `your-super-secret-key` |
| `API_BASE_URL` | Backend API URL | `http://localhost:8000` |

#### **Optional Environment Variables**

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:8501` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG_MODE` | Debug mode flag | `true` |

### **Step 4: Database Initialization**

```bash
# Run setup script (automatically creates database and admin user)
python setup.py

# Or manually initialize database
python -c "from backend.models.database import create_db_and_tables; create_db_and_tables()"
```

## 🚀 Running the Application

### **Option 1: Automated Startup (Recommended)**

```bash
# Start both backend and frontend automatically
python start_services.py
```

### **Option 2: Manual Startup**

#### **Start Backend Server**

```bash
# Terminal 1: Activate venv and start backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python run_backend.py
```

Backend will be available at: **http://localhost:8000**

#### **Start Frontend Application**

```bash
# Terminal 2: Activate venv and start frontend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python run_frontend.py
```

Frontend will be available at: **http://localhost:8501**

### **Option 3: Individual Scripts**

```bash
# Backend only
python run_backend.py

# Frontend only  
python run_frontend.py
```

## 🧪 Testing

### **Run Complete Test Suite**

```bash
# Run all tests (requires backend running)
python test_all.py
```

### **Run Specific Test Categories**

```bash
# Environment and dependencies (always available)
python test_all.py environment
python test_all.py dependencies
python test_all.py database

# Core features (requires backend running)
python test_all.py auth
python test_all.py risk
python test_all.py portfolio
python test_all.py scenario
python test_all.py export
```

### **Test Coverage**

- ✅ **Environment Configuration**: Python version, dependencies, environment variables
- ✅ **Database Operations**: Connection, models, CRUD operations
- ✅ **API Endpoints**: Authentication, CRUD operations, error handling
- ✅ **Business Logic**: Risk assessment, portfolio analysis, scenario analysis
- ✅ **Integration**: End-to-end user workflows

**Current Status**: 100% test success rate with comprehensive coverage

## 📚 Usage Examples

### **1. User Registration & Authentication**

```python
# Register new user
POST /auth/register
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
}

# Login
POST /auth/token
{
    "username": "user@example.com",
    "password": "SecurePass123!"
}
```

### **2. Risk Assessment**

```python
# Create risk profile
POST /api/v1/risk-profile
{
    "answers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}

# Get latest assessment
GET /api/v1/risk-profile/latest
```

### **3. Portfolio Analysis**

```python
# Analyze portfolio
POST /api/v1/analyze-portfolio
{
    "portfolio_input": "AAPL:100,GOOGL:50,MSFT:75"
}

# Get portfolio data
GET /api/v1/portfolio/latest
```

### **4. Scenario Analysis**

```python
# Analyze market scenario
POST /api/v1/analyze-scenario
{
    "scenario_text": "Federal Reserve increases interest rates by 0.5%",
    "portfolio_id": 1
}

# Get all scenarios
GET /api/v1/scenarios
```

### **5. Export Reports**

```python
# Export as PDF
POST /api/v1/export/pdf
{
    "include_risk_profile": true,
    "include_portfolio": true,
    "include_scenarios": true
}

# Download export
GET /api/v1/export/download/{export_id}
```

## 📁 Project Structure

```
fintech-trading-project/
├── 📁 app/                          # Streamlit frontend application
│   └── 📄 main.py                  # Main frontend application (3,174 lines)
├── 📁 backend/                      # FastAPI backend application
│   ├── 📄 main.py                  # FastAPI app entry point
│   ├── 📁 models/                  # Database models and schemas
│   │   ├── 📄 models.py            # SQLModel data models
│   │   └── 📄 database.py          # Database configuration
│   ├── 📁 routers/                 # API route handlers
│   │   ├── 📄 auth.py              # Authentication endpoints
│   │   ├── 📄 admin.py             # Admin management endpoints
│   │   ├── 📄 export.py            # Export functionality
│   │   ├── 📄 portfolio.py         # Portfolio management
│   │   ├── 📄 risk_profile.py      # Risk assessment
│   │   ├── 📄 scenario.py          # Scenario analysis
│   │   └── 📄 user_data.py         # User data aggregation
│   ├── 📁 services/                # Business logic services
│   │   ├── 📄 export_service.py    # Export generation
│   │   ├── 📄 portfolio_service.py # Portfolio analysis
│   │   ├── 📄 risk_profile_service.py # Risk assessment logic
│   │   └── 📄 scenario_service.py  # AI scenario analysis
│   ├── 📁 middleware/              # Security and logging middleware
│   ├── 📁 utils/                   # Utility functions
│   └── 📁 auth/                    # Authentication modules
├── 📁 exports/                     # Generated export files
├── 📁 logs/                        # Application logs
├── 📁 temp/                        # Temporary files
├── 📁 venv/                        # Python virtual environment
├── 📄 .env.example                 # Environment variables template
├── 📄 requirements.txt             # Python dependencies
├── 📄 setup.py                     # Automated setup script
├── 📄 start_services.py            # Service startup automation
├── 📄 run_backend.py               # Backend startup script
├── 📄 run_frontend.py              # Frontend startup script
├── 📄 test_all.py                  # Comprehensive test suite
├── 📄 investment_advisor.db        # SQLite database
└── 📄 README.md                    # This file
```

## 🔧 Configuration

### **Database Configuration**

The application uses SQLite by default with automatic table creation:

```python
# Database URL (configurable via environment)
DATABASE_URL = "sqlite:///./investment_advisor.db"

# Automatic table creation on startup
create_db_and_tables()
```

### **Security Configuration**

```python
# JWT Configuration
SECRET_KEY = "your-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS Configuration
CORS_ORIGINS = ["http://localhost:8501", "http://localhost:3000"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000
```

### **AI Configuration**

```python
# Google Gemini AI
GEMINI_API_KEY = "your-gemini-api-key"

# AI Analysis Settings
MAX_RETRIES = 2
BASE_DELAY = 2.0
```

## 🚀 Deployment

### **Production Deployment**

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export DEBUG_MODE=false
   export ENABLE_HTTPS=true
   export LOG_LEVEL=WARNING
   ```

2. **Database Migration**
   ```bash
   # Backup existing database
   cp investment_advisor.db investment_advisor_backup.db
   
   # Run setup in production mode
   python setup.py --production
   ```

3. **Service Management**
   ```bash
   # Use systemd (Linux) or Windows Services
   # Configure reverse proxy (Nginx/Apache)
   # Enable SSL/TLS certificates
   ```

### **Docker Deployment**

```dockerfile
# Dockerfile example
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run_backend.py"]
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### **Development Setup**

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   python test_all.py
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### **Contribution Guidelines**

- **Code Style**: Follow PEP 8 Python style guide
- **Testing**: Ensure all tests pass before submitting
- **Documentation**: Update documentation for new features
- **Commits**: Use clear, descriptive commit messages
- **Issues**: Report bugs and suggest features via GitHub Issues

### **Development Workflow**

```bash
# 1. Setup development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Make changes and test
python test_all.py

# 3. Run specific tests during development
python test_all.py auth
python test_all.py portfolio

# 4. Check code quality
python -m flake8 backend/ app/
python -m black backend/ app/
```

## 📊 API Documentation

### **Interactive API Docs**

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Core Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | User registration |
| `POST` | `/auth/token` | User authentication |
| `POST` | `/api/v1/risk-profile` | Create risk assessment |
| `POST` | `/api/v1/analyze-portfolio` | Analyze portfolio |
| `POST` | `/api/v1/analyze-scenario` | Analyze market scenario |
| `POST` | `/api/v1/export/pdf` | Export report as PDF |
| `GET` | `/api/v1/user/data` | Get all user data |
| `GET` | `/api/v1/admin/users` | Admin: List all users |

## 🐛 Troubleshooting

### **Common Issues**

#### **Backend Won't Start**
```bash
# Check if port 8000 is available
netstat -an | grep 8000

# Check environment variables
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

#### **Frontend Connection Issues**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration in .env
CORS_ORIGINS=http://localhost:8501
```

#### **Database Issues**
```bash
# Reset database (WARNING: Data loss)
python reset_database.py

# Check database schema
python -c "from backend.models.database import create_db_and_tables; create_db_and_tables()"
```

#### **AI Analysis Failing**
```bash
# Verify Gemini API key
echo $GEMINI_API_KEY

# Check API quota and limits
# Visit: https://makersuite.google.com/app/apikey
```

### **Logs and Debugging**

```bash
# Check application logs
tail -f app.log

# Enable debug mode
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG

# Check specific service logs
tail -f logs/backend.log
tail -f logs/frontend.log
```

## 🆘 Support

### **Getting Help**

1. **📚 Documentation**: Check this README and inline code comments
2. **🐛 Issues**: Report bugs via [GitHub Issues](https://github.com/alokagarwal565/fintech-trading-project/issues)
3. **💬 Discussions**: Start discussions for questions and ideas
4. **📖 API Docs**: Interactive API documentation at http://localhost:8000/docs
5. **🧪 Testing**: Run `python test_all.py` to verify system health

### **Community Resources**

- **GitHub Repository**: [https://github.com/alokagarwal565/fintech-trading-project](https://github.com/alokagarwal565/fintech-trading-project)
- **FastAPI Documentation**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Streamlit Documentation**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **Google Gemini AI**: [https://ai.google.dev/](https://ai.google.dev/)

## 🎉 Acknowledgments

- **FastAPI**: Modern, fast web framework for building APIs
- **Streamlit**: Rapid web app development for data science
- **Google Gemini AI**: Advanced AI capabilities for financial analysis
- **SQLModel**: Modern Python library for working with databases
- **Yahoo Finance**: Real-time financial data via yfinance library

---

**⭐ Star this repository if you find it helpful!**

**🤝 Contributions are welcome and appreciated!**

**📧 Questions? Open an issue or start a discussion!**

---

*Built with ❤️ for the fintech community*