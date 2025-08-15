import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import httpx
import asyncio
from typing import Optional, Dict, Any
import json
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
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
        response.raise_for_status()
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

            /* --- SCENARIO ANALYSIS CUSTOM STYLES (ADAPTED FOR DARK/LIGHT THEMES) --- */
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
    
    # Load user data on first login
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
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login")
            
            if login_submitted:
                if email and password:
                    try:
                        with st.spinner("Logging in..."):
                            result = api_client.login_user(email, password)
                            st.session_state.access_token = result["access_token"]
                            st.session_state.user_email = email
                            st.success("✅ Login successful!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Login failed: {str(e)}")
                else:
                    st.warning("Please enter both email and password.")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_full_name = st.text_input("Full Name (Optional)", key="reg_full_name")
            register_submitted = st.form_submit_button("Register")
            
            if register_submitted:
                if reg_email and reg_password:
                    try:
                        with st.spinner("Creating account..."):
                            result = api_client.register_user(reg_email, reg_password, reg_full_name)
                            st.success("✅ Account created successfully! Please login.")
                    except Exception as e:
                        st.error(f"❌ Registration failed: {str(e)}")
                else:
                    st.warning("Please enter both email and password.")

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

if __name__ == "__main__":
    main()
