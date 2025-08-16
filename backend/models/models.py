from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RiskCategory(str, Enum):
    CONSERVATIVE = "Conservative"
    MODERATE = "Moderate"
    AGGRESSIVE = "Aggressive"

class ExportType(str, Enum):
    TEXT = "text"
    PDF = "pdf"

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    portfolios: List["Portfolio"] = Relationship(back_populates="user")
    risk_assessments: List["RiskAssessment"] = Relationship(back_populates="user")
    scenarios: List["Scenario"] = Relationship(back_populates="user")
    exports: List["Export"] = Relationship(back_populates="user")

class Portfolio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str = Field(default="My Portfolio")
    total_value: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="portfolios")
    holdings: List["Holding"] = Relationship(back_populates="portfolio")

class Holding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolio.id")
    company_name: str
    symbol: str
    quantity: int
    current_price: float
    total_value: float
    sector: Optional[str] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    portfolio: Portfolio = Relationship(back_populates="holdings")

class RiskAssessment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    score: int
    category: RiskCategory
    description: str
    recommendations: str  # JSON string of recommendations list
    answers: str  # JSON string of questionnaire answers
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="risk_assessments")

class Scenario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    scenario_text: str
    analysis_narrative: str
    insights: str  # JSON string of insights list
    recommendations: str  # JSON string of recommendations list
    risk_assessment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="scenarios")

class Export(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    export_type: ExportType
    filename: str
    file_path: str
    include_risk_profile: bool = True
    include_portfolio: bool = True
    include_scenarios: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="exports")

# Pydantic models for API requests/responses
class UserCreate(SQLModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(SQLModel):
    email: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str
    user_role: str

class RiskProfileRequest(SQLModel):
    answers: List[str]

class PortfolioAnalysisRequest(SQLModel):
    portfolio_input: str

class ScenarioAnalysisRequest(SQLModel):
    scenario_text: str
    portfolio_id: Optional[int] = None

class ExportRequest(SQLModel):
    include_risk_profile: bool = True
    include_portfolio: bool = True
    include_scenarios: bool = True

# Response models for user data retrieval
class UserDataResponse(SQLModel):
    risk_profile: Optional[dict] = None
    portfolio: Optional[dict] = None
    scenarios: List[dict] = []
    exports: List[dict] = []

# Admin Dashboard Response Models
class AdminUserSummary(SQLModel):
    id: int
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    risk_assessments_count: int
    portfolios_count: int
    scenarios_count: int
    exports_count: int

class AdminPortfolioSummary(SQLModel):
    id: int
    user_email: str
    user_full_name: Optional[str]
    name: str
    total_value: float
    holdings_count: int
    created_at: datetime
    updated_at: datetime

class AdminRiskAssessmentSummary(SQLModel):
    id: int
    user_email: str
    user_full_name: Optional[str]
    score: int
    category: RiskCategory
    created_at: datetime

class AdminScenarioSummary(SQLModel):
    id: int
    user_email: str
    user_full_name: Optional[str]
    scenario_text: str
    risk_assessment: str
    created_at: datetime

class AdminExportSummary(SQLModel):
    id: int
    user_email: str
    user_full_name: Optional[str]
    export_type: ExportType
    filename: str
    include_risk_profile: bool
    include_portfolio: bool
    include_scenarios: bool
    created_at: datetime

class AdminDashboardStats(SQLModel):
    total_users: int
    active_users: int
    new_users_this_week: int
    new_users_this_month: int
    total_portfolios: int
    total_holdings: int
    average_holdings_per_portfolio: float
    total_risk_assessments: int
    risk_score_distribution: dict
    total_scenarios: int
    total_exports: int
    most_common_stocks: List[dict]
    most_common_sectors: List[dict]

class AdminSystemLog(SQLModel):
    timestamp: str
    level: str
    message: str
    module: str
    function: str
    line: int