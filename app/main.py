import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.risk_profile import RiskProfiler
from backend.portfolio import PortfolioHandler
from backend.scenario_analysis import ScenarioAnalyzer
from backend.explain import ExplanationGenerator
from backend.data_fetcher import DataFetcher

# Page config
st.set_page_config(
    page_title="AI Risk & Scenario Advisor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
        margin: 10px 0;
    }
    .risk-conservative { border-left-color: #28a745; }
    .risk-balanced { border-left-color: #ffc107; }
    .risk-aggressive { border-left-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'risk_answers' not in st.session_state:
        st.session_state.risk_answers = {}
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'portfolio_metrics' not in st.session_state:
        st.session_state.portfolio_metrics = {}
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI-Powered Risk & Scenario Advisor</h1>
        <p style="color: white; text-align: center; margin: 0;">
            Understand your risk tolerance • Analyze your portfolio • Get AI-powered insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    steps = [
        "🏠 Welcome",
        "📝 Risk Assessment", 
        "💼 Portfolio Input",
        "🔍 Scenario Analysis",
        "📊 Results & Insights"
    ]
    
    # Display current step
    for i, step_name in enumerate(steps, 1):
        if st.sidebar.button(step_name, key=f"nav_{i}"):
            st.session_state.step = i
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Current Step:** " + steps[st.session_state.step - 1])
    
    # Main content based on step
    if st.session_state.step == 1:
        show_welcome()
    elif st.session_state.step == 2:
        show_risk_assessment()
    elif st.session_state.step == 3:
        show_portfolio_input()
    elif st.session_state.step == 4:
        show_scenario_analysis()
    elif st.session_state.step == 5:
        show_results()

def show_welcome():
    st.markdown("## Welcome to Your Personal Investment Advisor! 🚀")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### What This Tool Does:
        
        🎯 **Risk Assessment**: Answer a few questions to understand your investment personality
        
        💼 **Portfolio Analysis**: Input your holdings and get instant insights
        
        🔍 **Scenario Planning**: See how market events might impact your investments
        
        📊 **AI-Powered Advice**: Get personalized suggestions based on your risk profile
        
        ### How It Works:
        1. **Complete the risk assessment** (5 minutes)
        2. **Enter your portfolio** (stocks you own)
        3. **Describe a scenario** (market event, news, etc.)
        4. **Get AI analysis** with actionable insights
        
        ### Sample Scenarios You Can Test:
        - "What if RBI increases interest rates by 0.5%?"
        - "How would a 15% drop in IT sector affect my portfolio?"
        - "What if crude oil prices rise by 30%?"
        - "Impact of upcoming budget announcement on my holdings"
        """)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>🎨 Built For You</h4>
            <p>No complex financial jargon. Get insights in plain English that you can act on immediately.</p>
        </div>
        
        <div class="metric-card">
            <h4>🔒 Privacy First</h4>
            <p>Your data stays with you. No accounts, no tracking, no data storage.</p>
        </div>
        
        <div class="metric-card">
            <h4>⚡ Real-Time Data</h4>
            <p>Powered by live market data and cutting-edge AI analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🚀 Start Risk Assessment", type="primary", use_container_width=True):
        st.session_state.step = 2
        st.rerun()

def show_risk_assessment():
    st.markdown("## 📝 Risk Assessment Questionnaire")
    st.markdown("Answer these questions to understand your investment personality:")
    
    profiler = RiskProfiler()
    
    with st.form("risk_assessment_form"):
        answers = {}
        
        for i, question in enumerate(profiler.questions):
            st.markdown(f"### {i+1}. {question['question']}")
            answers[question['id']] = st.radio(
                f"Select your answer:",
                question['options'],
                key=f"q_{question['id']}",
                index=0
            )
        
        submitted = st.form_submit_button("📊 Calculate My Risk Profile", type="primary")
        
        if submitted:
            st.session_state.risk_answers = answers
            risk_score, risk_profile = profiler.calculate_risk_score(answers)
            
            st.session_state.risk_score = risk_score
            st.session_state.risk_profile = risk_profile
            
            # Show results
            st.success("✅ Risk assessment completed!")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Risk Score", f"{risk_score:.0f}/100")
            
            with col2:
                st.metric("Risk Profile", risk_profile)
            
            with col3:
                color = {"Conservative": "🟢", "Balanced": "🟡", "Aggressive": "🔴"}
                st.metric("Risk Level", color.get(risk_profile, "⚪"))
            
            # Explanation
            risk_class = risk_profile.lower()
            st.markdown(f"""
            <div class="metric-card risk-{risk_class}">
                <h4>Your Risk Profile: {risk_profile}</h4>
                <p>{profiler.get_risk_description(risk_profile)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("➡️ Continue to Portfolio Input", type="primary"):
                st.session_state.step = 3
                st.rerun()

def show_portfolio_input():
    st.markdown("## 💼 Portfolio Input")
    
    if 'risk_profile' not in st.session_state:
        st.warning("⚠️ Please complete the risk assessment first!")
        if st.button("Go to Risk Assessment"):
            st.session_state.step = 2
            st.rerun()
        return
    
    st.markdown(f"**Your Risk Profile:** {st.session_state.risk_profile}")
    
    portfolio_handler = PortfolioHandler()
    data_fetcher = DataFetcher()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Enter Your Portfolio")
        st.markdown("Enter your holdings in any of these formats:")
        st.code("""TCS, 10
HDFC Bank: 5 shares
INFY 15
RELIANCE, 8 shares""")
        
        portfolio_text = st.text_area(
            "Your Portfolio Holdings:",
            height=200,
            placeholder="Enter ticker, quantity (one per line)",
            help="Supported formats: 'TCS, 10' or 'TCS: 10 shares' or 'TCS 10'"
        )
        
        if st.button("📊 Analyze Portfolio", type="primary") and portfolio_text:
            with st.spinner("Analyzing your portfolio..."):
                # Parse portfolio
                parsed_portfolio = portfolio_handler.parse_portfolio_input(portfolio_text)
                
                if parsed_portfolio:
                    # Validate and enrich
                    validated_portfolio, errors = portfolio_handler.validate_and_enrich_portfolio(parsed_portfolio)
                    
                    if errors:
                        st.error("Some issues found:")
                        for error in errors:
                            st.write(f"❌ {error}")
                    
                    if validated_portfolio:
                        # Calculate metrics
                        metrics = portfolio_handler.calculate_portfolio_metrics(validated_portfolio)
                        
                        # Store in session state
                        st.session_state.portfolio = validated_portfolio
                        st.session_state.portfolio_metrics = metrics
                        
                        st.success(f"✅ Successfully analyzed {len(validated_portfolio)} holdings!")
                        
                        # Show portfolio summary
                        st.markdown("### Portfolio Summary")
                        
                        # Metrics
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric("Total Value", f"₹{metrics['total_value']:,.0f}")
                        with col_b:
                            st.metric("Holdings", metrics['num_holdings'])
                        with col_c:
                            st.metric("Portfolio Beta", f"{metrics['weighted_beta']:.2f}")
                        with col_d:
                            avg_weight = 100 / metrics['num_holdings']
                            st.metric("Avg Weight", f"{avg_weight:.1f}%")
                        
                        # Holdings table
                        df = pd.DataFrame(validated_portfolio)
                        df['weight_pct'] = df['weight'] * 100
                        df['total_value_formatted'] = df['total_value'].apply(lambda x: f"₹{x:,.0f}")
                        
                        display_df = df[['company_name', 'ticker', 'quantity', 'current_price', 'total_value_formatted', 'weight_pct', 'sector']].copy()
                        display_df.columns = ['Company', 'Ticker', 'Qty', 'Price', 'Value', 'Weight %', 'Sector']
                        display_df['Weight %'] = display_df['Weight %'].round(1)
                        display_df['Price'] = display_df['Price'].round(2)
                        
                        st.dataframe(display_df, use_container_width=True)
                        
                        if st.button("🎯 Continue to Scenario Analysis", type="primary"):
                            st.session_state.step = 4
                            st.rerun()
    
    with col2:
        st.markdown("### Sample Portfolios")
        
        sample_portfolios = {
            "Tech Heavy": "TCS, 10\nINFY, 15\nWIPRO, 20\nHCLTECH, 8",
            "Balanced": "RELIANCE, 5\nHDFC, 10\nSBI, 15\nITC, 25\nTCS, 8",
            "Banking Focus": "HDFC, 10\nICICIBC, 15\nSBI, 20\nAXISBANK, 12"
        }
        
        for name, portfolio in sample_portfolios.items():
            if st.button(f"Load {name}", key=f"sample_{name}"):
                st.text_area("Portfolio", value=portfolio, key="loaded_portfolio", height=100)

def show_scenario_analysis():
    st.markdown("## 🔍 Scenario Analysis")
    
    if not st.session_state.portfolio:
        st.warning("⚠️ Please enter your portfolio first!")
        if st.button("Go to Portfolio Input"):
            st.session_state.step = 3
            st.rerun()
        return
    
    # Show current portfolio summary
    with st.expander("📊 Current Portfolio Summary", expanded=False):
        metrics = st.session_state.portfolio_metrics
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Value", f"₹{metrics['total_value']:,.0f}")
        with col2:
            st.metric("Holdings", metrics['num_holdings'])
        with col3:
            st.metric("Portfolio Beta", f"{metrics['weighted_beta']:.2f}")
        
        # Top holdings
        portfolio_df = pd.DataFrame(st.session_state.portfolio)
        top_holdings = portfolio_df.nlargest(5, 'total_value')
        st.markdown("**Top 5 Holdings:**")
        for _, holding in top_holdings.iterrows():
            weight = holding['weight'] * 100
            st.write(f"• {holding['company_name']}: ₹{holding['total_value']:,.0f} ({weight:.1f}%)")
    
    # Scenario input
    st.markdown("### What scenario would you like to analyze?")
    
    # Predefined scenarios
    st.markdown("**Quick Scenarios:**")
    quick_scenarios = [
        "RBI increases repo rate by 0.5%",
        "IT sector expected to decline 15% due to US recession fears",
        "Budget announcement increases infrastructure spending by 25%",
        "Crude oil prices surge 30% due to geopolitical tensions",
        "Banking sector faces stress due to rising NPAs",
        "Market correction of 20% expected in next 3 months"
    ]
    
    col1, col2 = st.columns(2)
    for i, scenario in enumerate(quick_scenarios):
        col = col1 if i % 2 == 0 else col2
        if col.button(scenario, key=f"quick_{i}", use_container_width=True):
            st.session_state.selected_scenario = scenario
    
    # Custom scenario
    st.markdown("**Or describe your own scenario:**")
    custom_scenario = st.text_area(
        "Describe the market event or scenario:",
        height=100,
        placeholder="e.g., What if the government announces new tax reforms affecting IT companies?",
        value=st.session_state.get('selected_scenario', '')
    )
    
    if st.button("🔮 Analyze This Scenario", type="primary") and custom_scenario:
        with st.spinner("🤖 AI is analyzing the scenario impact..."):
            analyzer = ScenarioAnalyzer()
            
            # Run the analysis
            analysis_result = analyzer.analyze_scenario(
                custom_scenario,
                st.session_state.portfolio,
                st.session_state.risk_profile,
                st.session_state.portfolio_metrics
            )
            
            st.session_state.scenario_analysis = analysis_result
            
            # Show results immediately
            st.markdown("### 📋 Analysis Results")
            st.markdown(analysis_result['analysis'])
            
            # Quick suggestions
            st.markdown("### 💡 Quick Actions")
            suggestions = analyzer.generate_quick_suggestions(
                custom_scenario, 
                st.session_state.risk_profile
            )
            
            for i, suggestion in enumerate(suggestions[:5], 1):
                st.markdown(f"{i}. {suggestion}")
            
            if st.button("📊 View Detailed Results", type="primary"):
                st.session_state.step = 5
                st.rerun()

def show_results():
    st.markdown("## 📊 Detailed Analysis & Insights")
    
    if 'scenario_analysis' not in st.session_state:
        st.warning("⚠️ Please complete scenario analysis first!")
        if st.button("Go to Scenario Analysis"):
            st.session_state.step = 4
            st.rerun()
        return
    
    # Portfolio overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Portfolio Overview")
        
        metrics = st.session_state.portfolio_metrics
        
        # Key metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Total Value", f"₹{metrics['total_value']:,.0f}")
        with metric_col2:
            st.metric("Risk Profile", st.session_state.risk_profile)
        with metric_col3:
            st.metric("Holdings", metrics['num_holdings'])
        with metric_col4:
            st.metric("Portfolio Beta", f"{metrics['weighted_beta']:.2f}")
    
    with col2:
        st.markdown("### 🎯 Risk Assessment")
        risk_score = st.session_state.get('risk_score', 50)
        
        # Risk gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Risk Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgreen"},
                    {'range': [40, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Portfolio composition charts
    st.markdown("### 📊 Portfolio Composition")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Holdings pie chart
        portfolio_df = pd.DataFrame(st.session_state.portfolio)
        fig_holdings = px.pie(
            portfolio_df, 
            values='total_value', 
            names='company_name',
            title="Holdings Distribution"
        )
        st.plotly_chart(fig_holdings, use_container_width=True)
    
    with chart_col2:
        # Sector allocation
        sectors = st.session_state.portfolio_metrics.get('sector_allocation', {})
        if sectors:
            sector_df = pd.DataFrame(list(sectors.items()), columns=['Sector', 'Weight'])
            fig_sectors = px.pie(
                sector_df, 
                values='Weight', 
                names='Sector',
                title="Sector Allocation"
            )
            st.plotly_chart(fig_sectors, use_container_width=True)
    
    # Scenario analysis results
    st.markdown("### 🔮 Scenario Analysis Results")
    
    analysis = st.session_state.scenario_analysis
    
    st.markdown(f"**Analyzed Scenario:** {analysis['scenario']}")
    
    # Analysis content
    with st.container():
        st.markdown(analysis['analysis'])
    
    # AI-powered explanations
    st.markdown("### 🤖 AI Insights & Explanations")
    
    explainer = ExplanationGenerator()
    
    with st.spinner("Generating personalized insights..."):
        # Portfolio explanation
        portfolio_explanation = explainer.generate_portfolio_explanation(
            st.session_state.portfolio,
            st.session_state.portfolio_metrics,
            st.session_state.risk_profile
        )
        
        # Risk profile explanation
        risk_explanation = explainer.explain_risk_profile(
            st.session_state.risk_profile,
            st.session_state.get('risk_score', 50)
        )
    
    tab1, tab2 = st.tabs(["💼 Portfolio Insights", "🎯 Risk Profile Insights"])
    
    with tab1:
        st.markdown(portfolio_explanation)
    
    with tab2:
        st.markdown(risk_explanation)
    
    # Export options
    st.markdown("### 📥 Export Your Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Portfolio Summary", use_container_width=True):
            # Create downloadable portfolio summary
            portfolio_df = pd.DataFrame(st.session_state.portfolio)
            csv = portfolio_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="portfolio_summary.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📝 Save Analysis Report", use_container_width=True):
            # Create text report
            report = f"""
            PORTFOLIO ANALYSIS REPORT
            Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            RISK PROFILE: {st.session_state.risk_profile}
            RISK SCORE: {st.session_state.get('risk_score', 'N/A')}/100
            
            SCENARIO ANALYZED: {analysis['scenario']}
            
            ANALYSIS:
            {analysis['analysis']}
            
            PORTFOLIO INSIGHTS:
            {portfolio_explanation}
            """
            
            st.download_button(
                label="Download Report",
                data=report,
                file_name="investment_analysis_report.txt",
                mime="text/plain"
            )
    
    with col3:
        if st.button("🔄 Start New Analysis", use_container_width=True):
            # Reset session state
            for key in list(st.session_state.keys()):
                if key != 'step':
                    del st.session_state[key]
            st.session_state.step = 1
            st.rerun()

if __name__ == "__main__":
    main()
