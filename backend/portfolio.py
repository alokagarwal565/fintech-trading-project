import pandas as pd
import yfinance as yf
import re
from typing import List, Dict, Tuple
import streamlit as st

class PortfolioHandler:
    def __init__(self):
        self.portfolio_data = []
        
    def parse_portfolio_input(self, portfolio_text: str) -> List[Dict]:
        """Parse portfolio input text into structured data"""
        portfolio = []
        lines = portfolio_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to parse patterns like "TCS, 10" or "TCS: 10 shares" or "TCS 10"
            patterns = [
                r'([A-Z\.]+),?\s*:?\s*(\d+)\s*shares?',
                r'([A-Z\.]+),?\s*(\d+)',
                r'([A-Z\.]+)\s+(\d+)'
            ]
            
            parsed = False
            for pattern in patterns:
                match = re.search(pattern, line.upper())
                if match:
                    ticker = match.group(1).strip()
                    quantity = int(match.group(2))
                    portfolio.append({
                        'ticker': ticker,
                        'quantity': quantity
                    })
                    parsed = True
                    break
            
            if not parsed:
                st.warning(f"Could not parse line: {line}")
        
        return portfolio
    
    def validate_and_enrich_portfolio(self, portfolio: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Validate tickers and enrich with market data"""
        validated_portfolio = []
        errors = []
        
        for item in portfolio:
            ticker = item['ticker']
            try:
                # Try to fetch ticker info
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get current price
                hist = stock.history(period="1d")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    
                    validated_portfolio.append({
                        'ticker': ticker,
                        'quantity': item['quantity'],
                        'current_price': current_price,
                        'total_value': current_price * item['quantity'],
                        'company_name': info.get('longName', ticker),
                        'sector': info.get('sector', 'Unknown'),
                        'beta': info.get('beta', 1.0)
                    })
                else:
                    errors.append(f"No price data found for {ticker}")
            except Exception as e:
                errors.append(f"Error validating {ticker}: {str(e)}")
        
        return validated_portfolio, errors
    
    def calculate_portfolio_metrics(self, portfolio: List[Dict]) -> Dict:
        """Calculate portfolio-level metrics"""
        if not portfolio:
            return {}
        
        total_value = sum(item['total_value'] for item in portfolio)
        
        # Calculate weights
        for item in portfolio:
            item['weight'] = item['total_value'] / total_value
        
        # Calculate weighted beta
        weighted_beta = sum(item['beta'] * item['weight'] for item in portfolio if item['beta'])
        
        # Sector allocation
        sectors = {}
        for item in portfolio:
            sector = item['sector']
            if sector in sectors:
                sectors[sector] += item['weight']
            else:
                sectors[sector] = item['weight']
        
        return {
            'total_value': total_value,
            'weighted_beta': weighted_beta,
            'sector_allocation': sectors,
            'num_holdings': len(portfolio)
        }
