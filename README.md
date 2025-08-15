# AI-Powered Risk & Scenario Advisor for Retail Investors

A comprehensive full-stack application that helps retail investors assess their risk tolerance, analyze portfolios, and run AI-driven scenario planning using Google Gemini AI.

## 🚀 New Features - Data Persistence

**All user actions and results are now automatically saved and restored when users log back in!**

### ✅ What's New

- **Persistent User Sessions**: All user data is automatically saved to the database
- **Automatic Data Restoration**: When users log in, their previous work is immediately displayed
- **Data Management**: Users can update, replace, or delete their saved data
- **Export History**: Track and re-download all previous exports

### 🎯 User Experience Improvements

1. **Risk Profiling**
   - Previous risk assessments are displayed immediately on login
   - "Retake Assessment" button to replace old results
   - Shows assessment date and complete results

2. **Portfolio Analysis**
   - Saved portfolio data is restored on login
   - "Re-analyze Portfolio" option to update holdings
   - Displays last updated date and current holdings

3. **Scenario Analysis**
   - All previous scenario analyses are listed
   - Individual scenario management (view, delete)
   - Summary table of all analyses with risk levels

4. **Export Management**
   - Complete export history with metadata
   - Re-download any previous export
   - Delete old exports as needed

## 🏗️ Architecture

- **Frontend**: Streamlit (Port 8501)
- **Backend**: FastAPI (Port 8000)
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI Integration**: Google Gemini API
- **Stock Data**: yfinance API
- **Authentication**: JWT tokens
- **Security**: Rate limiting, input sanitization, CORS

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLModel**: SQL database toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Token authentication
- **Redis**: Rate limiting and caching
- **ReportLab**: PDF generation
- **yfinance**: Real-time stock data
- **Google Gemini**: AI-powered scenario analysis

### Frontend
- **Streamlit**: Interactive web application
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **httpx**: HTTP client for API communication

### Security & Performance
- **Rate Limiting**: Redis-based API rate limiting
- **Input Sanitization**: Protection against XSS and injection attacks
- **Security Headers**: Comprehensive security middleware
- **Retry Logic**: Exponential backoff for external API calls
- **Logging**: Comprehensive application and security logging

## 📋 Features

### 1. Risk Assessment
- 6-question interactive questionnaire
- Calculates risk score (0-24) and category (Conservative/Moderate/Aggressive)
- Provides personalized investment recommendations
- **NEW**: Results are saved and restored on login

### 2. Portfolio Analysis
- Natural language portfolio input (e.g., "TCS: 10, HDFC Bank: 5 shares")
- Real-time stock data fetching via yfinance
- Portfolio metrics calculation (P/E ratio, dividend yield, concentration)
- Interactive visualizations (pie charts, bar charts)
- **NEW**: Portfolio data persists across sessions

### 3. AI-Powered Scenario Analysis
- Integration with Google Gemini AI
- Predefined and custom market scenarios
- Impact analysis on portfolio performance
- Actionable recommendations and risk assessment
- **NEW**: All scenarios are saved and manageable

### 4. Data Export
- Export analysis results in Text and PDF formats
- Customizable export options (include/exclude sections)
- Professional report generation
- **NEW**: Export history tracking and re-download capability

### 5. User Management
- Secure user registration and authentication
- JWT-based session management
- **NEW**: Complete data persistence and restoration

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Redis server (for rate limiting)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fintech-trading-project
   ```

2. **Run the automated setup**
   ```bash
   python setup.py
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Start the backend server**
   ```bash
   python run_backend.py
   ```

5. **Start the frontend application**
   ```bash
   python run_frontend.py
   ```

6. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./investment_advisor.db

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CORS
CORS_ORIGINS=http://localhost:8501,http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

## 📊 Database Schema

### Core Models
- **User**: User accounts and authentication
- **RiskAssessment**: Risk profile results and questionnaire answers
- **Portfolio**: User portfolios with total values
- **Holding**: Individual stock holdings with real-time data
- **Scenario**: AI-generated scenario analyses
- **Export**: Export history and file metadata

