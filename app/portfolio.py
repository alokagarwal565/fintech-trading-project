import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from typing import Dict, List, Any

class PortfolioAnalyzer:
    def __init__(self):
        self.indian_stock_suffixes = ['.NS', '.BO']  # NSE and BSE suffixes
    
    def parse_portfolio_input(self, input_text: str) -> tuple[List[Dict[str, Any]], List[str]]:
        """
        Parse natural language portfolio input
        """
        holdings = []
        invalid_entries = []
        
        # Split by commas and clean
        entries = [entry.strip() for entry in input_text.split(',')]
        
        for entry in entries:
            if not entry:
                continue
                
            # Try different parsing patterns
            patterns = [
                r'^([A-Za-z\s&]+):\s*(\d+)\s*shares?$',  # "Company: X shares"
                r'^([A-Za-z\s&]+):\s*(\d+)$',            # "Company: X"
                r'^(\d+)\s+([A-Za-z\s&]+)$',             # "X Company"
                r'^([A-Za-z\s&]+)\s+(\d+)$'              # "Company X"
            ]
            
            parsed = False
            for pattern in patterns:
                match = re.match(pattern, entry.strip())
                if match:
                    if pattern.startswith('^(\\d+)'):
                        # Quantity comes first
                        quantity, company = match.groups()
                    else:
                        # Company comes first
                        company, quantity = match.groups()
                    
                    holdings.append({
                        'company': company.strip(),
                        'quantity': int(quantity),
                        'original_entry': entry
                    })
                    parsed = True
                    break
            
            if not parsed:
                invalid_entries.append(entry)
        
        return holdings, invalid_entries
    
    def get_stock_symbol(self, company_name: str) -> str:
        """
        Convert company name to stock symbol
        """
        # Common Indian stock symbol mappings
        symbol_mapping = {
            'tcs': 'TCS.NS',
            'tata consultancy services': 'TCS.NS',
            'hdfc bank': 'HDFCBANK.NS',
            'hdfc': 'HDFCBANK.NS',
            'reliance': 'RELIANCE.NS',
            'reliance industries': 'RELIANCE.NS',
            'infosys': 'INFY.NS',
            'wipro': 'WIPRO.NS',
            'icici bank': 'ICICIBANK.NS',
            'icici': 'ICICIBANK.NS',
            'sbi': 'SBIN.NS',
            'state bank of india': 'SBIN.NS',
            'bharti airtel': 'BHARTIARTL.NS',
            'airtel': 'BHARTIARTL.NS',
            'itc': 'ITC.NS',
            'larsen & toubro': 'LT.NS',
            'l&t': 'LT.NS',
            'asian paints': 'ASIANPAINT.NS',
            'bajaj finance': 'BAJFINANCE.NS',
            'maruti suzuki': 'MARUTI.NS',
            'maruti': 'MARUTI.NS',
            'hul': 'HINDUNILVR.NS',
            'hindustan unilever': 'HINDUNILVR.NS',
            'kotak mahindra bank': 'KOTAKBANK.NS',
            'kotak': 'KOTAKBANK.NS',
            'axis bank': 'AXISBANK.NS',
            'axis': 'AXISBANK.NS',
            'mahindra & mahindra': 'M&M.NS',
            'm&m': 'M&M.NS',
            'sun pharma': 'SUNPHARMA.NS',
            'dr reddy': 'DRREDDY.NS',
            'tech mahindra': 'TECHM.NS',
            'hcl technologies': 'HCLTECH.NS',
            'hcl tech': 'HCLTECH.NS',
            'titan': 'TITAN.NS',
            'nestle': 'NESTLEIND.NS',
            'bajaj auto': 'BAJAJ-AUTO.NS',
            'power grid': 'POWERGRID.NS',
            'ntpc': 'NTPC.NS',
            'coal india': 'COALINDIA.NS',
            'ongc': 'ONGC.NS',
            'ioc': 'IOC.NS',
            'indian oil': 'IOC.NS',
            'bpcl': 'BPCL.NS',
            'tata steel': 'TATASTEEL.NS',
            'jsw steel': 'JSWSTEEL.NS',
            'ultratech cement': 'ULTRACEMCO.NS',
            'grasim': 'GRASIM.NS',
            'adani enterprises': 'ADANIENT.NS',
            'adani ports': 'ADANIPORTS.NS',
            'eicher motors': 'EICHERMOT.NS'
        }
        
        # Clean and normalize company name
        clean_name = company_name.lower().strip()
        
        # Try exact match first
        if clean_name in symbol_mapping:
            return symbol_mapping[clean_name]
        
        # Try partial matches
        for key, symbol in symbol_mapping.items():
            if key in clean_name or clean_name in key:
                return symbol
        
        # If no mapping found, try the company name as is with .NS suffix
        # Convert to uppercase and add .NS
        potential_symbol = clean_name.upper().replace(' ', '') + '.NS'
        return potential_symbol
    
    def fetch_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current stock data from yFinance
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not current_price:
                # Try to get from history
                hist = stock.history(period="1d")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'company_name': info.get('longName', symbol),
                'currency': info.get('currency', 'INR'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'sector': info.get('sector'),
                'valid': True
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'error': str(e),
                'valid': False
            }
    
    def parse_and_analyze_portfolio(self, input_text: str) -> Dict[str, Any]:
        """
        Parse input and analyze complete portfolio
        """
        # Parse input
        holdings, invalid_entries = self.parse_portfolio_input(input_text)
        
        valid_holdings = []
        invalid_holdings = []
        total_value = 0
        
        # Process each holding
        for holding in holdings:
            symbol = self.get_stock_symbol(holding.get('company', ''))
            stock_data = self.fetch_stock_data(symbol)
            
            if stock_data['valid'] and stock_data.get('current_price'):
                holding_value = holding.get('quantity', 0) * stock_data['current_price']
                total_value += holding_value
                
                valid_holdings.append({
                    'Company': stock_data.get('company_name', holding.get('company', '')),
                    'Symbol': symbol,
                    'Quantity': holding.get('quantity', 0),
                    'Current Price (₹)': round(stock_data['current_price'], 2),
                    'Total Value (₹)': round(holding_value, 2),
                    'Sector': stock_data.get('sector', 'Unknown'),
                    'P/E Ratio': stock_data.get('pe_ratio'),
                    'Dividend Yield (%)': round(stock_data.get('dividend_yield', 0) * 100, 2) if stock_data.get('dividend_yield') else None
                })
            else:
                invalid_holdings.append(holding.get('original_entry', ''))
        
        # Add invalid entries from parsing
        invalid_holdings.extend(invalid_entries)
        
        return {
            'valid_holdings': valid_holdings,
            'invalid_holdings': invalid_holdings,
            'total_value': total_value,
            'analysis_timestamp': pd.Timestamp.now()
        }
    
    def visualize_portfolio(self, holdings: List[Dict]) -> None:
        """
        Create portfolio visualizations
        """
        if not holdings:
            return
        
        df = pd.DataFrame(holdings)
        
        # Portfolio composition pie chart
        fig_pie = px.pie(
            df, 
            values='Total Value (₹)', 
            names='Company',
            title="Portfolio Composition by Value"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Sector allocation
        if 'Sector' in df.columns:
            sector_data = df.groupby('Sector')['Total Value (₹)'].sum().reset_index()
            if len(sector_data) > 1:
                fig_sector = px.bar(
                    sector_data,
                    x='Sector',
                    y='Total Value (₹)',
                    title="Portfolio Allocation by Sector"
                )
                st.plotly_chart(fig_sector, use_container_width=True)
        
        # Holdings value bar chart
        fig_bar = px.bar(
            df,
            x='Company',
            y='Total Value (₹)',
            title="Individual Holdings Value",
            text='Total Value (₹)'
        )
        fig_bar.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    def get_portfolio_metrics(self, holdings: List[Dict]) -> Dict[str, Any]:
        """
        Calculate portfolio metrics
        """
        if not holdings:
            return {}
        
        df = pd.DataFrame(holdings)
        
        # Basic metrics
        total_value = df['Total Value (₹)'].sum()
        avg_pe = df['P/E Ratio'].mean() if 'P/E Ratio' in df.columns else None
        avg_dividend_yield = df['Dividend Yield (%)'].mean() if 'Dividend Yield (%)' in df.columns else None
        
        # Concentration analysis
        largest_holding_pct = (df['Total Value (₹)'].max() / total_value) * 100
        top_3_values = df['Total Value (₹)'].nlargest(3)
        top_3_holdings_pct = (top_3_values.sum() / total_value) * 100
        
        # Sector diversification
        sector_count = df['Sector'].nunique() if 'Sector' in df.columns else 0
        
        return {
            'total_value': total_value,
            'number_of_holdings': len(holdings),
            'average_pe_ratio': avg_pe,
            'average_dividend_yield': avg_dividend_yield,
            'largest_holding_percentage': largest_holding_pct,
            'top_3_holdings_percentage': top_3_holdings_pct,
            'sector_diversification': sector_count
        }
