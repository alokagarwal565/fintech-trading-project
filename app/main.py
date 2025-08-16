import streamlit as st
import os
import re
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import httpx
import asyncio
from typing import Optional, Dict, Any, Tuple
import json
import plotly.graph_objects as go
import html

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def is_valid_content(content: str, min_length: int = 10) -> bool:
    """
    Validate if content is meaningful and not empty HTML tags.
    
    Args:
        content: The content to validate
        min_length: Minimum length for content to be considered valid
        
    Returns:
        bool: True if content is valid, False otherwise
    """
    if not content or not isinstance(content, str):
        return False
    
    # Clean HTML tags
    clean_content = re.sub(r'<[^>]*>', '', content).strip()
    
    # Check for empty or invalid content
    if not clean_content or len(clean_content) < min_length:
        return False
    
    # Check for common empty HTML patterns
    empty_patterns = ['<div></div>', '</div></div>', '<p></p>', '<span></span>']
    if clean_content in empty_patterns:
        return False
    
    return True

def clean_and_validate_content(content: str, min_length: int = 10) -> Optional[str]:
    """
    Clean and validate content, returning None if invalid.
    
    Args:
        content: The content to clean and validate
        min_length: Minimum length for content to be considered valid
        
    Returns:
        str or None: Cleaned content if valid, None if invalid
    """
    if not is_valid_content(content, min_length):
        return None
    
    # Clean HTML tags and entities
    decoded_content = html.unescape(content)
    clean_content = re.sub(r'<[^>]*>', '', decoded_content)
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
    
    return clean_content if len(clean_content) >= min_length else None

