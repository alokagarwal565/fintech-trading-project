from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from backend.models.models import User, UserCreate, UserLogin, Token
from backend.models.database import get_session
from backend.auth.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend.middleware.security import security_middleware
from backend.utils.logger import app_logger, log_security_event

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, request: Request, session: Session = Depends(get_session)):
    """
    Register a new user with enhanced security validation
    """
    # Input validation and sanitization
    if not security_middleware.validate_email(user_data.email):
        log_security_event(app_logger, "INVALID_EMAIL", f"Invalid email format: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    if not security_middleware.validate_password_strength(user_data.password):
        log_security_event(app_logger, "WEAK_PASSWORD", f"Weak password attempted for email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    # Sanitize inputs
    sanitized_email = security_middleware.sanitize_input(user_data.email)
    sanitized_full_name = security_middleware.sanitize_input(user_data.full_name) if user_data.full_name else None
    
    # Check if user already exists
    statement = select(User).where(User.email == sanitized_email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        log_security_event(app_logger, "DUPLICATE_REGISTRATION", f"Duplicate registration attempt for: {sanitized_email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=sanitized_email,
        hashed_password=hashed_password,
        full_name=sanitized_full_name
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    app_logger.info(f"New user registered: {user.id} ({sanitized_email})")
    return {"message": "User registered successfully", "user_id": user.id}

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None, session: Session = Depends(get_session)):
    """
    Login and get access token with enhanced security
    """
    # Input validation
    if not security_middleware.validate_email(form_data.username):
        log_security_event(app_logger, "INVALID_LOGIN_EMAIL", f"Invalid email format in login: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        # Log failed login attempt
        client_ip = request.client.host if request and request.client else "unknown"
        log_security_event(app_logger, "FAILED_LOGIN", f"Failed login attempt for email: {form_data.username}", ip_address=client_ip)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    app_logger.info(f"User logged in successfully: {user.id} ({user.email})")
    return {"access_token": access_token, "token_type": "bearer"}