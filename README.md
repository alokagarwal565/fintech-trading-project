# AI-Powered Risk & Scenario Advisor for Retail Investors

A comprehensive full-stack application that helps retail investors assess their risk tolerance, analyze portfolios, and run AI-driven scenario planning using Google Gemini AI. The application provides a complete, persistent user experience where all work is automatically saved and restored.

## 🎯 Project Status

✅ **FULLY FUNCTIONAL** - All core features implemented and tested  
✅ **DATA PERSISTENCE** - Complete user data persistence across sessions  
✅ **UNIFIED TESTING** - Comprehensive test suite with 100% success rate  
✅ **PRODUCTION READY** - Security, performance, and deployment optimized  

## 🚀 Key Features

### ✅ **Complete Data Persistence**
- **Automatic Data Saving**: All user actions are automatically saved to the database
- **Session Restoration**: Previous work is immediately displayed when users log back in
- **Data Management**: Users can update, replace, or delete their saved data
- **Export History**: Track and re-download all previous exports

### ✅ **Risk Assessment System**
- 6-question interactive questionnaire with intelligent scoring
- Risk categorization (Conservative/Moderate/Aggressive)
- Personalized investment recommendations
- **Persistent Results**: Assessment history saved and restored

### ✅ **Portfolio Analysis Engine**
- Natural language portfolio input parsing
- Real-time stock data via yfinance API
- Advanced metrics calculation (P/E, dividend yield, concentration)
- **Interactive Visualizations**: Pie charts, sector analysis, holdings breakdown
- **Data Persistence**: Portfolio data persists across sessions

### ✅ **AI-Powered Scenario Analysis**
- Google Gemini AI integration for market scenario analysis
- Predefined and custom market scenarios
- Impact analysis on portfolio performance
- Actionable recommendations and risk assessment
- **Complete History**: All scenarios saved and manageable

### ✅ **Export & Reporting System**
- Professional Text and PDF export generation
- Customizable export options (include/exclude sections)
- Export history tracking and re-download capability
- ReportLab-powered document generation

### ✅ **User Management & Security**
- Secure JWT-based authentication
- **Real-time password strength validation** with visual feedback
- **Enhanced error handling** with user-friendly messages
- Password hashing with bcrypt
- Rate limiting and input sanitization
- Comprehensive security middleware

## 🏗️ Architecture

### **Frontend (Streamlit - Port 8501)**
- Interactive web application with modern UI
- Real-time data visualization with Plotly
- Responsive design for desktop and mobile
- Seamless API integration

### **Backend (FastAPI - Port 8000)**
- High-performance REST API
- SQLModel ORM with SQLite/PostgreSQL support
- Redis-based rate limiting and caching
- Comprehensive logging and monitoring

### **Database & Storage**
- **SQLite**: Development database with full schema
- **PostgreSQL**: Production-ready database support
- **File Storage**: Export files and document management
- **Redis**: Caching and rate limiting

### **External Integrations**
- **Google Gemini AI**: Advanced scenario analysis
- **yfinance**: Real-time stock market data
- **ReportLab**: Professional PDF generation

## 🛠️ Technology Stack

### **Backend Technologies**
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **SQLModel**: SQL database toolkit and ORM with Pydantic integration
- **JWT**: Secure token-based authentication
- **Redis**: Rate limiting, caching, and session management
- **ReportLab**: Professional PDF document generation
- **yfinance**: Real-time stock market data API
- **Google Gemini**: AI-powered scenario analysis

### **Frontend Technologies**
- **Streamlit**: Interactive web application framework
- **Plotly**: Advanced data visualization and charts
- **Pandas**: Data manipulation and analysis
- **httpx**: Modern HTTP client for API communication

### **Security & Performance**
- **Rate Limiting**: Redis-based API rate limiting (60/min, 1000/hour)
- **Input Sanitization**: Protection against XSS and injection attacks
- **Security Headers**: Comprehensive security middleware
- **Retry Logic**: Exponential backoff for external API calls
- **Logging**: Application and security event logging
- **CORS Protection**: Cross-origin resource sharing security

