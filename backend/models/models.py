from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RiskCategory(str, Enum):
    CONSERVATIVE = "Conservative"
    MODERATE = "Moderate"
    AGGRESSIVE = "Aggressive"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    portfolios: List["Portfolio"] = Relationship(back_populates="user")
    risk_assessments: List["RiskAssessment"] = Relationship(back_populates="user")
    scenarios: List["Scenario"] = Relationship(back_populates="user")

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