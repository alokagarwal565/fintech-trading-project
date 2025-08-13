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
    
    def assess_risk_profile(self, answers: list, token: str) -> Dict[str, Any]:
        data = {"answers": answers}
        response = self.client.post(
            f"{self.base_url}/api/v1/risk-profile",
            json=data,
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

# Initialize API client
api_client = APIClient(API_BASE_URL)

def main():
    st.set_page_config(
        page_title="AI-Powered Risk & Scenario Advisor",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
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
            except Exception as e:
                st.error(f"❌ Error assessing risk profile: {str(e)}")

def show_portfolio_analysis():
    st.header("💼 Portfolio Analysis")
    
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
                    
                    if result['valid_holdings']:
                        st.success("✅ Portfolio analyzed successfully!")
                        
                        # Display portfolio summary
                        st.subheader("Portfolio Summary")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Value", f"₹{result['total_value']:,.2f}")
                        with col2:
                            st.metric("Total Holdings", result['metrics']['holdings_count'])
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
                    
                    else:
                        st.error("❌ No valid holdings found. Please check your input format.")
                
            except Exception as e:
                st.error(f"❌ Error analyzing portfolio: {str(e)}")
        else:
            st.warning("Please enter your portfolio holdings.")

def show_scenario_analysis():
    st.header("🔮 AI-Powered Scenario Analysis")
    
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
                    result = api_client.analyze_scenario(scenario_text, st.session_state.access_token)
                    
                    st.success("✅ Scenario analysis complete!")
                    
                    # Display analysis
                    st.subheader("🤖 AI Analysis")
                    st.write(result['narrative'])
                    
                    st.subheader("📊 Key Insights")
                    for insight in result['insights']:
                        st.write(f"• {insight}")
                    
                    st.subheader("💡 Recommendations")
                    for rec in result['recommendations']:
                        st.write(f"• {rec}")
                    
                    if result['risk_assessment']:
                        st.subheader("⚠️ Risk Assessment")
                        st.write(result['risk_assessment'])
                    
                    # Store in session state for display
                    scenario_result = {
                        'timestamp': datetime.now(),
                        'scenario': scenario_text,
                        'analysis': result
                    }
                    st.session_state.scenario_results.append(scenario_result)
                
            except Exception as e:
                st.error(f"❌ Error in scenario analysis: {str(e)}")
        else:
            st.warning("Please enter a scenario to analyze.")
    
    # Show previous analyses
    if st.session_state.scenario_results:
        st.subheader("📋 Previous Analyses")
        for i, result in enumerate(reversed(st.session_state.scenario_results[-5:])):
            with st.expander(f"Analysis {len(st.session_state.scenario_results)-i}: {result['scenario'][:50]}..."):
                st.write(f"**Analyzed on:** {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write("**Scenario:**", result['scenario'])
                st.write("**Analysis:**", result['analysis']['narrative'])

def show_export_options():
    st.header("📋 Export Your Analysis Results")
    
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
            except Exception as e:
                st.error(f"❌ Error generating PDF export: {str(e)}")

if __name__ == "__main__":
    main()

