import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

# Import our modules
from risk_profile import RiskProfiler
from portfolio import PortfolioAnalyzer
from scenario_analysis import ScenarioAnalyzer
from utils import export_to_text, export_to_pdf, validate_environment

def main():
    st.set_page_config(
        page_title="AI-Powered Risk & Scenario Advisor",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Validate environment
    if not validate_environment():
        st.error("⚠️ Missing required environment variables. Please check your .env file.")
        st.stop()
    
    # Main header
    st.title("📊 AI-Powered Risk & Scenario Advisor for Retail Investors")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
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

def show_risk_profiling():
    st.header("🎯 Risk Tolerance Assessment")
    st.write("Complete this questionnaire to understand your investment risk profile.")
    
    profiler = RiskProfiler()
    
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
            risk_profile = profiler.assess_risk_tolerance(answers)
            st.session_state.risk_profile = risk_profile
            
            # Display results
            st.success("✅ Risk Assessment Complete!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Risk Profile", risk_profile['category'])
            with col2:
                st.metric("Risk Score", f"{risk_profile['score']}/24")
            
            st.write("**Profile Description:**")
            st.write(risk_profile['description'])
            
            st.write("**Investment Recommendations:**")
            for rec in risk_profile['recommendations']:
                st.write(f"• {rec}")

def show_portfolio_analysis():
    st.header("💼 Portfolio Analysis")
    
    if st.session_state.risk_profile is None:
        st.warning("⚠️ Please complete the risk assessment first.")
        return
    
    st.write("Enter your stock holdings in natural language (e.g., 'TCS: 10, HDFC Bank: 5 shares')")
    
    analyzer = PortfolioAnalyzer()
    
    # Portfolio input
    portfolio_input = st.text_area(
        "Your Holdings:",
        placeholder="Example: TCS: 10, HDFC Bank: 5 shares, Reliance: 15, Infosys: 8",
        height=100
    )
    
    if st.button("Analyze Portfolio"):
        if portfolio_input.strip():
            with st.spinner("Fetching live market data..."):
                try:
                    portfolio_data = analyzer.parse_and_analyze_portfolio(portfolio_input)
                    st.session_state.portfolio_data = portfolio_data
                    
                    if portfolio_data['valid_holdings']:
                        st.success("✅ Portfolio analyzed successfully!")
                        
                        # Portfolio summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Value", f"₹{portfolio_data['total_value']:,.2f}")
                        with col2:
                            st.metric("Valid Holdings", len(portfolio_data['valid_holdings']))
                        with col3:
                            st.metric("Invalid Entries", len(portfolio_data['invalid_holdings']))
                        
                        # Holdings table
                        if portfolio_data['valid_holdings']:
                            st.subheader("📈 Your Holdings")
                            df = pd.DataFrame(portfolio_data['valid_holdings'])
                            st.dataframe(df, use_container_width=True)
                            
                            # Portfolio visualization
                            analyzer.visualize_portfolio(portfolio_data['valid_holdings'])
                        
                        # Invalid holdings
                        if portfolio_data['invalid_holdings']:
                            st.subheader("⚠️ Invalid Holdings")
                            for invalid in portfolio_data['invalid_holdings']:
                                st.error(f"Could not process: {invalid}")
                    
                    else:
                        st.error("❌ No valid holdings found. Please check your input format.")
                
                except Exception as e:
                    st.error(f"❌ Error analyzing portfolio: {str(e)}")
        else:
            st.warning("Please enter your portfolio holdings.")

def show_scenario_analysis():
    st.header("🔮 AI-Powered Scenario Analysis")
    
    if st.session_state.portfolio_data is None:
        st.warning("⚠️ Please analyze your portfolio first.")
        return
    
    analyzer = ScenarioAnalyzer()
    
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
            with st.spinner("AI is analyzing the scenario impact..."):
                try:
                    analysis = analyzer.analyze_scenario(
                        scenario_text,
                        st.session_state.portfolio_data['valid_holdings'],
                        st.session_state.risk_profile
                    )
                    
                    # Store results
                    result = {
                        'timestamp': datetime.now(),
                        'scenario': scenario_text,
                        'analysis': analysis
                    }
                    st.session_state.scenario_results.append(result)
                    
                    st.success("✅ Scenario analysis complete!")
                    
                    # Display analysis
                    st.subheader("🤖 AI Analysis")
                    st.write(analysis['narrative'])
                    
                    st.subheader("📊 Key Insights")
                    for insight in analysis['insights']:
                        st.write(f"• {insight}")
                    
                    st.subheader("💡 Recommendations")
                    for rec in analysis['recommendations']:
                        st.write(f"• {rec}")
                    
                    if analysis['risk_assessment']:
                        st.subheader("⚠️ Risk Assessment")
                        st.write(analysis['risk_assessment'])
                
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
    
    if not any([st.session_state.risk_profile, st.session_state.portfolio_data, st.session_state.scenario_results]):
        st.warning("⚠️ No analysis data available to export. Please complete the assessments first.")
        return
    
    st.write("Export your analysis results for future reference.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export as Text"):
            try:
                text_content = export_to_text(
                    st.session_state.risk_profile,
                    st.session_state.portfolio_data,
                    st.session_state.scenario_results
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
                pdf_content = export_to_pdf(
                    st.session_state.risk_profile,
                    st.session_state.portfolio_data,
                    st.session_state.scenario_results
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
    
    # Preview export content
    if st.checkbox("Preview Export Content"):
        st.subheader("📄 Export Preview")
        
        if st.session_state.risk_profile:
            st.write("**Risk Profile:**", st.session_state.risk_profile['category'])
        
        if st.session_state.portfolio_data:
            st.write("**Portfolio Holdings:**", len(st.session_state.portfolio_data.get('valid_holdings', [])))
        
        if st.session_state.scenario_results:
            st.write("**Scenario Analyses:**", len(st.session_state.scenario_results))

if __name__ == "__main__":
    main()
