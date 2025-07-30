import yfinance as yf
import pandas as pd
from typing import Dict, List
import streamlit as st

class DataFetcher:
    def __init__(self):
        pass
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_stock_info(_self, ticker: str) -> Dict:
        """Get comprehensive stock information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1mo")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            return {
                'ticker': ticker,
                'current_price': current_price,
                'previous_close': prev_close,
                'change_percent': change_pct,
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'beta': info.get('beta', 1.0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'volume': hist['Volume'].iloc[-1] if not hist.empty else 0
            }
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def get_market_indices(self) -> Dict:
        """Get major market indices data"""
        indices = {
            '^NSEI': 'NIFTY 50',
            '^BSESN': 'SENSEX',
            '^IXIC': 'NASDAQ',
            '^GSPC': 'S&P 500'
        }
        
        market_data = {}
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = ((current - prev) / prev) * 100
                    market_data[name] = {
                        'value': current,
                        'change_percent': change
                    }
            except:
                continue
        
        return market_data