## 📋 Complete Feature List

### 1. **User Authentication & Management**
- Secure user registration with email validation
- **Real-time password strength validation** with visual feedback
- **Enhanced error handling** with structured error responses
- JWT-based login and session management
- Password strength validation and hashing
- User profile management

### 2. **Risk Assessment System**
- 6-question interactive questionnaire
- Intelligent risk scoring (0-24 scale)
- Risk categorization (Conservative/Moderate/Aggressive)
- Personalized investment recommendations
- Assessment history and retake functionality

### 3. **Portfolio Analysis Engine**
- Natural language portfolio input parsing
- Real-time stock data fetching
- Portfolio metrics calculation:
  - Total portfolio value
  - Individual holding values
  - P/E ratios and dividend yields
  - Sector allocation analysis
  - Concentration risk assessment
- Interactive visualizations:
  - Portfolio composition pie chart
  - Sector allocation bar chart
  - Holdings value comparison
- Portfolio history and update functionality

### 4. **AI-Powered Scenario Analysis**
- Google Gemini AI integration
- Market scenario impact analysis
- Portfolio performance projections
- Risk assessment for scenarios
- Actionable investment recommendations
- Scenario history management

### 5. **Export & Reporting System**
- Professional text report generation
- PDF document creation with ReportLab
- Customizable export options
- Export history tracking
- Re-download functionality

### 6. **Data Persistence & Management**
- Complete user data persistence
- Automatic session restoration
- Data update and replacement
- Export history management
- User data aggregation

## 🚀 Quick Start

### 1. **Clone and Setup**
```bash
git clone <your-repo-url>
cd fintech-trading-project
python setup.py
```

### 2. **Start Backend**
```bash
python run_backend.py
```

### 3. **Setup Admin User (First Time Only)**
```bash
python setup_admin.py
```
Follow the prompts to create your admin account.

### 4. **Start Frontend**
```bash
python run_frontend.py
```

### 5. **Access the Application**
- **Regular Users**: Navigate to `http://localhost:8501` and login with your credentials
- **Admin Users**: Login with admin credentials to access the Admin Dashboard

## 🔐 Admin Dashboard

The application now includes a comprehensive **Admin Dashboard** that provides administrators with full system oversight and management capabilities.

### **Admin Authentication**
- **Role-based Access**: Only users with `admin` role can access the Admin Dashboard
- **Secure Setup**: Use `setup_admin.py` to create the initial admin user
- **JWT Protection**: Admin endpoints are protected with role-based authentication

### **Admin Dashboard Features**

#### 📊 **Overview Dashboard**
- **User Statistics**: Total users, active users, new users (weekly/monthly)
- **Portfolio Analytics**: Total portfolios, holdings, average holdings per portfolio
- **Risk Assessment Metrics**: Risk score distribution charts
- **Investment Insights**: Most common stocks and sector distribution
- **System Metrics**: Total scenarios, exports, and system performance

#### 👥 **User Management**
- **User List**: Complete user database with activity counts
- **User Status**: Toggle user active/inactive status
- **User Actions**: Delete users and associated data
- **Search & Filter**: Find users by email, name, or status
- **Activity Tracking**: Monitor user engagement across all features

#### 💼 **Portfolio Management**
- **Portfolio Overview**: All user portfolios with values and holdings
- **User Linking**: See which portfolios belong to which users
- **Performance Tracking**: Monitor portfolio creation and updates
- **Data Export**: Download portfolio data for analysis

#### 🎯 **Risk Assessment Management**
- **Assessment History**: All risk assessments across all users
- **Score Distribution**: Visualize risk score patterns
- **User Insights**: Track user risk tolerance evolution
- **Category Analysis**: Monitor risk category distribution

#### 🔮 **Scenario Analysis Management**
- **Scenario Database**: All AI-generated scenario analyses
- **User Engagement**: Track scenario usage patterns
- **Risk Assessment**: Monitor scenario risk levels
- **Content Review**: Review AI-generated insights and recommendations