### Key Features
- **Foreign Key Relationships**: All user data is properly linked
- **Timestamps**: Created/updated timestamps for all records
- **JSON Storage**: Complex data stored as JSON strings
- **Cascade Deletes**: Proper cleanup when deleting parent records

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/token` - User login

### Risk Profiling
- `POST /api/v1/risk-profile` - Create risk assessment
- `GET /api/v1/risk-profile/latest` - Get latest assessment
- `DELETE /api/v1/risk-profile/latest` - Delete latest assessment

### Portfolio Analysis
- `POST /api/v1/analyze-portfolio` - Analyze portfolio
- `GET /api/v1/portfolio/latest` - Get latest portfolio
- `DELETE /api/v1/portfolio/latest` - Delete latest portfolio

### Scenario Analysis
- `POST /api/v1/analyze-scenario` - Create scenario analysis
- `GET /api/v1/scenarios` - Get all scenarios
- `GET /api/v1/scenarios/{id}` - Get specific scenario
- `DELETE /api/v1/scenarios/{id}` - Delete specific scenario

### Export Management
- `POST /api/v1/export/text` - Export as text
- `POST /api/v1/export/pdf` - Export as PDF
- `GET /api/v1/export/history` - Get export history
- `GET /api/v1/export/download/{id}` - Download export file
- `DELETE /api/v1/export/{id}` - Delete export

### User Data
- `GET /api/v1/user/data` - Get all user data

## 🧪 Testing

The application includes a comprehensive unified test suite that consolidates all testing functionality:

### Running Tests

**Run all tests:**
```bash
python test_all.py
```

**Run specific test categories:**
```bash
# Environment and dependencies
python test_all.py environment
python test_all.py dependencies
python test_all.py database

# Backend connectivity
python test_all.py health

# Authentication
python test_all.py auth

# Core features
python test_all.py risk
python test_all.py portfolio
python test_all.py visualizations
python test_all.py scenario
python test_all.py export
python test_all.py userdata
```

### Test Coverage

The unified test suite covers:

- **Environment Configuration**: API keys, environment variables
- **Dependencies**: All required Python packages
- **Database**: Connection, models, and schema
- **Backend Health**: API availability and responsiveness
- **Authentication**: User registration, login, and JWT tokens
- **Risk Assessment**: Questionnaire, scoring, and persistence
- **Portfolio Analysis**: Input parsing, data fetching, and visualizations
- **Scenario Analysis**: AI-powered scenario generation and storage
- **Export Functionality**: Text and PDF export with history
- **User Data**: Complete data aggregation and retrieval

### Test Results

The test suite provides detailed output with:
- ✅ Success indicators for each test
- ❌ Error messages with specific failure reasons
- 📊 Summary statistics (pass/fail counts, success rate)
- 🔍 Detailed debugging information

### Test Configuration

Tests use the following configuration:
- **Base URL**: `http://localhost:8000`
- **Test User**: `test@example.com` / `TestPass123!`
- **Existing User**: `alokagarwal629@gmail.com` / `TestPass123!`

**Note**: Make sure the backend server is running before executing tests that require API connectivity.

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt password hashing
- **Input Sanitization**: Protection against XSS and injection attacks
- **Rate Limiting**: Redis-based API rate limiting
- **Security Headers**: Comprehensive security middleware
- **CORS Protection**: Cross-origin resource sharing protection

## 📈 Performance Optimizations

- **Database Indexing**: Optimized queries with proper indexing
- **Caching**: Redis-based caching for frequently accessed data
- **Retry Logic**: Exponential backoff for external API calls
- **Async Operations**: Non-blocking API operations
- **Connection Pooling**: Efficient database connection management

## 🚀 Production Deployment

See `DEPLOYMENT.md` for detailed production deployment instructions including:
- Docker containerization
- Nginx reverse proxy setup
- SSL/TLS configuration
- Monitoring and logging
- Backup strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the documentation
2. Review the API docs at http://localhost:8000/docs
3. Run the test script to verify functionality
4. Check the logs for error details

---

**🎉 The application now provides a complete, persistent user experience where all work is automatically saved and restored!**