def validate_password_strength(password: str) -> Tuple[bool, Dict[str, bool], str]:
    """
    Validate password strength and return detailed feedback
    Returns: (is_valid, requirements_met, strength_level)
    """
    if not password:
        return False, {}, "Empty"
    
    requirements = {
        "length": len(password) >= 8,
        "uppercase": bool(re.search(r'[A-Z]', password)),
        "lowercase": bool(re.search(r'[a-z]', password)),
        "digit": bool(re.search(r'\d', password)),
        "special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    }
    
    # Count met requirements
    met_count = sum(requirements.values())
    
    # Determine strength level
    if met_count == 5:
        strength = "Strong"
    elif met_count >= 3:
        strength = "Medium"
    elif met_count >= 1:
        strength = "Weak"
    else:
        strength = "Very Weak"
    
    # Password is valid if all requirements are met
    is_valid = all(requirements.values())
    
    return is_valid, requirements, strength

def get_strength_color(strength: str) -> str:
    """Get color for password strength indicator"""
    colors = {
        "Very Weak": "#ff4444",
        "Weak": "#ff8800", 
        "Medium": "#ffaa00",
        "Strong": "#00aa00"
    }
    return colors.get(strength, "#666666")

def get_strength_percentage(strength: str) -> int:
    """Get percentage for password strength bar"""
    percentages = {
        "Very Weak": 25,
        "Weak": 50,
        "Medium": 75,
        "Strong": 100
    }
    return percentages.get(strength, 0)

def display_password_validation(password: str, container):
    """Display real-time password validation feedback"""
    is_valid, requirements, strength = validate_password_strength(password)
    
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    .password-strength {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .requirement-item {
        margin: 5px 0;
        font-size: 14px;
    }
    .strength-indicator {
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 3px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Password strength meter
    color = get_strength_color(strength)
    percentage = get_strength_percentage(strength)
    st.markdown(f"""
    <div class="password-strength">
        <div style="margin-bottom: 10px;">
            <strong style="color: #000000;">Password Strength:</strong> 
            <span class="strength-indicator" style="color: {color}; background-color: {color}20;">{strength}</span>
        </div>
        <div style="margin-bottom: 15px;">
            <div style="background-color: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="background-color: {color}; height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
            </div>
        </div>
        <div><strong style="color: #000000;">Requirements:</strong></div>
    """, unsafe_allow_html=True)
    
    req_labels = {
        "length": "At least 8 characters",
        "uppercase": "Contains uppercase letter(s)",
        "lowercase": "Contains lowercase letter(s)", 
        "digit": "Contains number(s)",
        "special": "Contains special character(s)"
    }
    
    for req_key, label in req_labels.items():
        if requirements.get(req_key, False):
            st.markdown(f"<div class='requirement-item'>✅ {label}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='requirement-item'>❌ {label}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return is_valid

def display_error_message(message: str, error_type: str = "general"):
    """Display a styled error message with appropriate styling"""
    if error_type == "duplicate_email":
        st.markdown(f"""
        <div class="error-message">
            <strong>❌ {message}</strong>
            <small>💡 Tip: If you already have an account, try logging in instead.</small>
        </div>
        """, unsafe_allow_html=True)
    elif error_type == "invalid_email":
        st.markdown(f"""
        <div class="error-message">
            <strong>❌ {message}</strong>
            <small>💡 Tip: Please enter a valid email address (e.g., user@example.com)</small>
        </div>
        """, unsafe_allow_html=True)
    elif error_type == "weak_password":
        st.markdown(f"""
        <div class="error-message">
            <strong>❌ {message}</strong>
            <small>💡 Tip: Check the password requirements above and try again.</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="error-message">
            <strong>❌ {message}</strong>
        </div>
        """, unsafe_allow_html=True)

class APIError(Exception):
    """Custom exception for API errors with structured error details"""
    def __init__(self, status_code: int, error_type: str, message: str):
        self.status_code = status_code
        self.error_type = error_type
        self.message = message
        super().__init__(message)

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def _handle_error_response(self, response: httpx.Response):
        """Handle error responses and extract structured error information"""
        try:
            error_data = response.json()
            if isinstance(error_data, dict) and 'detail' in error_data:
                detail = error_data['detail']
                if isinstance(detail, dict) and 'error' in detail and 'message' in detail:
                    # Structured error response
                    raise APIError(
                        status_code=response.status_code,
                        error_type=detail['error'],
                        message=detail['message']
                    )
                elif isinstance(detail, str):
                    # Simple string error
                    raise APIError(
                        status_code=response.status_code,
                        error_type="unknown",
                        message=detail
                    )
        except (ValueError, KeyError):
            # Fallback for non-JSON responses
            pass
        
        # Default error handling
        response.raise_for_status()
    
    def get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    def register_user(self, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        data = {"email": email, "password": password}
        if full_name:
            data["full_name"] = full_name
        
        response = self.client.post(
            f"{self.base_url}/auth/register",
            json=data,
            headers=self.get_headers()
        )
        
        if response.status_code >= 400:
            self._handle_error_response(response)
        
        return response.json()
    
    def setup_admin_user(self, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Setup initial admin user"""
        data = {"email": email, "password": password}
        if full_name:
            data["full_name"] = full_name
        
        response = self.client.post(
            f"{self.base_url}/auth/setup-admin",
            json=data,
            headers=self.get_headers()
        )
        
        if response.status_code >= 400:
            self._handle_error_response(response)
        
        return response.json()
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        data = {"username": email, "password": password}
        response = self.client.post(
            f"{self.base_url}/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        return response.json()
    
    def get_user_data(self, token: str) -> Dict[str, Any]:
        """Fetch all user data including risk profile, portfolio, scenarios, and exports"""
        response = self.client.get(
            f"{self.base_url}/api/v1/user/data",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def assess_risk_profile(self, answers: list, token: str) -> Dict[str, Any]:
        data = {"answers": answers}
        response = self.client.post(
            f"{self.base_url}/api/v1/risk-profile",
            json=data,
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def get_latest_risk_profile(self, token: str) -> Dict[str, Any]:
        """Get the latest risk assessment for the user"""
        response = self.client.get(
            f"{self.base_url}/api/v1/risk-profile/latest",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def delete_latest_risk_profile(self, token: str) -> Dict[str, Any]:
        """Delete the latest risk assessment for the user"""
        response = self.client.delete(
            f"{self.base_url}/api/v1/risk-profile/latest",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def analyze_portfolio(self, portfolio_input: str, token: str) -> Dict[str, Any]:
        data = {"portfolio_input": portfolio_input}
        response = self.client.post(
            f"{self.base_url}/api/v1/analyze-portfolio",
            json=data,
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def get_latest_portfolio(self, token: str) -> Dict[str, Any]:
        """Get the latest portfolio analysis for the user"""
        response = self.client.get(
            f"{self.base_url}/api/v1/portfolio/latest",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def delete_latest_portfolio(self, token: str) -> Dict[str, Any]:
        """Delete the latest portfolio for the user"""
        response = self.client.delete(
            f"{self.base_url}/api/v1/portfolio/latest",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def analyze_scenario(self, scenario_text: str, token: str, portfolio_id: int = None) -> Dict[str, Any]:
        data = {"scenario_text": scenario_text}
        if portfolio_id:
            data["portfolio_id"] = portfolio_id
        
        response = self.client.post(
            f"{self.base_url}/api/v1/analyze-scenario",
            json=data,
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def get_user_scenarios(self, token: str) -> Dict[str, Any]:
        """Get all scenarios for the user"""
        response = self.client.get(
            f"{self.base_url}/api/v1/scenarios",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def delete_scenario(self, scenario_id: int, token: str) -> Dict[str, Any]:
        """Delete a specific scenario"""
        response = self.client.delete(
            f"{self.base_url}/api/v1/scenarios/{scenario_id}",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def export_text(self, token: str, include_risk_profile: bool = True, 
                   include_portfolio: bool = True, include_scenarios: bool = True) -> bytes:
        data = {
            "include_risk_profile": include_risk_profile,
            "include_portfolio": include_portfolio,
            "include_scenarios": include_scenarios
        }
        response = self.client.post(
            f"{self.base_url}/api/v1/export/text",
            json=data,
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.content
    
    def export_pdf(self, token: str, include_risk_profile: bool = True,
                  include_portfolio: bool = True, include_scenarios: bool = True) -> bytes:
        data = {
            "include_risk_profile": include_risk_profile,
            "include_portfolio": include_portfolio,
            "include_scenarios": include_scenarios
        }
        response = self.client.post(
            f"{self.base_url}/api/v1/export/pdf",
            json=data,
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.content
    
    def get_export_history(self, token: str) -> Dict[str, Any]:
        """Get export history for the user"""
        response = self.client.get(
            f"{self.base_url}/api/v1/export/history",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def download_export(self, export_id: int, token: str) -> bytes:
        """Download a specific export file"""
        response = self.client.get(
            f"{self.base_url}/api/v1/export/download/{export_id}",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.content
    
    def delete_export(self, export_id: int, token: str) -> Dict[str, Any]:
        """Delete a specific export"""
        response = self.client.delete(
            f"{self.base_url}/api/v1/export/{export_id}",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    # Admin-specific methods
    def get_admin_dashboard_stats(self, token: str) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        response = self.client.get(
            f"{self.base_url}/api/v1/admin/dashboard/stats",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def get_admin_users(self, token: str, skip: int = 0, limit: int = 100, active_only: bool = False) -> Dict[str, Any]:
        """Get all users for admin dashboard"""
        params = {"skip": skip, "limit": limit}
        if active_only:
            params["active_only"] = True
        
        response = self.client.get(
            f"{self.base_url}/api/v1/admin/users",
            params=params,
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def get_admin_portfolios(self, token: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Get all portfolios for admin dashboard"""
        response = self.client.get(
            f"{self.base_url}/api/v1/admin/portfolios",
            params={"skip": skip, "limit": limit},
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def get_admin_risk_assessments(self, token: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Get all risk assessments for admin dashboard"""
        response = self.client.get(
            f"{self.base_url}/api/v1/admin/risk-assessments",
            params={"skip": skip, "limit": limit},
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def get_admin_scenarios(self, token: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Get all scenarios for admin dashboard"""
        response = self.client.get(
            f"{self.base_url}/api/v1/admin/scenarios",
            params={"skip": skip, "limit": limit},
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def get_admin_exports(self, token: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Get all exports for admin dashboard"""
        response = self.client.get(
            f"{self.base_url}/api/v1/admin/exports",
            params={"skip": skip, "limit": limit},
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def get_admin_system_logs(self, token: str, skip: int = 0, limit: int = 100, level: str = None, search: str = None) -> Dict[str, Any]:
        """Get system logs for admin dashboard"""
        params = {"skip": skip, "limit": limit}
        if level:
            params["level"] = level
        if search:
            params["search"] = search
        
        response = self.client.get(
            f"{self.base_url}/api/v1/admin/system-logs",
            params=params,
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def toggle_user_status(self, user_id: int, token: str) -> Dict[str, Any]:
        """Toggle user active/inactive status"""
        response = self.client.put(
            f"{self.base_url}/api/v1/admin/users/{user_id}/toggle-status",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()
    
    def delete_user(self, user_id: int, token: str) -> Dict[str, Any]:
        """Delete a user and all associated data"""
        response = self.client.delete(
            f"{self.base_url}/api/v1/admin/users/{user_id}",
            headers=self.get_headers(token)
        )
        response.raise_for_status()
        return response.json()

# Initialize API client
api_client = APIClient(API_BASE_URL)

def add_custom_css():
    """
    Injects custom CSS to handle theme-specific styling and fix the text visibility issue.
    """
    st.markdown("""
        <style>
            /* --- GLOBAL STYLES FOR TEXT VISIBILITY --- */
            /* In dark mode, ensure text is a light color */
            [data-theme="dark"] .stMarkdown,
            [data-theme="dark"] .stText,
            [data-theme="dark"] .st-eb {
                color: #e0e0e0; /* Light gray for readability */
            }
            /* In light mode, ensure text is a dark color */
            [data-theme="light"] .stMarkdown,
            [data-theme="light"] .stText,
            [data-theme="light"] .st-eb {
                color: #222222; /* Dark gray for readability */
            }

            /* --- ERROR STATE STYLES --- */
            .error-field {
                border: 2px solid #ff4444 !important;
                background-color: #fff5f5 !important;
            }
            
            /* Improved error message styling */
            .error-message {
                background-color: #fef2f2;
                border: 2px solid #fecaca;
                border-left: 6px solid #ef4444;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                color: #991b1b !important;
                font-weight: 500;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                max-width: 100%;
                word-wrap: break-word;
                overflow-wrap: break-word;
                line-height: 1.6;
            }
            
            /* Ensure error message text is always visible and properly formatted */
            .error-message strong {
                color: #991b1b !important;
                font-size: 16px;
                font-weight: 600;
                display: block;
                margin-bottom: 8px;
            }
            
            .error-message small {
                color: #6b7280 !important;
                font-size: 14px;
                line-height: 1.5;
                display: block;
                margin-top: 8px;
                font-style: italic;
            }
            
            /* Dark theme specific error message styling */
            [data-theme="dark"] .error-message {
                background-color: #1f1f1f;
                border: 2px solid #4b5563;
                border-left: 6px solid #f87171;
                color: #fca5a5 !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }
            
            [data-theme="dark"] .error-message strong {
                color: #fca5a5 !important;
            }
            
            [data-theme="dark"] .error-message small {
                color: #d1d5db !important;
            }
            
            /* Fallback styling for better compatibility */
            .error-message * {
                color: inherit !important;
            }
            
            /* Ensure error messages are always visible regardless of theme */
            .stMarkdown .error-message,
            .stMarkdown .error-message * {
                color: #991b1b !important;
            }
            
            /* Force visibility for error message text */
            .error-message strong,
            .error-message small {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                width: 100% !important;
            }
            
            /* Additional styling for better error message visibility */
            .stMarkdown div[class*="error-message"] {
                background-color: #fef2f2 !important;
                border: 2px solid #fecaca !important;
                border-left: 6px solid #ef4444 !important;
                padding: 20px !important;
                margin: 20px 0 !important;
                border-radius: 8px !important;
                color: #991b1b !important;
                font-weight: 500 !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
                max-width: 100% !important;
                word-wrap: break-word !important;
                overflow-wrap: break-word !important;
            }
            
            /* Ensure all text within error messages is visible */
            .stMarkdown div[class*="error-message"] * {
                color: #991b1b !important;
            }
            
            /* Dark theme override for error messages */
            [data-theme="dark"] .stMarkdown div[class*="error-message"] {
                background-color: #1f1f1f !important;
                border: 2px solid #4b5563 !important;
                border-left: 6px solid #f87171 !important;
                color: #fca5a5 !important;
            }
            
            [data-theme="dark"] .stMarkdown div[class*="error-message"] * {
                color: #fca5a5 !important;
            }
            
            /* Final fallback to ensure error messages are always visible */
            div.error-message,
            div.error-message *,
            .stMarkdown div.error-message,
            .stMarkdown div.error-message * {
                color: #991b1b !important;
                background-color: #fef2f2 !important;
                border: 2px solid #fecaca !important;
                border-left: 6px solid #ef4444 !important;
                padding: 20px !important;
                margin: 20px 0 !important;
                border-radius: 8px !important;
                font-weight: 500 !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
                max-width: 100% !important;
                word-wrap: break-word !important;
                overflow-wrap: break-word !important;
            }
            
            /* Dark theme final fallback */
            [data-theme="dark"] div.error-message,
            [data-theme="dark"] div.error-message *,
            [data-theme="dark"] .stMarkdown div.error-message,
            [data-theme="dark"] .stMarkdown div.error-message * {
                color: #fca5a5 !important;
                background-color: #1f1f1f !important;
                border: 2px solid #4b5563 !important;
                border-left: 6px solid #f87171 !important;
            }
            
            /* Improved button styling */
            .helpful-button {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                margin: 10px 5px 0 0;
                font-weight: 500;
                transition: background-color 0.2s ease;
                display: inline-block;
            }
            
            .helpful-button:hover {
                background-color: #2563eb;
            }
            
            /* Button container for better layout */
            .button-container {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 15px;
            }
            
            /* Ensure error messages don't interfere with other elements */
            .error-message + * {
                margin-top: 20px !important;
            }
            
            /* Better spacing for form elements after error messages */
            .stButton {
                margin-top: 15px !important;
            }
            
            /* Ensure proper text wrapping in all contexts */
            .stMarkdown, .stText {
                word-wrap: break-word !important;
                overflow-wrap: break-word !important;
                max-width: 100% !important;
            }
            
            /* --- SCENARIO ANALYSIS CUSTOM STYLES (ADAPTED FOR DARK/LIGHT THEMES --- */
            .scenario-header {
                font-size: 24px;
                margin-bottom: 20px;
            }
            .section-header {
                font-size: 20px;
                margin: 15px 0;
                padding-bottom: 5px;
                border-bottom: 2px solid #eee;
            }
            
            /* Light theme colors for headers and boxes */
            [data-theme="light"] .scenario-header { color: #1f77b4; }
            [data-theme="light"] .section-header { color: #2c3e50; }
            [data-theme="light"] .insight-box {
                background-color: #f8f9fa;
                border-left: 4px solid #1f77b4;
            }
            [data-theme="light"] .st-expander details summary::marker { color: #2c3e50; }

            /* Dark theme colors for headers and boxes */
            [data-theme="dark"] .scenario-header { color: #8ecae6; } /* Lighter blue */
            [data-theme="dark"] .section-header { color: #bdbdbd; } /* Lighter gray */
            [data-theme="dark"] .insight-box {
                background-color: #333333;
                border-left: 4px solid #8ecae6;
            }
            [data-theme="dark"] .st-expander details summary::marker { color: #e0e0e0; }
            
            .risk-high {
                color: #dc3545;
                font-weight: bold;
            }
            .risk-medium {
                color: #ffc107;
                font-weight: bold;
            }
            .risk-low {
                color: #28a745;
                font-weight: bold;
            }
            
            /* Enhanced Scenario Analysis Styles */
            .scenario-card {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 16px;
                margin: 8px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .scenario-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            }
            
            .scenario-header-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            .insight-item {
                background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
                border: 1px solid #e1bee7;
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0;
                display: flex;
                align-items: center;
                transition: all 0.2s ease;
            }
            
            .insight-item:hover {
                transform: translateX(4px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .insight-number {
                background: #9c27b0;
                color: white;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                margin-right: 12px;
                flex-shrink: 0;
            }
            
            .recommendation-card {
                background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
                border: 1px solid #c8e6c9;
                border-radius: 8px;
                padding: 16px;
                margin: 12px 0;
                position: relative;
                transition: all 0.2s ease;
            }
            
            .recommendation-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .priority-badge {
                position: absolute;
                top: -8px;
                left: 16px;
                background: #4caf50;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
            }
            
            .risk-badge {
                background: var(--risk-bg);
                border: 2px solid var(--risk-border);
                border-radius: 20px;
                padding: 12px 20px;
                text-align: center;
                margin: 10px 0;
                transition: all 0.2s ease;
            }
            
            .risk-badge:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .analysis-section {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 10px 0;
                transition: all 0.2s ease;
            }
            
            .analysis-section:hover {
                border-color: #667eea;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
            }
            
            /* Enhanced Text Visibility and Contrast */
            .scenario-text-content {
                color: #2c3e50 !important;
                font-weight: 500 !important;
                line-height: 1.6 !important;
                background-color: #ffffff !important;
                padding: 16px !important;
                border-radius: 8px !important;
                border: 1px solid #e9ecef !important;
                margin: 8px 0 !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
            }
            
            .scenario-text-content strong {
                color: #1a365d !important;
                font-weight: 700 !important;
            }
            
            .scenario-text-content em {
                color: #2d3748 !important;
                font-style: italic !important;
            }
            
            /* Enhanced Section Headers */
            .section-header-enhanced {
                color: #2c3e50 !important;
                font-size: 18px !important;
                font-weight: 700 !important;
                margin: 20px 0 12px 0 !important;
                padding: 12px 16px !important;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
                border-left: 4px solid #667eea !important;
                border-radius: 6px !important;
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
            }
            
            .section-header-enhanced::before {
                content: "📋";
                font-size: 20px;
            }
            
            /* Enhanced Button Styling */
            .btn-primary-enhanced {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                border: none !important;
                padding: 10px 20px !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                transition: all 0.2s ease !important;
                cursor: pointer !important;
                box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3) !important;
            }
            
            .btn-primary-enhanced:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
            }
            
            .btn-danger-enhanced {
                background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%) !important;
                color: white !important;
                border: none !important;
                padding: 8px 16px !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                transition: all 0.2s ease !important;
                cursor: pointer !important;
                box-shadow: 0 2px 4px rgba(229, 62, 62, 0.3) !important;
            }
            
            .btn-danger-enhanced:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(229, 62, 62, 0.4) !important;
            }
            
            .btn-success-enhanced {
                background: linear-gradient(135deg, #38a169 0%, #2f855a 100%) !important;
                color: white !important;
                border: none !important;
                padding: 8px 16px !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                transition: all 0.2s ease !important;
                cursor: pointer !important;
                box-shadow: 0 2px 4px rgba(56, 161, 105, 0.3) !important;
            }
            
            .btn-success-enhanced:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(56, 161, 105, 0.4) !important;
            }
            
            /* Enhanced Content Boxes */
            .content-box-enhanced {
                background: #ffffff !important;
                border: 2px solid #e9ecef !important;
                border-radius: 12px !important;
                padding: 20px !important;
                margin: 16px 0 !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
                transition: all 0.3s ease !important;
            }
            
            .content-box-enhanced:hover {
                border-color: #667eea !important;
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15) !important;
                transform: translateY(-2px) !important;
            }
            
            .content-box-enhanced h4 {
                color: #2c3e50 !important;
                font-size: 16px !important;
                font-weight: 700 !important;
                margin: 0 0 12px 0 !important;
                padding-bottom: 8px !important;
                border-bottom: 2px solid #e9ecef !important;
            }
            
            .content-box-enhanced p {
                color: #4a5568 !important;
                font-size: 14px !important;
                line-height: 1.7 !important;
                margin: 8px 0 !important;
            }
            
            /* Enhanced Table Styling */
            .table-enhanced {
                background: #ffffff !important;
                border-radius: 12px !important;
                overflow: hidden !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
                margin: 16px 0 !important;
            }
            
            .table-enhanced th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                font-weight: 700 !important;
                padding: 16px 12px !important;
                text-align: left !important;
                border: none !important;
            }
            
            .table-enhanced td {
                padding: 12px !important;
                border-bottom: 1px solid #e9ecef !important;
                color: #4a5568 !important;
                font-weight: 500 !important;
            }
            
            .table-enhanced tr:hover {
                background-color: #f8f9fa !important;
            }
            
            /* Enhanced Risk Level Indicators */
            .risk-indicator-low {
                background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
                color: white !important;
                padding: 6px 12px !important;
                border-radius: 20px !important;
                font-weight: 700 !important;
                font-size: 12px !important;
                text-align: center !important;
                display: inline-block !important;
                box-shadow: 0 2px 8px rgba(72, 187, 120, 0.3) !important;
            }
            
            .risk-indicator-medium {
                background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%) !important;
                color: white !important;
                padding: 6px 12px !important;
                border-radius: 20px !important;
                font-weight: 700 !important;
                font-size: 12px !important;
                text-align: center !important;
                display: inline-block !important;
                box-shadow: 0 2px 8px rgba(237, 137, 54, 0.3) !important;
            }
            
            .risk-indicator-high {
                background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%) !important;
                color: white !important;
                padding: 6px 12px !important;
                border-radius: 20px !important;
                font-weight: 700 !important;
                font-size: 12px !important;
                text-align: center !important;
                display: inline-block !important;
                box-shadow: 0 2px 8px rgba(229, 62, 62, 0.3) !important;
            }
            
            /* Enhanced Expandable Sections */
            .expandable-section {
                background: #ffffff !important;
                border: 2px solid #e9ecef !important;
                border-radius: 12px !important;
                margin: 16px 0 !important;
                overflow: hidden !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
            }
            
            .expandable-header {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
                padding: 16px 20px !important;
                cursor: pointer !important;
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                border-bottom: 1px solid #e9ecef !important;
                transition: all 0.3s ease !important;
            }
            
            .expandable-header:hover {
                background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%) !important;
            }
            
            .expandable-header h4 {
                color: #2c3e50 !important;
                font-size: 16px !important;
                font-weight: 700 !important;
                margin: 0 !important;
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
            }
            
            .expandable-content {
                padding: 20px !important;
                background: #ffffff !important;
            }
            
            /* Mobile Responsiveness */
            @media (max-width: 768px) {
                .scenario-card {
                    padding: 12px;
                    margin: 6px 0;
                }
                
                .scenario-header-card {
                    padding: 16px;
                    margin-bottom: 16px;
                }
                
                .insight-item {
                    padding: 10px;
                    margin: 6px 0;
                }
                
                .insight-number {
                    width: 20px;
                    height: 20px;
                    font-size: 11px;
                    margin-right: 8px;
                }
                
                .recommendation-card {
                    padding: 12px;
                    margin: 8px 0;
                }
                
                .priority-badge {
                    font-size: 11px;
                    padding: 3px 8px;
                }
                
                .risk-badge {
                    padding: 10px 16px;
                    margin: 8px 0;
                }
                
                .content-box-enhanced {
                    padding: 16px;
                    margin: 12px 0;
                }
                
                .section-header-enhanced {
                    font-size: 16px;
                    padding: 10px 12px;
                }
            }
            
            /* Dark Theme Enhancements */
            [data-theme="dark"] .scenario-card {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                border-color: #4a5568;
                color: #e2e8f0;
            }
            
            [data-theme="dark"] .insight-item {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                border-color: #718096;
                color: #e2e8f0;
            }
            
            [data-theme="dark"] .recommendation-card {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                border-color: #718096;
                color: #e2e8f0;
            }
            
            [data-theme="dark"] .analysis-section {
                background-color: #2d3748;
                border-color: #4a5568;
                color: #e2e8f0;
            }
            
            [data-theme="dark"] .scenario-text-content {
                background-color: #2d3748 !important;
                color: #e2e8f0 !important;
                border-color: #4a5568 !important;
            }
            
            [data-theme="dark"] .scenario-text-content strong {
                color: #90cdf4 !important;
            }
            
            [data-theme="dark"] .content-box-enhanced {
                background: #2d3748 !important;
                border-color: #4a5568 !important;
                color: #e2e8f0 !important;
            }
            
            [data-theme="dark"] .content-box-enhanced h4 {
                color: #e2e8f0 !important;
                border-bottom-color: #4a5568 !important;
            }
            
            [data-theme="dark"] .content-box-enhanced p {
                color: #cbd5e0 !important;
            }
            
            [data-theme="dark"] .table-enhanced {
                background: #2d3748 !important;
            }
            
            [data-theme="dark"] .table-enhanced td {
                color: #e2e8f0 !important;
                border-bottom-color: #4a5568 !important;
            }
            
            [data-theme="dark"] .table-enhanced tr:hover {
                background-color: #4a5568 !important;
            }
            
            /* Animation for expandable sections */
            .st-expander {
                transition: all 0.3s ease;
            }
            
            .st-expander:hover {
                transform: translateY(-1px);
            }
            
            /* Button enhancements */
            .scenario-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                transition: all 0.2s ease;
                cursor: pointer;
            }
            
            .scenario-button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }
            
            /* Additional Mobile and Dark Theme Enhancements */
            @media (max-width: 480px) {
                .scenario-card {
                    padding: 10px;
                    margin: 4px 0;
                }
                
                .scenario-header-card {
                    padding: 14px;
                    margin-bottom: 14px;
                }
                
                .insight-item {
                    padding: 8px;
                    margin: 4px 0;
                }
                
                .insight-number {
                    width: 18px;
                    height: 18px;
                    font-size: 10px;
                    margin-right: 6px;
                }
                
                .recommendation-card {
                    padding: 10px;
                    margin: 6px 0;
                }
                
                .priority-badge {
                    font-size: 10px;
                    padding: 2px 6px;
                }
                
                .risk-badge {
                    padding: 8px 12px;
                    margin: 6px 0;
                }
                
                .content-box-enhanced {
                    padding: 14px;
                    margin: 10px 0;
                }
                
                .section-header-enhanced {
                    font-size: 15px;
                    padding: 8px 10px;
                }
                
                .btn-primary-enhanced,
                .btn-danger-enhanced,
                .btn-success-enhanced {
                    padding: 8px 12px;
                    font-size: 12px;
                }
            }
            
            /* Enhanced Dark Theme Support */
            @media (prefers-color-scheme: dark) {
                .scenario-card {
                    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                    border-color: #4a5568;
                    color: #e2e8f0;
                }
                
                .insight-item {
                    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                    border-color: #718096;
                    color: #e2e8f0;
                }
                
                .recommendation-card {
                    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                    border-color: #718096;
                    color: #e2e8f0;
                }
                
                .analysis-section {
                    background-color: #2d3748;
                    border-color: #4a5568;
                    color: #e2e8f0;
                }
                
                .scenario-text-content {
                    background-color: #2d3748 !important;
                    color: #e2e8f0 !important;
                    border-color: #4a5568 !important;
                }
                
                .scenario-text-content strong {
                    color: #90cdf4 !important;
                }
                
                .content-box-enhanced {
                    background: #2d3748 !important;
                    border-color: #4a5568 !important;
                    color: #e2e8f0 !important;
                }
                
                .content-box-enhanced h4 {
                    color: #e2e8f0 !important;
                    border-bottom-color: #4a5568 !important;
                }
                
                .content-box-enhanced p {
                    color: #cbd5e0 !important;
                }
                
                .table-enhanced {
                    background: #2d3748 !important;
                }
                
                .table-enhanced td {
                    color: #e2e8f0 !important;
                    border-bottom-color: #4a5568 !important;
                }
                
                .table-enhanced tr:hover {
                    background-color: #4a5568 !important;
                }
                
                .section-header-enhanced {
                    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
                    color: #e2e8f0 !important;
                    border-left-color: #667eea !important;
                }
                
                .expandable-header {
                    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
                    border-bottom-color: #4a5568 !important;
                }
                
                .expandable-header:hover {
                    background: linear-gradient(135deg, #4a5568 0%, #718096 100%) !important;
                }
                
                .expandable-header h4 {
                    color: #e2e8f0 !important;
                }
                
                .expandable-content {
                    background: #2d3748 !important;
                    color: #e2e8f0 !important;
                }
            }
            
            /* Print-friendly styles */
            @media print {
                .scenario-card,
                .content-box-enhanced,
                .insight-item,
                .recommendation-card {
                    break-inside: avoid;
                    page-break-inside: avoid;
                }
                
                .btn-primary-enhanced,
                .btn-danger-enhanced,
                .btn-success-enhanced {
                    display: none !important;
                }
            }
            
            /* Override Streamlit's default light backgrounds */
            .scenario-card-container .stMarkdown {
                background: transparent !important;
            }
            
            /* Ensure text is visible on dark background */
            .scenario-card-container strong {
                color: #ffffff !important;
            }
            
            .scenario-card-container {
                color: #ffffff !important;
            }
            
            /* Override Streamlit's default info box styling for dark theme */
            .scenario-card-container .stInfo {
                background-color: #1e1e1e !important;
                border: 1px solid #4a4a4a !important;
                color: #ffffff !important;
            }
            
            /* Ensure all text elements in scenario cards are visible */
            .scenario-card-container p,
            .scenario-card-container div,
            .scenario-card-container span {
                color: #ffffff !important;
            }
            
            /* Remove ALL white backgrounds from Streamlit components */
            .scenario-card-container .stAlert,
            .scenario-card-container .stAlert > div,
            .scenario-card-container .stAlert > div > div,
            .scenario-card-container .stInfo,
            .scenario-card-container .stInfo > div,
            .scenario-card-container .stInfo > div > div,
            .scenario-card-container .stSuccess,
            .scenario-card-container .stSuccess > div,
            .scenario-card-container .stSuccess > div > div,
            .scenario-card-container .stWarning,
            .scenario-card-container .stWarning > div,
            .scenario-card-container .stWarning > div > div,
            .scenario-card-container .stError,
            .scenario-card-container .stError > div,
            .scenario-card-container .stError > div > div {
                background-color: transparent !important;
                background: transparent !important;
            }
            
            /* Override Streamlit's default container backgrounds */
            .scenario-card-container .stContainer,
            .scenario-card-container .stContainer > div {
                background: transparent !important;
            }
            
            /* Remove any remaining white backgrounds */
            .scenario-card-container * {
                background-color: transparent !important;
                background: transparent !important;
            }
            
            /* Force dark theme for all elements within scenario cards */
            .scenario-card-container .stMarkdown,
            .scenario-card-container .stMarkdown > div,
            .scenario-card-container .stMarkdown > div > div {
                background: transparent !important;
                background-color: transparent !important;
            }
            
            /* Specific styling for Streamlit info boxes to match dark theme */
            .scenario-card-container .stInfo {
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%) !important;
                background-color: #1e1e1e !important;
                border: 1px solid #4a4a4a !important;
                color: #ffffff !important;
                border-radius: 8px !important;
                padding: 12px !important;
            }
            
            /* Override any Streamlit default styling that might create white backgrounds */
            .scenario-card-container .stInfo > div,
            .scenario-card-container .stInfo > div > div,
            .scenario-card-container .stInfo > div > div > div {
                background: transparent !important;
                background-color: transparent !important;
            }
            
            /* Ensure buttons also have dark theme */
            .scenario-card-container .stButton > button {
                background-color: #007bff !important;
                color: #ffffff !important;
                border: 1px solid #0056b3 !important;
            }
            
            .scenario-card-container .stButton > button:hover {
                background-color: #0056b3 !important;
            }
            
            /* Additional overrides to remove any remaining white backgrounds */
            .scenario-card-container .stAlert,
            .scenario-card-container .stAlert > div,
            .scenario-card-container .stAlert > div > div,
            .scenario-card-container .stAlert > div > div > div {
                background: transparent !important;
                background-color: transparent !important;
            }
            
            /* Override any Streamlit default styling */
            .scenario-card-container .stMarkdown > div,
            .scenario-card-container .stMarkdown > div > div,
            .scenario-card-container .stMarkdown > div > div > div {
                background: transparent !important;
                background-color: transparent !important;
            }
            
            /* Force dark theme for all nested elements */
            .scenario-card-container * {
                background: transparent !important;
                background-color: transparent !important;
            }
            
            /* Specific override for info boxes */
            .scenario-card-container .stInfo,
            .scenario-card-container .stInfo > div,
            .scenario-card-container .stInfo > div > div,
            .scenario-card-container .stInfo > div > div > div {
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%) !important;
                background-color: #1e1e1e !important;
            }
            
            /* Final aggressive override to remove ALL white backgrounds */
            .scenario-card-container,
            .scenario-card-container *,
            .scenario-card-container * *,
            .scenario-card-container * * * {
                background: transparent !important;
                background-color: transparent !important;
            }
            
            /* Exception: Only allow dark backgrounds for specific elements */
            .scenario-card-container {
                background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%) !important;
            }
            
            .scenario-card-container .stInfo {
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%) !important;
            }
        </style>
    """, unsafe_allow_html=True)

def load_user_data():
    """Load user data from the backend and populate session state"""
    try:
        with st.spinner("🔄 Loading your saved data..."):
            user_data = api_client.get_user_data(st.session_state.access_token)
            
            # Load risk profile
            if user_data.get('risk_profile'):
                st.session_state.risk_profile = user_data['risk_profile']
            
            # Load portfolio data
            if user_data.get('portfolio'):
                st.session_state.portfolio_data = user_data['portfolio']
            
            # Load scenarios
            if user_data.get('scenarios'):
                st.session_state.scenario_results = []
                for scenario in user_data['scenarios']:
                    # Create analysis structure with all available fields
                    analysis = {
                        'narrative': scenario['narrative'],
                        'insights': scenario['insights'],
                        'recommendations': scenario['recommendations'],
                        'risk_assessment': scenario['risk_assessment']
                    }
                    
                    # Add additional fields if they exist in the scenario data
                    if 'risk_details' in scenario:
                        analysis['risk_details'] = scenario['risk_details']
                    if 'portfolio_impact' in scenario:
                        analysis['portfolio_impact'] = scenario['portfolio_impact']
                    if 'portfolio_composition' in scenario:
                        analysis['portfolio_composition'] = scenario['portfolio_composition']
                    
                    scenario_result = {
                        'timestamp': datetime.fromisoformat(scenario['created_at'].replace('Z', '+00:00')),
                        'scenario': scenario['scenario_text'],
                        'analysis': analysis
                    }
                    st.session_state.scenario_results.append(scenario_result)
            
            # Load exports
            if user_data.get('exports'):
                st.session_state.export_history = user_data['exports']
            else:
                st.session_state.export_history = []
                
    except Exception as e:
        st.error(f"❌ Error loading user data: {str(e)}")

def main():
    st.set_page_config(
        page_title="AI-Powered Risk & Scenario Advisor",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom CSS at the start of the app
    add_custom_css()
    
    # Check if backend is running
    try:
        response = api_client.client.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            st.error("⚠️ Backend API is not responding. Please start the FastAPI server.")
            st.stop()
    except Exception as e:
        st.error("⚠️ Cannot connect to backend API. Please start the FastAPI server on port 8000.")
        st.stop()
    
    # Main header
    st.title("📊 AI-Powered Risk & Scenario Advisor for Retail Investors")
    st.markdown("---")
    
    # Authentication check
    if 'access_token' not in st.session_state:
        show_auth_page()
        return
    
    # Check if user is admin and show admin dashboard
    if st.session_state.get('user_role') == 'admin':
        show_admin_dashboard()
        return
    
    # Load user data on first login (for regular users)
    if 'user_data_loaded' not in st.session_state:
        load_user_data()
        st.session_state.user_data_loaded = True
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    page = st.sidebar.radio(
        "Choose a section:",
        ["🎯 Risk Profiling", "💼 Portfolio Analysis", "🔮 Scenario Analysis", "📋 Export Results"]
    )
    
    # Initialize session state
    if 'risk_profile' not in st.session_state:
        st.session_state.risk_profile = None
    if 'portfolio_data' not in st.session_state:
        st.session_state.portfolio_data = None
    if 'scenario_results' not in st.session_state:
        st.session_state.scenario_results = []
    if 'export_history' not in st.session_state:
        st.session_state.export_history = []
    
    # Page routing
    if page == "🎯 Risk Profiling":
        show_risk_profiling()
    elif page == "💼 Portfolio Analysis":
        show_portfolio_analysis()
    elif page == "🔮 Scenario Analysis":
        show_scenario_analysis()
    elif page == "📋 Export Results":
        show_export_options()

def show_auth_page():
    st.header("🔐 Authentication")
    
    # Initialize active tab in session state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Login"
    
    # Initialize form key for registration form
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    
    # Create tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    # Set active tab based on session state
    if st.session_state.active_tab == "Register":
        # Switch to register tab
        st.session_state.active_tab = "Login"  # Reset for next time
    
    with tab1:
        st.subheader("Login to Your Account")
        
        # Login form
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_btn"):
            if not login_email or not login_password:
                st.warning("Please enter both email and password.")
            else:
                try:
                    with st.spinner("Logging in..."):
                        result = api_client.login_user(login_email, login_password)
                        st.session_state.access_token = result["access_token"]
                        st.session_state.user_email = login_email
                        st.session_state.user_role = result.get("user_role", "user")
                        st.success("✅ Login successful!")
                        st.rerun()
                except Exception as e:
                    error_msg = str(e)
                    if "401 Unauthorized" in error_msg:
                        display_error_message("Invalid email or password. Please check your credentials.", "general")
                        # Add a helpful button to switch to register tab
                        st.markdown("**Don't have an account?**")
                        if st.button("📝 Create New Account", key="go_to_register", use_container_width=True):
                            st.session_state.active_tab = "Register"
                            st.rerun()
                    else:
                        display_error_message(f"Login failed: {error_msg}", "general")
    
    with tab2:
        st.subheader("Create New Account")
        
        # Use form keys that can be safely cleared
        if "registration_success" not in st.session_state:
            st.session_state.registration_success = False
        
        if st.session_state.registration_success:
            st.success("✅ Account created successfully! Please login.")
            # Reset the success flag
            st.session_state.registration_success = False
            # Clear form by using unique keys that can be safely reset
            if "form_key" not in st.session_state:
                st.session_state.form_key = 0
            st.session_state.form_key += 1
        else:
            # Registration form with real-time password validation
            reg_email = st.text_input("Email", key=f"reg_email_{st.session_state.form_key}")
            reg_password = st.text_input("Password", type="password", key=f"reg_password_{st.session_state.form_key}")
            
            # Real-time password validation
            if reg_password:
                with st.container():
                    st.markdown("---")
                    st.markdown("**🔒 Password Strength Check**")
                    password_valid = display_password_validation(reg_password, st)
                    st.markdown("---")
            
            reg_full_name = st.text_input("Full Name (Optional)", key=f"reg_full_name_{st.session_state.form_key}")
            
            # Registration button with validation
            if st.button("Register", key=f"register_btn_{st.session_state.form_key}"):
                if not reg_email or not reg_password:
                    st.warning("Please enter both email and password.")
                elif reg_password and not password_valid:
                    display_error_message("Your password is too weak. Please fulfill all requirements.", "weak_password")
                else:
                    try:
                        with st.spinner("Creating account..."):
                            result = api_client.register_user(reg_email, reg_password, reg_full_name)
                            # Set success flag instead of trying to clear session state
                            st.session_state.registration_success = True
                            st.rerun()
                    except APIError as e:
                        # Handle structured API errors
                        if e.error_type == "duplicate_email":
                            display_error_message(e.message, "duplicate_email")
                            # Add a helpful button to switch to login tab
                            st.markdown("**What would you like to do?**")
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button("🔐 Go to Login", key="go_to_login", use_container_width=True):
                                    st.session_state.active_tab = "Login"
                                    st.rerun()
                            with col2:
                                if st.button("🔄 Try Different Email", key="try_different_email", use_container_width=True):
                                    # Reset form key to clear form
                                    if "form_key" not in st.session_state:
                                        st.session_state.form_key = 0
                                    st.session_state.form_key += 1
                                    st.rerun()
                        elif e.error_type == "invalid_email":
                            display_error_message(e.message, "invalid_email")
                        elif e.error_type == "weak_password":
                            display_error_message(e.message, "weak_password")
                        else:
                            display_error_message(e.message, "general")
                    except Exception as e:
                        error_msg = str(e)
                        if "400 Bad Request" in error_msg:
                            if "already registered" in error_msg.lower():
                                display_error_message("This email is already registered. Please use another email or log in instead.", "duplicate_email")
                                # Add a helpful button to switch to login tab
                                st.markdown("**What would you like to do?**")
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    if st.button("🔐 Go to Login", key="go_to_login_alt", use_container_width=True):
                                        st.session_state.active_tab = "Login"
                                        st.rerun()
                                with col2:
                                    if st.button("🔄 Try Different Email", key="try_different_email_alt", use_container_width=True):
                                        # Reset form key to clear form
                                        if "form_key" not in st.session_state:
                                            st.session_state.form_key = 0
                                        st.session_state.form_key += 1
                                        st.rerun()
                            elif "Invalid email format" in error_msg:
                                display_error_message("Please enter a valid email address.", "invalid_email")
                        else:
                            display_error_message(f"Registration failed: {error_msg}", "general")

def show_risk_profiling():
    st.header("🎯 Risk Tolerance Assessment")
    
    # Check if user has existing risk profile
    if st.session_state.risk_profile:
        st.success("✅ You have completed a risk assessment!")
        
        # Display existing results
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Risk Profile", st.session_state.risk_profile['category'])
        with col2:
            st.metric("Risk Score", f"{st.session_state.risk_profile['score']}/24")
        
        st.write("**Profile Description:**")
        st.write(st.session_state.risk_profile['description'])
        
        st.write("**Investment Recommendations:**")
        for rec in st.session_state.risk_profile['recommendations']:
            st.write(f"• {rec}")
        
        st.write(f"**Assessment Date:** {st.session_state.risk_profile['created_at'][:10]}")
        
        # Option to retake assessment
        st.markdown("---")
        if st.button("🔄 Retake Risk Assessment"):
            try:
                with st.spinner("Deleting previous assessment..."):
                    api_client.delete_latest_risk_profile(st.session_state.access_token)
                st.session_state.risk_profile = None
                st.success("Previous assessment deleted. You can now retake the assessment.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error deleting previous assessment: {str(e)}")
        
        return
    
    st.write("Complete this questionnaire to understand your investment risk profile.")
    
    with st.form("risk_assessment_form"):
        st.subheader("Investment Risk Questionnaire")
        
        # Question 1: Investment experience
        q1 = st.radio(
            "1. How long have you been investing in stocks?",
            ["Less than 1 year", "1-3 years", "3-5 years", "More than 5 years"],
            key="q1"
        )
        
        # Question 2: Risk comfort
        q2 = st.radio(
            "2. If your portfolio lost 20% in a month, what would you do?",
            ["Sell immediately", "Sell some holdings", "Hold and wait", "Buy more"],
            key="q2"
        )
        
        # Question 3: Investment goals
        q3 = st.radio(
            "3. What is your primary investment goal?",
            ["Capital preservation", "Steady income", "Moderate growth", "Aggressive growth"],
            key="q3"
        )
        
        # Question 4: Time horizon
        q4 = st.radio(
            "4. When do you plan to use this money?",
            ["Within 1 year", "1-3 years", "3-7 years", "More than 7 years"],
            key="q4"
        )
        
        # Question 5: Income stability
        q5 = st.radio(
            "5. How stable is your current income?",
            ["Very unstable", "Somewhat unstable", "Stable", "Very stable"],
            key="q5"
        )
        
        # Question 6: Emergency fund
        q6 = st.radio(
            "6. Do you have an emergency fund covering 3-6 months of expenses?",
            ["No emergency fund", "Less than 3 months", "3-6 months", "More than 6 months"],
            key="q6"
        )
        
        submitted = st.form_submit_button("Assess My Risk Profile")
        
        if submitted:
            answers = [q1, q2, q3, q4, q5, q6]
            try:
                with st.spinner("🤖 Analyzing your risk profile..."):
                    result = api_client.assess_risk_profile(answers, st.session_state.access_token)
                    st.session_state.risk_profile = result
                    
                    # Display results
                    st.success("✅ Risk Assessment Complete!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Risk Profile", result['category'])
                    with col2:
                        st.metric("Risk Score", f"{result['score']}/24")
                    
                    st.write("**Profile Description:**")
                    st.write(result['description'])
                    
                    st.write("**Investment Recommendations:**")
                    for rec in result['recommendations']:
                        st.write(f"• {rec}")
                    
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error assessing risk profile: {str(e)}")

def show_portfolio_analysis():
    st.header("💼 Portfolio Analysis")
    
    # Check if user has existing portfolio data
    if st.session_state.portfolio_data:
        st.success("✅ You have a saved portfolio analysis!")
        
        # Display portfolio summary
        st.subheader("Portfolio Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Value", f"₹{st.session_state.portfolio_data['total_value']:,.2f}")
        with col2:
            st.metric("Total Holdings", st.session_state.portfolio_data['holdings_count'])
        with col3:
            # Safe check for updated_at field
            updated_date = st.session_state.portfolio_data.get('updated_at', st.session_state.portfolio_data.get('created_at', ''))
            if updated_date:
                st.metric("Last Updated", updated_date[:10])
            else:
                st.metric("Last Updated", "N/A")
        
        # Display holdings table
        if st.session_state.portfolio_data.get('holdings') or st.session_state.portfolio_data.get('valid_holdings'):
            st.subheader("📈 Your Holdings")
            # Handle both 'holdings' and 'valid_holdings' keys
            holdings_data = st.session_state.portfolio_data.get('holdings', st.session_state.portfolio_data.get('valid_holdings', []))
            if holdings_data:
                df = pd.DataFrame(holdings_data)
                st.dataframe(df, use_container_width=True)
        
        # Display visualizations if available
        if st.session_state.portfolio_data.get('visualizations'):
            st.subheader("📊 Portfolio Visualizations")
            vis_col1, vis_col2 = st.columns(2)
            with vis_col1:
                if st.session_state.portfolio_data['visualizations'].get('pie_chart') and st.session_state.portfolio_data['visualizations']['pie_chart'] != '{}':
                    try:
                        pie_fig = go.Figure(json.loads(st.session_state.portfolio_data['visualizations']['pie_chart']))
                        st.plotly_chart(pie_fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not display pie chart: {e}")
                
                if st.session_state.portfolio_data['visualizations'].get('sector_bar_chart') and st.session_state.portfolio_data['visualizations']['sector_bar_chart'] != '{}':
                    try:
                        sector_fig = go.Figure(json.loads(st.session_state.portfolio_data['visualizations']['sector_bar_chart']))
                        st.plotly_chart(sector_fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not display sector chart: {e}")
            
            with vis_col2:
                if st.session_state.portfolio_data['visualizations'].get('holdings_bar_chart') and st.session_state.portfolio_data['visualizations']['holdings_bar_chart'] != '{}':
                    try:
                        holdings_fig = go.Figure(json.loads(st.session_state.portfolio_data['visualizations']['holdings_bar_chart']))
                        st.plotly_chart(holdings_fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not display holdings chart: {e}")
        
        # Option to re-analyze portfolio
        st.markdown("---")
        if st.button("🔄 Re-analyze Portfolio"):
            try:
                with st.spinner("Deleting previous portfolio..."):
                    api_client.delete_latest_portfolio(st.session_state.access_token)
                st.session_state.portfolio_data = None
                st.success("Previous portfolio deleted. You can now re-analyze your portfolio.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error deleting previous portfolio: {str(e)}")
        
        return
    
    st.write("Enter your stock holdings in natural language (e.g., 'TCS: 10, HDFC Bank: 5 shares')")
    
    # Portfolio input
    portfolio_input = st.text_area(
        "Your Holdings:",
        placeholder="Example: TCS: 10, HDFC Bank: 5 shares, Reliance: 15, Infosys: 8",
        height=100
    )
    
    if st.button("Analyze Portfolio"):
        if portfolio_input.strip():
            try:
                with st.spinner("📊 Fetching live market data and analyzing portfolio..."):
                    result = api_client.analyze_portfolio(portfolio_input, st.session_state.access_token)
                    
                    # Debug: Log the response structure
                    if st.session_state.get('debug_mode'):
                        st.write("🔍 Debug: API Response Structure", result.keys())
                        st.write("🔍 Debug: Full Response", result)
                    
                    # Validate response structure
                    if not isinstance(result, dict):
                        st.error("❌ Invalid response format from server")
                        return
                    
                    if 'valid_holdings' not in result:
                        st.error(f"❌ Missing 'valid_holdings' in response. Available keys: {list(result.keys())}")
                        return
                    
                    st.session_state.portfolio_data = result
                    
                    # Normalize the data structure to ensure consistency
                    if 'valid_holdings' in result and 'holdings' not in result:
                        st.session_state.portfolio_data['holdings'] = result['valid_holdings']
                    
                    if result['valid_holdings'] and len(result['valid_holdings']) > 0:
                        st.success("✅ Portfolio analyzed successfully!")
                        
                        # Display portfolio summary
                        st.subheader("Portfolio Summary")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Value", f"₹{result['total_value']:,.2f}")
                        with col2:
                            st.metric("Total Holdings", result['holdings_count'])
                        with col3:
                            st.metric("Invalid Entries", len(result['invalid_holdings']))

                        # Display key metrics
                        st.subheader("Key Metrics")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Average P/E Ratio", f"{result['metrics']['average_pe_ratio']:.2f}" if result['metrics']['average_pe_ratio'] else "N/A")
                        with col2:
                            st.metric("Average Dividend Yield", f"{result['metrics']['average_dividend_yield']:.2f}%" if result['metrics']['average_dividend_yield'] else "N/A")
                        with col3:
                            st.metric("Largest Holding Concentration", f"{result['metrics']['concentration_percentage']:.2f}%")
                        
                        # Display valid holdings table
                        if result['valid_holdings']:
                            st.subheader("📈 Your Holdings")
                            df = pd.DataFrame(result['valid_holdings'])
                            st.dataframe(df, use_container_width=True)
                        
                        # Display visualizations
                        if result.get('visualizations'):
                            st.subheader("📊 Portfolio Visualizations")
                            vis_col1, vis_col2 = st.columns(2)
                            with vis_col1:
                                if result['visualizations']['pie_chart'] != '{}':
                                    pie_fig = go.Figure(json.loads(result['visualizations']['pie_chart']))
                                    st.plotly_chart(pie_fig, use_container_width=True)
                                if result['visualizations']['sector_bar_chart'] != '{}':
                                    sector_fig = go.Figure(json.loads(result['visualizations']['sector_bar_chart']))
                                    st.plotly_chart(sector_fig, use_container_width=True)
                            with vis_col2:
                                if result['visualizations']['holdings_bar_chart'] != '{}':
                                    holdings_fig = go.Figure(json.loads(result['visualizations']['holdings_bar_chart']))
                                    st.plotly_chart(holdings_fig, use_container_width=True)

                        # Display invalid holdings
                        if result['invalid_holdings']:
                            st.subheader("⚠️ Invalid Holdings")
                            for invalid in result['invalid_holdings']:
                                st.error(f"Could not process: {invalid}")
                        
                        st.rerun()
                    
                    elif result['valid_holdings'] is not None and len(result['valid_holdings']) == 0:
                        st.warning("⚠️ Portfolio analysis completed, but no valid holdings were found.")
                        st.info("This might happen if:")
                        st.info("• Stock symbols couldn't be resolved")
                        st.info("• Market data is unavailable")
                        st.info("• Input format needs adjustment")
                        
                        if result.get('invalid_holdings'):
                            st.subheader("⚠️ Invalid Entries")
                            for invalid in result['invalid_holdings']:
                                st.error(f"Could not process: {invalid}")
                    else:
                        st.error("❌ No valid holdings found. Please check your input format.")
                
            except Exception as e:
                st.error(f"❌ Error analyzing portfolio: {str(e)}")
        else:
            st.warning("Please enter your portfolio holdings.")

def create_risk_chart(risk_level: str):
    """
    Create a simple chart visualization for risk assessment
    """
    import plotly.graph_objects as go
    
    # Define risk levels and their values
    risk_levels = ['LOW', 'MEDIUM', 'HIGH']
    risk_values = [1, 2, 3]
    
    # Determine current risk level
    current_risk = 1  # Default to LOW
    if "medium" in risk_level.lower():
        current_risk = 2
    elif "high" in risk_level.lower():
        current_risk = 3
    
    # Create colors for the chart
    colors = ['#28a745', '#ffc107', '#dc3545']
    
    # Create the chart
    fig = go.Figure()
    
    # Add bars for each risk level
    for i, (level, value, color) in enumerate(zip(risk_levels, risk_values, colors)):
        opacity = 0.3 if value != current_risk else 1.0
        fig.add_trace(go.Bar(
            x=[level],
            y=[value],
            marker_color=color,
            opacity=opacity,
            showlegend=False,
            text=[f"{level} RISK" if value == current_risk else ""],
            textposition='middle',
            textfont=dict(color='white', size=12, weight='bold')
        ))
    
    # Update layout
    fig.update_layout(
        title="Risk Level Assessment",
        xaxis_title="Risk Level",
        yaxis_title="Risk Intensity",
        yaxis=dict(range=[0, 3.5], showticklabels=False),
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Update axes
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    
    return fig

def display_scenario_analysis(result: dict):
    """
    Enhanced display function for scenario analysis results with dynamic portfolio-aware analysis
    """
    
    # Scenario Header Card
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <h2 style="margin: 0; color: white; font-size: 24px;">🔮 Dynamic Scenario Analysis Results</h2>
            <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">
                Portfolio-aware AI analysis with dynamic risk assessment
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create three columns for better layout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # 📝 Analysis Overview Section
        narrative = result.get("narrative", "")
        clean_narrative = clean_and_validate_content(narrative, min_length=20)
        
        if clean_narrative:
            with st.expander("📝 Analysis Overview", expanded=True):
                st.markdown(f"""
                    <div class="content-box-enhanced">
                        <h4>📊 Dynamic Analysis Summary</h4>
                        <div class="scenario-text-content">
                            {clean_narrative}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # 🔑 Key Insights Section
        insights = result.get('insights', [])
        valid_insights = []
        
        # Filter out empty or invalid insights
        for insight in insights:
            clean_insight = clean_and_validate_content(insight, min_length=10)
            if clean_insight:
                valid_insights.append(clean_insight)
        
        # Only render the section if there are valid insights
        if valid_insights:
            with st.expander("🔑 Key Insights", expanded=True):
                st.markdown('<div class="section-header-enhanced">Portfolio-Specific Insights</div>', unsafe_allow_html=True)
                for i, clean_insight in enumerate(valid_insights, 1):
                    st.markdown(f"""
                        <div class="content-box-enhanced">
                            <div style="display: flex; align-items: flex-start; gap: 12px;">
                                <span class="insight-number">{i}</span>
                                <div class="scenario-text-content" style="flex: 1; margin: 0;">
                                    {clean_insight}
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        
        # ✅ Actionable Recommendations Section
        recommendations = result.get('recommendations', [])
        valid_recommendations = []
        
        # Filter out empty or invalid recommendations
        for rec in recommendations:
            clean_rec = clean_and_validate_content(rec, min_length=10)
            if clean_rec:
                valid_recommendations.append(clean_rec)
        
        # Only render the section if there are valid recommendations
        if valid_recommendations:
            with st.expander("✅ Actionable Recommendations", expanded=True):
                st.markdown('<div class="section-header-enhanced">Portfolio-Specific Actions</div>', unsafe_allow_html=True)
                for i, clean_rec in enumerate(valid_recommendations, 1):
                    st.markdown(f"""
                        <div class="content-box-enhanced">
                            <div style="position: relative;">
                                <div class="priority-badge" style="position: absolute; top: -8px; left: 16px; z-index: 10;">
                                    Priority {i}
                                </div>
                                <div class="scenario-text-content" style="margin-top: 8px;">
                                    {clean_rec}
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    with col2:
        # 📊 Enhanced Risk Assessment Section
        risk_level = result.get('risk_assessment', '')
        risk_details = result.get('risk_details', {})
        
        # Only render if there's a valid risk assessment
        if risk_level and isinstance(risk_level, str) and risk_level.strip():
            with st.expander("📊 Dynamic Risk Assessment", expanded=True):
                st.markdown('<div class="section-header-enhanced">Portfolio-Specific Risk Analysis</div>', unsafe_allow_html=True)
                
                # Determine risk level and color
                if risk_level in ['CRITICAL', 'HIGH']:
                    risk_color = "#dc3545"
                    risk_bg = "#f8d7da"
                    risk_icon = "🔴"
                    risk_class = "risk-indicator-high"
                elif risk_level == 'MEDIUM':
                    risk_color = "#ffc107"
                    risk_bg = "#fff3cd"
                    risk_icon = "🟡"
                    risk_class = "risk-indicator-medium"
                else:
                    risk_color = "#28a745"
                    risk_bg = "#d4edda"
                    risk_icon = "🟢"
                    risk_class = "risk-indicator-low"
                
                # Risk Level Badge
                st.markdown(f"""
                    <div class="content-box-enhanced">
                        <h4>Risk Level Assessment</h4>
                        <div class="{risk_class}">
                            {risk_icon} {risk_level} RISK
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Risk Score if available
                if risk_details and isinstance(risk_details, dict) and 'score' in risk_details:
                    st.markdown(f"""
                        <div class="content-box-enhanced">
                            <h4>Risk Score</h4>
                            <div style="font-size: 24px; font-weight: bold; color: {risk_color};">
                                {risk_details['score']:.1f}/100
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Primary Risk Factors
                if (risk_details and isinstance(risk_details, dict) and 
                    'primary_factors' in risk_details and 
                    risk_details['primary_factors'] and 
                    isinstance(risk_details['primary_factors'], list)):
                    
                    valid_factors = [factor for factor in risk_details['primary_factors'] 
                                   if factor and isinstance(factor, str) and factor.strip()]
                    
                    if valid_factors:
                        st.markdown("""
                            <div class="content-box-enhanced">
                                <h4>Primary Risk Factors</h4>
                            </div>
                        """, unsafe_allow_html=True)
                        for factor in valid_factors:
                            st.markdown(f"""
                                <div class="content-box-enhanced" style="margin-top: 8px;">
                                    <div style="color: #dc3545;">⚠️ {factor}</div>
                                </div>
                            """, unsafe_allow_html=True)

    with col3:
        # 📈 Portfolio Impact Analysis
        portfolio_impact = result.get('portfolio_impact', {})
        portfolio_composition = result.get('portfolio_composition', {})
        
        # Check if there's meaningful portfolio impact data
        has_impact_data = (portfolio_impact and isinstance(portfolio_impact, dict) and 
                          ('impact_severity' in portfolio_impact or 'affected_sectors' in portfolio_impact))
        has_composition_data = (portfolio_composition and isinstance(portfolio_composition, dict) and
                               ('diversification_level' in portfolio_composition or 
                                'num_holdings' in portfolio_composition))
        
        if has_impact_data or has_composition_data:
            with st.expander("📈 Portfolio Impact", expanded=True):
                st.markdown('<div class="section-header-enhanced">Scenario Impact Analysis</div>', unsafe_allow_html=True)
                
                # Impact Severity
                if (portfolio_impact and isinstance(portfolio_impact, dict) and 
                    'impact_severity' in portfolio_impact and 
                    portfolio_impact['impact_severity']):
                    severity = portfolio_impact['impact_severity']
                    severity_color = "#dc3545" if severity == "HIGH" else "#ffc107" if severity == "MEDIUM" else "#28a745"
                    st.markdown(f"""
                        <div class="content-box-enhanced">
                            <h4>Impact Severity</h4>
                            <div style="font-size: 18px; font-weight: bold; color: {severity_color};">
                                {severity}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Portfolio Composition Summary
                if (portfolio_composition and isinstance(portfolio_composition, dict) and
                    ('diversification_level' in portfolio_composition or 
                     'num_holdings' in portfolio_composition)):
                    
                    st.markdown("""
                        <div class="content-box-enhanced">
                            <h4>Portfolio Composition</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Diversification Level
                    if ('diversification_level' in portfolio_composition and 
                        portfolio_composition['diversification_level']):
                        div_level = portfolio_composition['diversification_level']
                        div_color = "#dc3545" if "CONCENTRATION" in div_level else "#ffc107" if "MODERATE" in div_level else "#28a745"
                        st.markdown(f"""
                            <div style="color: {div_color}; font-weight: bold; margin: 8px 0;">
                                {div_level.replace('_', ' ').title()}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Key Stats
                    if ('num_holdings' in portfolio_composition and 
                        'num_sectors' in portfolio_composition and
                        portfolio_composition['num_holdings'] and 
                        portfolio_composition['num_sectors']):
                        st.markdown(f"""
                            <div style="font-size: 12px; color: #6c757d; margin: 8px 0;">
                                {portfolio_composition['num_holdings']} holdings across {portfolio_composition['num_sectors']} sectors
                            </div>
                        """, unsafe_allow_html=True)
                
                # Affected Sectors
                if (portfolio_impact and isinstance(portfolio_impact, dict) and
                    'affected_sectors' in portfolio_impact and 
                    portfolio_impact['affected_sectors'] and
                    isinstance(portfolio_impact['affected_sectors'], list)):
                    
                    valid_sectors = [sector for sector in portfolio_impact['affected_sectors'] 
                                   if sector and isinstance(sector, dict) and 
                                   'sector' in sector and 'risk_level' in sector]
                    
                    if valid_sectors:
                        st.markdown("""
                            <div class="content-box-enhanced">
                                <h4>Most Affected Sectors</h4>
                            </div>
                        """, unsafe_allow_html=True)
                        for sector_risk in valid_sectors[:3]:  # Show top 3
                            risk_color = "#dc3545" if sector_risk['risk_level'] == "HIGH" else "#ffc107" if sector_risk['risk_level'] == "MEDIUM" else "#28a745"
                            st.markdown(f"""
                                <div style="margin: 4px 0; font-size: 12px;">
                                    <span style="color: {risk_color}; font-weight: bold;">{sector_risk['sector']}</span>
                                    <span style="color: #6c757d;"> ({sector_risk.get('weight', 0):.1f}%)</span>
                                </div>
                            """, unsafe_allow_html=True)

def show_scenario_analysis():
    """Enhanced Scenario Analysis section with improved UI/UX"""
    
    st.header("🔮 AI-Powered Scenario Analysis")
    
    # Automatically refresh data when page loads to ensure latest data
    if 'scenario_data_refreshed' not in st.session_state:
        load_user_data()
        st.session_state.scenario_data_refreshed = True
    
    # Add refresh button to reload data
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("")  # Spacer
    with col2:
        if st.button("🔄 Refresh Data", help="Reload latest scenario data"):
            load_user_data()
            st.session_state.scenario_data_refreshed = True
            st.rerun()
    
    # Check if user has saved scenarios
    if hasattr(st.session_state, 'scenario_results') and st.session_state.scenario_results:
        st.success(f"✅ You have {len(st.session_state.scenario_results)} saved scenario analyses!")
        
        # Recent Scenario Analyses Section
        st.subheader("📊 Recent Scenario Analyses")
        
        # Display scenarios in a simple row-based grid
        if len(st.session_state.scenario_results) > 0:
            # Simple CSS for clean cards
            st.markdown("""
                <style>
                .scenario-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin: 20px 0;
                }
                .scenario-card {
                    background: #2d2d2d;
                    border: 1px solid #4a4a4a;
                    border-radius: 8px;
                    padding: 16px;
                    color: white;
                }
                .scenario-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                }
                .scenario-title {
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                }
                .risk-badge {
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: bold;
                }
                .risk-critical { background: #dc3545; color: white; }
                .risk-high { background: #fd7e14; color: white; }
                .risk-medium { background: #ffc107; color: black; }
                .risk-low { background: #28a745; color: white; }
                .scenario-date {
                    color: #cccccc;
                    font-size: 12px;
                    margin-bottom: 8px;
                }
                .scenario-text {
                    color: white;
                    margin-bottom: 16px;
                    line-height: 1.4;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Create the grid container
            st.markdown('<div class="scenario-grid">', unsafe_allow_html=True)
            
            for i, result in enumerate(st.session_state.scenario_results):
                # Get risk level
                risk_level = result['analysis'].get('risk_assessment', 'LOW')
                
                # Determine risk class and text
                if isinstance(risk_level, str):
                    if risk_level in ['CRITICAL', 'HIGH']:
                        risk_class = "risk-high" if risk_level == "HIGH" else "risk-critical"
                        risk_text_short = "HIGH" if risk_level == "HIGH" else "CRITICAL"
                    elif risk_level == 'MEDIUM':
                        risk_class = "risk-medium"
                        risk_text_short = "MEDIUM"
                    else:
                        risk_class = "risk-low"
                        risk_text_short = "LOW"
                else:
                    risk_class = "risk-low"
                    risk_text_short = "LOW"
                
                # Create scenario card HTML
                scenario_number = len(st.session_state.scenario_results) - i
                date_str = result['timestamp'].strftime('%Y-%m-%d %H:%M')
                scenario_text = result['scenario'][:60] + "..." if len(result['scenario']) > 60 else result['scenario']
                
                card_html = f"""
                <div class="scenario-card">
                    <div class="scenario-header">
                        <div class="scenario-title">🔮 Scenario {scenario_number}</div>
                        <div class="risk-badge {risk_class}">{risk_text_short}</div>
                    </div>
                    <div class="scenario-date">Date: {date_str}</div>
                    <div class="scenario-text"><strong>Scenario:</strong> {scenario_text}</div>
                </div>
                """
                
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Display buttons immediately after each card
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 View Full", key=f"view_{i}", use_container_width=True):
                        st.session_state.selected_scenario = i
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{i}", use_container_width=True, type="secondary"):
                        try:
                            # Find the scenario ID from the backend
                            scenarios = api_client.get_user_scenarios(st.session_state.access_token)
                            if scenarios.get('scenarios'):
                                # Find the matching scenario by timestamp
                                target_timestamp = result['timestamp'].isoformat()
                                for scenario in scenarios['scenarios']:
                                    if scenario['created_at'].startswith(target_timestamp[:10]):
                                        api_client.delete_scenario(scenario['scenario_id'], st.session_state.access_token)
                                        st.session_state.scenario_results.pop(i)
                                        st.success("Scenario deleted successfully!")
                                        st.rerun()
                                        break
                        except Exception as e:
                            st.error(f"❌ Error deleting scenario: {str(e)}")
                
                # Add some spacing between card+button groups
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Close the grid container
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # No scenarios exist yet
        st.info("ℹ️ No saved scenario analyses found. Create your first scenario analysis below!")
        st.markdown("---")
    
    # Show full analysis if a scenario is selected
    if 'selected_scenario' in st.session_state:
        selected_idx = st.session_state.selected_scenario
        if selected_idx < len(st.session_state.scenario_results):
            selected_result = st.session_state.scenario_results[selected_idx]
            
            st.subheader(f"📊 Full Analysis: Scenario {len(st.session_state.scenario_results)-selected_idx}")
            
            # Close button
            if st.button("❌ Close Full Analysis"):
                del st.session_state.selected_scenario
                st.rerun()
            
            # Display full analysis
            display_scenario_analysis(selected_result['analysis'])
            
            st.markdown("---")
    
    # Scenario Comparison Section (if multiple scenarios exist)
    if len(st.session_state.scenario_results) > 1:
        st.subheader("📊 Scenario Comparison")
        st.write("Compare the risk levels and characteristics of your analyzed scenarios.")
        
        # Create comparison data with actual risk scores
        comparison_data = []
        for i, result in enumerate(st.session_state.scenario_results):
            risk_level = result['analysis'].get('risk_assessment', 'LOW')
            risk_details = result['analysis'].get('risk_details', {})
            actual_risk_score = risk_details.get('score', 0)
            
            # Convert risk level to display format
            if risk_level in ['CRITICAL', 'HIGH']:
                display_risk_level = risk_level
            elif risk_level == 'MEDIUM':
                display_risk_level = 'MEDIUM'
            else:
                display_risk_level = 'LOW'
            
            comparison_data.append({
                "Scenario": f"Scenario {len(st.session_state.scenario_results)-i}",
                "Date": result['timestamp'].strftime('%Y-%m-%d'),
                "Risk Level": display_risk_level,
                "Risk Score": actual_risk_score,
                "Insights Count": len(result['analysis'].get('insights', [])),
                "Recommendations Count": len(result['analysis'].get('recommendations', [])),
                "Description": result['scenario'][:40] + "..." if len(result['scenario']) > 40 else result['scenario']
            })
        
        # Display comparison table
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)
    
    # New Scenario Analysis Section
    st.subheader("🔮 Analyze New Scenario")
    st.write("Analyze how different market scenarios might affect your portfolio.")
    
    # Tip box
    st.info("💡 **Tip:** You can analyze multiple scenarios and compare their impacts on your portfolio. Each analysis is automatically saved for future reference.")
    
    # Scenario input options
    col1, col2 = st.columns(2)
    
    with col1:
        scenario_type = st.radio(
            "Choose scenario type:",
            ["Predefined Scenarios", "Custom Scenario"],
            horizontal=True
        )
    
    with col2:
        if scenario_type == "Predefined Scenarios":
            predefined_scenarios = [
                "Major IT company announces poor quarterly results",
                "RBI increases repo rate by 0.5%",
                "Global oil prices surge by 20%",
                "New government policy affects real estate sector",
                "Major banking sector merger announcement",
                "Technology sector faces regulatory scrutiny"
            ]
            
            selected_scenario = st.selectbox(
                "Select a scenario:",
                predefined_scenarios,
                help="Choose from common market scenarios"
            )
            
            # Show scenario description
            scenario_descriptions = {
                "Major IT company announces poor quarterly results": "Technology sector scenario - Affects IT stocks, software companies, and tech-dependent sectors",
                "RBI increases repo rate by 0.5%": "Monetary Policy Scenario - Affects banking, real estate, and interest-sensitive sectors",
                "Global oil prices surge by 20%": "Energy sector scenario - Affects oil companies, transportation, and energy-dependent industries",
                "New government policy affects real estate sector": "Policy scenario - Affects real estate, construction, and related financial services",
                "Major banking sector merger announcement": "Financial sector scenario - Affects banking stocks, financial services, and market sentiment",
                "Technology sector faces regulatory scrutiny": "Regulatory scenario - Affects tech companies, compliance costs, and sector valuations"
            }
            
            if selected_scenario in scenario_descriptions:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                        border: 1px solid #28a745;
                        border-radius: 8px;
                        padding: 12px;
                        margin: 8px 0;
                    ">
                        <strong style="color: #155724;">📋 Scenario Details:</strong><br>
                        <span style="color: #155724; font-size: 13px;">{scenario_descriptions[selected_scenario]}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            selected_scenario = st.text_area(
                "Describe your custom scenario:",
                placeholder="e.g., A major company in the pharmaceutical sector announces breakthrough drug approval...",
                height=100,
                help="Describe any market scenario you want to analyze"
            )
    
    # Analysis button
    if st.button("🤖 Analyze Scenario Impact", type="primary", use_container_width=True):
        if selected_scenario and selected_scenario.strip():
            # Check if user is authenticated
            if 'access_token' not in st.session_state or not st.session_state.access_token:
                st.error("❌ Please log in first to analyze scenarios.")
                return
            
            with st.spinner("🔮 AI is analyzing your scenario..."):
                try:
                    # Call the scenario analysis API with the required token parameter
                    response = api_client.analyze_scenario(selected_scenario, st.session_state.access_token)
                    
                    if response and 'narrative' in response:
                        # Save the analysis result
                        if 'scenario_results' not in st.session_state:
                            st.session_state.scenario_results = []
                        
                        # Create result object with timestamp
                        result = {
                            'scenario': selected_scenario,
                            'analysis': response,
                            'timestamp': datetime.now()
                        }
                        
                        # Add to beginning of list (most recent first)
                        st.session_state.scenario_results.insert(0, result)
                        
                        st.success("✅ Scenario analysis completed successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to analyze scenario. Please try again.")
                except Exception as e:
                    error_msg = str(e)
                    if "401" in error_msg or "Unauthorized" in error_msg:
                        st.error("❌ Session expired. Please log in again.")
                        st.session_state.clear()
                        st.rerun()
                    elif "500" in error_msg or "Internal Server Error" in error_msg:
                        st.error("❌ Server error occurred. Please try again later.")
                    elif "timeout" in error_msg.lower():
                        st.error("❌ Request timed out. Please try again.")
                    else:
                        st.error(f"❌ Error analyzing scenario: {error_msg}")
        else:
            st.warning("⚠️ Please enter a scenario to analyze.")

def show_export_options():
    st.header("📋 Export Your Analysis Results")
    
    # Display export history if any
    if st.session_state.export_history:
        st.success(f"✅ You have {len(st.session_state.export_history)} previous exports!")
        
        st.subheader("📊 Export History")
        
        # Create export history table
        export_summary = []
        for export in st.session_state.export_history:
            export_summary.append({
                "Date": export['created_at'][:10],
                "Type": export['export_type'].upper(),
                "Filename": export['filename'],
                "Includes": f"Risk: {'✓' if export['include_risk_profile'] else '✗'}, "
                          f"Portfolio: {'✓' if export['include_portfolio'] else '✗'}, "
                          f"Scenarios: {'✓' if export['include_scenarios'] else '✗'}"
            })
        
        df = pd.DataFrame(export_summary)
        st.dataframe(df, use_container_width=True)
        
        # Download buttons for recent exports
        st.subheader("📥 Download Previous Exports")
        for i, export in enumerate(st.session_state.export_history[:5]):  # Show last 5
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{export['filename']}** ({export['export_type'].upper()})")
                st.write(f"Created: {export['created_at'][:10]}")
            with col2:
                if st.button(f"📥 Download", key=f"download_{i}"):
                    try:
                        with st.spinner("Downloading..."):
                            file_content = api_client.download_export(export['export_id'], st.session_state.access_token)
                            
                            # Determine file type and MIME type
                            file_extension = "txt" if export['export_type'] == 'text' else "pdf"
                            mime_type = "text/plain" if export['export_type'] == 'text' else "application/pdf"
                            
                            st.download_button(
                                label="Click to download",
                                data=file_content,
                                file_name=export['filename'],
                                mime=mime_type,
                                key=f"download_btn_{i}"
                            )
                    except Exception as e:
                        st.error(f"❌ Error downloading file: {str(e)}")
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_export_{i}"):
                    try:
                        with st.spinner("Deleting..."):
                            api_client.delete_export(export['export_id'], st.session_state.access_token)
                            st.session_state.export_history.pop(i)
                            st.success("Export deleted successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting export: {str(e)}")
        
        st.markdown("---")
    
    st.write("Export your analysis results for future reference.")
    
    # Export options
    col1, col2, col3 = st.columns(3)
    with col1:
        include_risk = st.checkbox("Include Risk Profile", value=True)
    with col2:
        include_portfolio = st.checkbox("Include Portfolio", value=True)
    with col3:
        include_scenarios = st.checkbox("Include Scenarios", value=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export as Text"):
            try:
                with st.spinner("📄 Generating text report..."):
                    text_content = api_client.export_text(
                        st.session_state.access_token,
                        include_risk,
                        include_portfolio,
                        include_scenarios
                    )
                    
                    st.download_button(
                        label="Download Text Report",
                        data=text_content,
                        file_name=f"investment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    st.success("✅ Text report ready for download!")
                    
                    # Refresh export history
                    try:
                        export_history = api_client.get_export_history(st.session_state.access_token)
                        st.session_state.export_history = export_history.get('exports', [])
                    except:
                        pass
            except Exception as e:
                st.error(f"❌ Error generating text export: {str(e)}")
    
    with col2:
        if st.button("📑 Export as PDF"):
            try:
                with st.spinner("📑 Generating PDF report..."):
                    pdf_content = api_client.export_pdf(
                        st.session_state.access_token,
                        include_risk,
                        include_portfolio,
                        include_scenarios
                    )
                    
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_content,
                        file_name=f"investment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ PDF report ready for download!")
                    
                    # Refresh export history
                    try:
                        export_history = api_client.get_export_history(st.session_state.access_token)
                        st.session_state.export_history = export_history.get('exports', [])
                    except:
                        pass
            except Exception as e:
                st.error(f"❌ Error generating PDF export: {str(e)}")

def show_admin_dashboard():
    """Display the admin dashboard with comprehensive analytics and management features"""
    st.header("🔐 Admin Dashboard")
    st.markdown("---")
    
    # Initialize session state for admin data
    if 'admin_stats' not in st.session_state:
        st.session_state.admin_stats = None
    if 'admin_users' not in st.session_state:
        st.session_state.admin_users = []
    if 'admin_portfolios' not in st.session_state:
        st.session_state.admin_portfolios = []
    if 'admin_risk_assessments' not in st.session_state:
        st.session_state.admin_risk_assessments = []
    if 'admin_scenarios' not in st.session_state:
        st.session_state.admin_scenarios = []
    if 'admin_exports' not in st.session_state:
        st.session_state.admin_exports = []
    if 'admin_logs' not in st.session_state:
        st.session_state.admin_logs = []
    
    # Sidebar for admin actions
    st.sidebar.title("Admin Actions")
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Refresh data button
    if st.sidebar.button("🔄 Refresh All Data"):
        load_admin_data()
        st.rerun()
    
    # Load admin data if not already loaded
    if st.session_state.admin_stats is None:
        load_admin_data()
    
    # Admin dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", "👥 Users", "💼 Portfolios", "🎯 Risk Assessments", 
        "🔮 Scenarios", "📋 Exports", "📝 System Logs"
    ])
    
    with tab1:
        show_admin_overview()
    
    with tab2:
        show_admin_users()
    
    with tab3:
        show_admin_portfolios()
    
    with tab4:
        show_admin_risk_assessments()
    
    with tab5:
        show_admin_scenarios()
    
    with tab6:
        show_admin_exports()
    
    with tab7:
        show_admin_system_logs()

def load_admin_data():
    """Load all admin dashboard data from the backend"""
    try:
        with st.spinner("🔄 Loading admin data..."):
            # Load dashboard statistics
            st.session_state.admin_stats = api_client.get_admin_dashboard_stats(st.session_state.access_token)
            
            # Load user data
            st.session_state.admin_users = api_client.get_admin_users(st.session_state.access_token)
            
            # Load portfolio data
            st.session_state.admin_portfolios = api_client.get_admin_portfolios(st.session_state.access_token)
            
            # Load risk assessment data
            st.session_state.admin_risk_assessments = api_client.get_admin_risk_assessments(st.session_state.access_token)
            
            # Load scenario data
            st.session_state.admin_scenarios = api_client.get_admin_scenarios(st.session_state.access_token)
            
            # Load export data
            st.session_state.admin_exports = api_client.get_admin_exports(st.session_state.access_token)
            
            # Load system logs
            st.session_state.admin_logs = api_client.get_admin_system_logs(st.session_state.access_token)
            
        st.success("✅ Admin data loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error loading admin data: {str(e)}")

def show_admin_overview():
    """Display admin dashboard overview with key metrics and charts"""
    st.subheader("📊 Dashboard Overview")
    
    if not st.session_state.admin_stats:
        st.warning("No dashboard data available. Please refresh.")
        return
    
    stats = st.session_state.admin_stats
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats['total_users'])
        st.metric("Active Users", stats['active_users'])
    
    with col2:
        st.metric("New Users (Week)", stats['new_users_this_week'])
        st.metric("New Users (Month)", stats['new_users_this_month'])
    
    with col3:
        st.metric("Total Portfolios", stats['total_portfolios'])
        st.metric("Total Holdings", stats['total_holdings'])
    
    with col4:
        st.metric("Avg Holdings/Portfolio", f"{stats['average_holdings_per_portfolio']:.1f}")
        st.metric("Total Exports", stats['total_exports'])
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Risk Score Distribution")
        if stats['risk_score_distribution']:
            risk_data = pd.DataFrame([
                {"Score": score, "Count": count} 
                for score, count in stats['risk_score_distribution'].items()
            ])
            fig = go.Figure(data=[
                go.Bar(x=risk_data['Score'], y=risk_data['Count'], marker_color='#1f77b4')
            ])
            fig.update_layout(title="Risk Score Distribution", xaxis_title="Risk Score", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No risk assessment data available")
    
    with col2:
        st.subheader("📈 Most Common Stocks")
        if stats['most_common_stocks']:
            stock_data = pd.DataFrame(stats['most_common_stocks'])
            fig = go.Figure(data=[
                go.Bar(x=stock_data['symbol'], y=stock_data['count'], marker_color='#ff7f0e')
            ])
            fig.update_layout(title="Most Common Stocks", xaxis_title="Stock Symbol", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No portfolio data available")
    
    # Sector distribution
    if stats['most_common_sectors']:
        st.subheader("🏢 Sector Distribution")
        sector_data = pd.DataFrame(stats['most_common_sectors'])
        fig = go.Figure(data=[
            go.Pie(labels=sector_data['sector'], values=sector_data['count'])
        ])
        fig.update_layout(title="Portfolio Sector Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_admin_users():
    """Display user management interface"""
    st.subheader("👥 User Management")
    
    if not st.session_state.admin_users:
        st.warning("No user data available. Please refresh.")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        active_filter = st.checkbox("Show Active Users Only", value=True)
    with col2:
        search_term = st.text_input("Search Users", placeholder="Enter email or name...")
    
    # Filter users
    filtered_users = st.session_state.admin_users
    if active_filter:
        filtered_users = [u for u in filtered_users if u['is_active']]
    
    if search_term:
        filtered_users = [
            u for u in filtered_users 
            if search_term.lower() in u['email'].lower() or 
               (u['full_name'] and search_term.lower() in u['full_name'].lower())
        ]
    
    # Display users table
    if filtered_users:
        user_data = []
        for user in filtered_users:
            user_data.append({
                "ID": user['id'],
                "Email": user['email'],
                "Name": user['full_name'] or "N/A",
                "Role": user['role'],
                "Status": "🟢 Active" if user['is_active'] else "🔴 Inactive",
                "Created": user['created_at'][:10],
                "Risk Profiles": user['risk_assessments_count'],
                "Portfolios": user['portfolios_count'],
                "Scenarios": user['scenarios_count'],
                "Exports": user['exports_count']
            })
        
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True)
        
        # User actions
        st.subheader("User Actions")
        selected_user_id = st.selectbox(
            "Select User for Actions",
            options=[u['id'] for u in filtered_users if u['role'] != 'admin'],
            format_func=lambda x: next(u['email'] for u in filtered_users if u['id'] == x)
        )
        
        if selected_user_id:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Toggle Status", key=f"toggle_{selected_user_id}"):
                    try:
                        result = api_client.toggle_user_status(selected_user_id, st.session_state.access_token)
                        st.success(result['message'])
                        load_admin_data()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                if st.button("🗑️ Delete User", key=f"delete_{selected_user_id}"):
                    if st.checkbox("I understand this will permanently delete the user and all their data"):
                        try:
                            result = api_client.delete_user(selected_user_id, st.session_state.access_token)
                            st.success(result['message'])
                            load_admin_data()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    else:
        st.info("No users found matching the criteria")

def show_admin_portfolios():
    """Display portfolio management interface"""
    st.subheader("💼 Portfolio Management")
    
    if not st.session_state.admin_portfolios:
        st.warning("No portfolio data available. Please refresh.")
        return
    
    # Display portfolios table
    portfolio_data = []
    for portfolio in st.session_state.admin_portfolios:
        portfolio_data.append({
            "ID": portfolio['id'],
            "User": portfolio['user_email'],
            "Name": portfolio['name'],
            "Total Value": f"₹{portfolio['total_value']:,.2f}",
            "Holdings": portfolio['holdings_count'],
            "Created": portfolio['created_at'][:10],
            "Updated": portfolio['updated_at'][:10]
        })
    
    df = pd.DataFrame(portfolio_data)
    st.dataframe(df, use_container_width=True)

def show_admin_risk_assessments():
    """Display risk assessment management interface"""
    st.subheader("🎯 Risk Assessment Management")
    
    if not st.session_state.admin_risk_assessments:
        st.warning("No risk assessment data available. Please refresh.")
        return
    
    # Display risk assessments table
    risk_data = []
    for assessment in st.session_state.admin_risk_assessments:
        risk_data.append({
            "ID": assessment['id'],
            "User": assessment['user_email'],
            "Score": assessment['score'],
            "Category": assessment['category'],
            "Created": assessment['created_at'][:10]
        })
    
    df = pd.DataFrame(risk_data)
    st.dataframe(df, use_container_width=True)

def show_admin_scenarios():
    """Display scenario management interface"""
    st.subheader("🔮 Scenario Analysis Management")
    
    if not st.session_state.admin_scenarios:
        st.warning("No scenario data available. Please refresh.")
        return
    
    # Display scenarios table
    scenario_data = []
    for scenario in st.session_state.admin_scenarios:
        scenario_data.append({
            "ID": scenario['id'],
            "User": scenario['user_email'],
            "Scenario": scenario['scenario_text'][:50] + "..." if len(scenario['scenario_text']) > 50 else scenario['scenario_text'],
            "Risk Level": scenario['risk_assessment'].split()[0] if scenario['risk_assessment'] else "N/A",
            "Created": scenario['created_at'][:10]
        })
    
    df = pd.DataFrame(scenario_data)
    st.dataframe(df, use_container_width=True)

def show_admin_exports():
    """Display export management interface"""
    st.subheader("📋 Export Management")
    
    if not st.session_state.admin_exports:
        st.warning("No export data available. Please refresh.")
        return
    
    # Display exports table
    export_data = []
    for export in st.session_state.admin_exports:
        export_data.append({
            "ID": export['id'],
            "User": export['user_email'],
            "Type": export['export_type'].upper(),
            "Filename": export['filename'],
            "Includes": f"Risk: {'✓' if export['include_risk_profile'] else '✗'}, "
                       f"Portfolio: {'✓' if export['include_portfolio'] else '✗'}, "
                       f"Scenarios: {'✓' if export['include_scenarios'] else '✗'}",
            "Created": export['created_at'][:10]
        })
    
    df = pd.DataFrame(export_data)
    st.dataframe(df, use_container_width=True)

def show_admin_system_logs():
    """Display system logs interface"""
    st.subheader("📝 System Logs")
    
    # Log filters
    col1, col2, col3 = st.columns(3)
    with col1:
        log_level = st.selectbox("Log Level", ["All", "INFO", "WARNING", "ERROR"], key="log_level")
    with col2:
        search_logs = st.text_input("Search Logs", placeholder="Enter search term...", key="search_logs")
    with col3:
        if st.button("🔍 Search Logs", key="search_logs_btn"):
            try:
                level_filter = log_level if log_level != "All" else None
                st.session_state.admin_logs = api_client.get_admin_system_logs(
                    st.session_state.access_token,
                    level=level_filter,
                    search=search_logs if search_logs else None
                )
                st.rerun()
            except Exception as e:
                st.error(f"Error searching logs: {str(e)}")
    
    # Display logs
    if st.session_state.admin_logs:
        log_data = []
        for log in st.session_state.admin_logs:
            log_data.append({
                "Timestamp": log['timestamp'],
                "Level": log['level'],
                "Module": log['module'],
                "Function": log['function'],
                "Line": log['line'],
                "Message": log['message'][:100] + "..." if len(log['message']) > 100 else log['message']
            })
        
        df = pd.DataFrame(log_data)
        st.dataframe(df, use_container_width=True)
        
        # Log download
        if st.button("📥 Download Logs"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Click to download",
                data=csv,
                file_name=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No log data available. Please refresh or search for specific logs.")

if __name__ == "__main__":
    main()