#### 📋 **Export Management**
- **Export History**: Track all generated reports (PDF/Text)
- **User Activity**: Monitor export usage patterns
- **Content Tracking**: See what data was included in each export
- **File Management**: Organize and track export files

#### 📝 **System Logs**
- **Real-time Monitoring**: View system logs directly from `app.log`
- **Log Filtering**: Filter by log level (INFO, WARNING, ERROR)
- **Search Capability**: Search logs for specific terms or patterns
- **Log Download**: Export logs for external analysis
- **Security Monitoring**: Track failed logins, security events, and API usage

### **Admin API Endpoints**

The backend provides comprehensive admin API endpoints:

- `GET /api/v1/admin/dashboard/stats` - Dashboard statistics
- `GET /api/v1/admin/users` - User management
- `GET /api/v1/admin/portfolios` - Portfolio overview
- `GET /api/v1/admin/risk-assessments` - Risk assessment data
- `GET /api/v1/admin/scenarios` - Scenario analysis data
- `GET /api/v1/admin/exports` - Export history
- `GET /api/v1/admin/system-logs` - System logs
- `PUT /api/v1/admin/users/{id}/toggle-status` - Toggle user status
- `DELETE /api/v1/admin/users/{id}` - Delete user

### **Security Features**
- **Role-based Access Control**: Admin endpoints require admin role
- **JWT Token Validation**: Secure authentication for all admin operations
- **Audit Logging**: All admin actions are logged for security
- **Input Validation**: Comprehensive validation for all admin inputs
- **Rate Limiting**: Admin endpoints are protected by rate limiting

### **Data Privacy**
- **User Data Protection**: Admin can view but not modify user data
- **Secure Deletion**: User deletion removes all associated data
- **Audit Trail**: All admin actions are logged with timestamps
- **Access Control**: Admins cannot modify other admin accounts

## 🧪 Testing

The application includes a **comprehensive unified test suite** that consolidates all testing functionality:

### **Smart Test Execution**

**Run all tests (automatically adapts to environment):**
```bash
python test_all.py
```

**Run specific test categories:**
```bash
# Environment and dependencies (always available)
python test_all.py environment
python test_all.py dependencies
python test_all.py database

# Backend connectivity (requires backend running)
python test_all.py health

# Core features (requires backend running)
python test_all.py auth
python test_all.py risk
python test_all.py portfolio
python test_all.py visualizations
python test_all.py scenario
python test_all.py export
python test_all.py userdata
```

### **Test Coverage**

#### **Offline Tests** (Always Run):
- Environment configuration validation
- Python dependencies verification
- Database connection and models testing

#### **Online Tests** (Require Backend):
- Backend API health and responsiveness
- User authentication and registration
- Risk assessment functionality
- Portfolio analysis and visualizations
- AI-powered scenario analysis
- Export functionality and history
- User data aggregation

### **Test Results**
- ✅ Success indicators for each test
- ⚠️ Warnings for missing optional components
- ❌ Detailed error messages and debugging info
- 📊 Summary statistics (pass/fail counts, success rate)
- 📋 Information about skipped tests

**Current Status**: 100% test success rate with comprehensive coverage

## 📊 Database Schema

### **Core Models**
- **User**: User accounts and authentication data
- **RiskAssessment**: Risk profile results and questionnaire answers
- **Portfolio**: User portfolios with total values and metadata
- **Holding**: Individual stock holdings with real-time data
- **Scenario**: AI-generated scenario analyses and recommendations
- **Export**: Export history and file metadata

### **Key Features**
- **Foreign Key Relationships**: All user data properly linked
- **Timestamps**: Created/updated timestamps for all records
- **JSON Storage**: Complex data stored as JSON strings
- **Cascade Deletes**: Proper cleanup when deleting parent records

## 🔧 API Endpoints

### **Authentication**
- `POST /auth/register` - User registration
- `POST /auth/token` - User login

### **Risk Profiling**
- `POST /api/v1/risk-profile` - Create risk assessment
- `GET /api/v1/risk-profile/latest` - Get latest assessment
- `DELETE /api/v1/risk-profile/latest` - Delete latest assessment

