# AI-Powered Risk & Scenario Advisor for Retail Investors - Full Stack Edition

A comprehensive full-stack web application with FastAPI backend and Streamlit frontend that helps retail investors understand their risk tolerance, analyze their portfolios, and get AI-powered insights on market scenarios using Google Gemini and yFinance APIs.

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
- User authentication and secure data persistence
- RESTful API architecture
- JWT-based security

## 🛠️ Technology Stack

### Backend
- **API Framework**: FastAPI
- **Database**: SQLModel with SQLite
- **Authentication**: JWT with python-jose and passlib
- **API Documentation**: Automatic OpenAPI/Swagger docs

### Frontend
- **UI Framework**: Streamlit
- **HTTP Client**: httpx for API communication

### Shared
- **Runtime**: Python 3.10+
- **AI Integration**: Google Gemini API via google-genai
- **Market Data**: yFinance
- **Visualization**: Plotly
- **Environment Management**: python-dotenv
- **PDF Generation**: ReportLab

## 🏗️ Architecture

The application follows a modern full-stack architecture:

```
┌─────────────────┐    HTTP/REST API    ┌──────────────────┐
│                 │ ◄─────────────────► │                  │
│ Streamlit       │                     │ FastAPI          │
│ Frontend        │                     │ Backend          │
│ (Port 8501)     │                     │ (Port 8000)      │
└─────────────────┘                     └──────────────────┘
                                                │
                                                ▼
                                        ┌──────────────────┐
                                        │ SQLite Database  │
                                        │ (SQLModel/ORM)   │
                                        └──────────────────┘
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Google Gemini API key
- Redis (optional, for rate limiting)

### Quick Start

#### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script
python setup.py
```

#### Option 2: Manual Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
```bash
cp env.example .env
# Edit .env file with your API keys
```

3. **Start the backend server**:
```bash
python run_backend.py
# Backend will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

4. **Start the frontend** (in a new terminal):
```bash
python run_frontend.py
# Frontend will be available at http://localhost:8501
```

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
GEMINI_API_KEY=your-gemini-api-key-here
SECRET_KEY=your-super-secret-jwt-key

# Optional (with defaults)
API_BASE_URL=http://localhost:8000
DATABASE_URL=sqlite:///./investment_advisor.db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

## 🔐 Authentication

The application now includes user authentication:

1. **Register**: Create a new account with email and password
2. **Login**: Access your personalized dashboard
3. **Secure API**: All analysis endpoints require valid JWT tokens
4. **Data Persistence**: Your analysis history is saved and accessible across sessions

## 📚 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints:

- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get access token
- `POST /api/v1/risk-profile` - Assess risk tolerance
- `POST /api/v1/analyze-portfolio` - Analyze portfolio holdings
- `POST /api/v1/analyze-scenario` - AI-powered scenario analysis
- `POST /api/v1/export/text` - Export analysis as text
- `POST /api/v1/export/pdf` - Export analysis as PDF

## 🗄️ Database Schema

The application uses SQLModel for database operations with the following main entities:

- **Users**: User accounts and authentication
- **Portfolios**: User portfolio collections
- **Holdings**: Individual stock holdings
- **RiskAssessments**: Risk tolerance evaluations
- **Scenarios**: AI scenario analysis results

## 🚀 Development

### Running in Development Mode

Both servers support hot-reload for development:

```bash
# Terminal 1: Backend with auto-reload
python run_backend.py

# Terminal 2: Frontend with auto-reload
python run_frontend.py
```

### Project Structure

```
├── backend/                 # FastAPI backend
│   ├── auth/               # Authentication logic
│   ├── models/             # Database models
│   ├── routers/            # API route handlers
│   ├── services/           # Business logic services
│   └── main.py            # FastAPI application
├── app/                    # Streamlit frontend
│   └── main.py            # Streamlit application
├── requirements.txt        # Python dependencies
├── run_backend.py         # Backend startup script
├── run_frontend.py        # Frontend startup script
└── .env.example           # Environment variables template
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication with configurable expiration
- **Password Hashing**: Bcrypt password hashing with strength validation
- **Input Sanitization**: Protection against SQL injection, XSS, and path traversal
- **Rate Limiting**: Redis-based rate limiting with per-user and per-IP tracking
- **Security Headers**: Comprehensive security headers (XSS protection, content type options, etc.)
- **CORS Protection**: Configurable CORS for frontend-backend communication
- **Input Validation**: Pydantic models for request validation with custom validators
- **Audit Logging**: Comprehensive security event logging
- **Environment-based Configuration**: All secrets managed via environment variables

## 📊 Enhanced Features

### Compared to the original Streamlit-only version:

- ✅ **User Authentication**: Secure user accounts with JWT tokens
- ✅ **Data Persistence**: Analysis history saved to database
- ✅ **RESTful API**: Clean API architecture with OpenAPI documentation
- ✅ **Scalable Backend**: FastAPI for high performance with async support
- ✅ **Enhanced Security**: Comprehensive security features with audit logging
- ✅ **Rate Limiting**: Redis-based rate limiting for API protection
- ✅ **Error Handling**: Robust error handling with retry logic
- ✅ **Logging**: Comprehensive logging with rotation and monitoring
- ✅ **Input Validation**: Advanced input sanitization and validation
- ✅ **Performance**: Optimized API calls with caching and retry mechanisms
- ✅ **Better UX**: Improved loading indicators and error handling
- ✅ **Production Ready**: Docker support and deployment guides

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues:

1. **Backend not starting**: Check if port 8000 is available
2. **Frontend can't connect**: Ensure backend is running on port 8000
3. **Database errors**: Check file permissions for SQLite database
4. **API key errors**: Verify GEMINI_API_KEY in .env file
5. **Rate limiting errors**: Check Redis connection if using rate limiting
6. **Authentication errors**: Verify SECRET_KEY is set in .env file

### Getting Help:

- Check the API documentation at `http://localhost:8000/docs`
- Review the application logs in the `logs/` directory
- Check the health endpoint: `http://localhost:8000/health`
- Ensure all dependencies are installed correctly
- Run the setup script: `python setup.py`

### Production Deployment:

For production deployment, see the comprehensive [Deployment Guide](DEPLOYMENT.md) which includes:
- Docker containerization
- Nginx configuration
- SSL/TLS setup
- Monitoring and logging
- Security best practices