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

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

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
            <strong>Password Strength:</strong> 
            <span class="strength-indicator" style="color: {color}; background-color: {color}20;">{strength}</span>
        </div>
        <div style="margin-bottom: 15px;">
            <div style="background-color: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="background-color: {color}; height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
            </div>
        </div>
        <div><strong>Requirements:</strong></div>
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
                    scenario_result = {
                        'timestamp': datetime.fromisoformat(scenario['created_at'].replace('Z', '+00:00')),
                        'scenario': scenario['scenario_text'],
                        'analysis': {
                            'narrative': scenario['narrative'],
                            'insights': scenario['insights'],
                            'recommendations': scenario['recommendations'],
                            'risk_assessment': scenario['risk_assessment']
                        }
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
        
        # Registration form with real-time password validation
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        
        # Real-time password validation
        if reg_password:
            with st.container():
                st.markdown("---")
                st.markdown("**🔒 Password Strength Check**")
                password_valid = display_password_validation(reg_password, st)
                st.markdown("---")
        
        reg_full_name = st.text_input("Full Name (Optional)", key="reg_full_name")
        
        # Registration button with validation
        if st.button("Register", key="register_btn"):
            if not reg_email or not reg_password:
                st.warning("Please enter both email and password.")
            elif reg_password and not password_valid:
                display_error_message("Your password is too weak. Please fulfill all requirements.", "weak_password")
            else:
                try:
                    with st.spinner("Creating account..."):
                        result = api_client.register_user(reg_email, reg_password, reg_full_name)
                        st.success("✅ Account created successfully! Please login.")
                        # Clear form
                        st.session_state.reg_email = ""
                        st.session_state.reg_password = ""
                        st.session_state.reg_full_name = ""
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
                                st.session_state.reg_email = ""
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
                        # Fallback for non-structured errors
                        if "Password must be at least 8 characters" in error_msg:
                            display_error_message("Password strength requirements not met. Please check the requirements above.", "weak_password")
                        elif "Email already registered" in error_msg:
                            display_error_message("This email is already registered. Please use a different email or login.", "duplicate_email")
                        elif "Invalid email format" in error_msg:
                            display_error_message("Please enter a valid email address.", "invalid_email")
                        else:
                            display_error_message(f"Registration failed: {error_msg}", "general")
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
                    st.session_state.portfolio_data = result
                    
                    # Normalize the data structure to ensure consistency
                    if 'valid_holdings' in result and 'holdings' not in result:
                        st.session_state.portfolio_data['holdings'] = result['valid_holdings']
                    
                    if result['valid_holdings']:
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
                    
                    else:
                        st.error("❌ No valid holdings found. Please check your input format.")
                
            except Exception as e:
                st.error(f"❌ Error analyzing portfolio: {str(e)}")
        else:
            st.warning("Please enter your portfolio holdings.")


def display_scenario_analysis(result: dict):
    """
    Enhanced display function for scenario analysis results
    """
    # Custom CSS for styling is now handled by the global function at the start of the app
    # st.markdown("""...""", unsafe_allow_html=True) is no longer needed here.

    # Overview Section
    st.markdown(f'<div class="scenario-header">Scenario Analysis Results</div>',
                unsafe_allow_html=True)
    
    with st.expander("📝 Analysis Overview", expanded=True):
        st.markdown(f'<div class="insight-box">{result["narrative"]}</div>',
                    unsafe_allow_html=True)

    # Key Insights
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.markdown('<div class="section-header">Key Insights</div>',
                    unsafe_allow_html=True)
        for insight in result['insights']:
            # The global CSS now handles the text color here
            st.write(f'• {insight}')

    with col2:
        st.markdown('<div class="section-header">Risk Assessment</div>',
                    unsafe_allow_html=True)
        risk_level = "HIGH" if "high" in result['risk_assessment'].lower() else \
                     "MEDIUM" if "medium" in result['risk_assessment'].lower() else "LOW"
        risk_class = f"risk-{risk_level.lower()}"
        st.markdown(f'<div class="{risk_class}">{risk_level} RISK</div>',
                    unsafe_allow_html=True)
        st.write(result['risk_assessment'])

    # Recommendations
    st.markdown('<div class="section-header">Actionable Recommendations</div>',
                unsafe_allow_html=True)
    
    for i, rec in enumerate(result['recommendations'], 1):
        st.markdown(f"""
            <div class="insight-box">
                <strong>{i}.</strong> {rec}
            </div>
        """, unsafe_allow_html=True)


def show_scenario_analysis():
    st.header("🔮 AI-Powered Scenario Analysis")
    
    # Display existing scenarios if any
    if st.session_state.scenario_results:
        st.success(f"✅ You have {len(st.session_state.scenario_results)} saved scenario analyses!")
        
        # Show recent scenarios
        st.subheader("📋 Recent Scenario Analyses")
        for i, result in enumerate(st.session_state.scenario_results[:3]):  # Show last 3
            with st.expander(f"Scenario {len(st.session_state.scenario_results)-i}: {result['scenario'][:50]}...", expanded=False):
                st.write(f"**Analyzed on:** {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write("**Scenario:**", result['scenario'])
                
                # Delete button for each scenario
                col1, col2 = st.columns([3, 1])
                with col1:
                    display_scenario_analysis(result['analysis'])
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_scenario_{i}"):
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
        
        st.markdown("---")
    
    st.write("Analyze how different market scenarios might affect your portfolio.")
    
    # Scenario selection
    scenario_type = st.radio(
        "Choose scenario type:",
        ["Predefined Scenarios", "Custom Scenario"]
    )
    
    if scenario_type == "Predefined Scenarios":
        predefined_scenarios = [
            "RBI increases repo rate by 0.5%",
            "Oil prices surge by 20% due to geopolitical tensions",
            "US Federal Reserve cuts interest rates",
            "Major IT company announces poor quarterly results",
            "Government announces new infrastructure spending",
            "Global recession fears increase",
            "New technology disrupts traditional banking",
            "Inflation rises to 7%"
        ]
        
        selected_scenario = st.selectbox(
            "Select a scenario:",
            predefined_scenarios
        )
        scenario_text = selected_scenario
    
    else:
        scenario_text = st.text_area(
            "Describe your custom scenario:",
            placeholder="Example: What if cryptocurrency becomes mainstream and affects traditional banking stocks?",
            height=100
        )
    
    if st.button("Analyze Scenario Impact"):
        if scenario_text.strip():
            try:
                with st.spinner("🤖 AI is analyzing the scenario impact..."):
                    result = api_client.analyze_scenario(scenario_text, 
                                                         st.session_state.access_token)
                    
                    st.success("✅ Scenario analysis complete!")
                    
                    # Display the analysis using the new function
                    display_scenario_analysis(result)
                    
                    # Store result
                    scenario_result = {
                        'timestamp': datetime.now(),
                        'scenario': scenario_text,
                        'analysis': {
                            'narrative': result['narrative'],
                            'insights': result['insights'],
                            'recommendations': result['recommendations'],
                            'risk_assessment': result['risk_assessment']
                        }
                    }
                    st.session_state.scenario_results.append(scenario_result)
                    
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error in scenario analysis: {str(e)}")
        else:
            st.warning("Please enter a scenario to analyze.")
    
    # Show all previous analyses in a table format
    if len(st.session_state.scenario_results) > 3:
        st.subheader("📊 All Scenario Analyses")
        
        # Create a summary table
        scenario_summary = []
        for i, result in enumerate(st.session_state.scenario_results):
            scenario_summary.append({
                "ID": len(st.session_state.scenario_results) - i,
                "Date": result['timestamp'].strftime('%Y-%m-%d %H:%M'),
                "Scenario": result['scenario'][:50] + "..." if len(result['scenario']) > 50 else result['scenario'],
                "Risk Level": result['analysis']['risk_assessment'].split()[0] if result['analysis']['risk_assessment'] else "N/A"
            })
        
        df = pd.DataFrame(scenario_summary)
        st.dataframe(df, use_container_width=True)


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