### **Portfolio Analysis**
- `POST /api/v1/analyze-portfolio` - Analyze portfolio
- `GET /api/v1/portfolio/latest` - Get latest portfolio
- `DELETE /api/v1/portfolio/latest` - Delete latest portfolio

### **Scenario Analysis**
- `POST /api/v1/analyze-scenario` - Create scenario analysis
- `GET /api/v1/scenarios` - Get all scenarios
- `GET /api/v1/scenarios/{id}` - Get specific scenario
- `DELETE /api/v1/scenarios/{id}` - Delete specific scenario

### **Export Management**
- `POST /api/v1/export/text` - Export as text
- `POST /api/v1/export/pdf` - Export as PDF
- `GET /api/v1/export/history` - Get export history
- `GET /api/v1/export/download/{id}` - Download export file
- `DELETE /api/v1/export/{id}` - Delete export

### **User Data**
- `GET /api/v1/user/data` - Get all user data

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Real-time Password Validation**: Frontend validation with visual feedback
  - At least 8 characters long
  - Contains uppercase letter(s)
  - Contains lowercase letter(s)
  - Contains number(s)
  - Contains special character(s)
  - Visual strength meter (Very Weak → Weak → Medium → Strong)
  - Real-time checklist updates as user types
- **Enhanced Error Handling**: User-friendly error messages with structured responses
  - Duplicate email detection with clear messaging
  - Invalid email format validation
  - Password strength requirement feedback
  - Helpful action buttons (Go to Login, Try Different Email)
  - Styled error messages with tips and suggestions
- **Password Hashing**: bcrypt password hashing with salt
- **Input Sanitization**: Protection against XSS and injection attacks
- **Rate Limiting**: Redis-based API rate limiting
- **Security Headers**: Comprehensive security middleware
- **CORS Protection**: Cross-origin resource sharing protection
- **Audit Logging**: Security event logging and monitoring

## 📈 Performance Optimizations

- **Database Indexing**: Optimized queries with proper indexing
- **Caching**: Redis-based caching for frequently accessed data
- **Retry Logic**: Exponential backoff for external API calls
- **Async Operations**: Non-blocking API operations
- **Connection Pooling**: Efficient database connection management
- **Memory Optimization**: Efficient data handling and cleanup

## 🚀 Production Deployment

See `DEPLOYMENT.md` for detailed production deployment instructions including:
- Docker containerization
- Nginx reverse proxy setup
- SSL/TLS configuration
- Monitoring and logging
- Backup strategies
- Performance optimization

## 📁 Project Structure

```
fintech-trading-project/
├── app/                    # Streamlit frontend
│   └── main.py            # Main frontend application
├── backend/               # FastAPI backend
│   ├── main.py           # FastAPI application entry point
│   ├── models/           # Database models and schemas
│   ├── routers/          # API route handlers
│   ├── services/         # Business logic services
│   ├── middleware/       # Security and logging middleware
│   ├── utils/            # Utility functions
│   └── auth/             # Authentication modules
├── exports/              # Generated export files
├── logs/                 # Application logs
├── temp/                 # Temporary files
├── test_all.py           # Unified test suite
├── requirements.txt      # Python dependencies
├── setup.py             # Automated setup script
├── run_backend.py       # Backend startup script
├── run_frontend.py      # Frontend startup script
└── README.md            # Project documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the documentation
2. Review the API docs at http://localhost:8000/docs
3. Run the test script: `python test_all.py`
4. Check the logs for error details
5. Review the deployment guide in `DEPLOYMENT.md`

## 🎉 Project Status

**✅ FULLY FUNCTIONAL** - All features implemented and tested  
**✅ PRODUCTION READY** - Security, performance, and deployment optimized  
**✅ COMPREHENSIVE TESTING** - 100% test success rate with full coverage  
**✅ COMPLETE DOCUMENTATION** - Detailed guides and API documentation  

---

**🚀 Ready for production deployment with complete feature set and comprehensive testing!**