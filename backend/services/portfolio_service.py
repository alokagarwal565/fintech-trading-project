import yfinance as yf
import re
from typing import Dict, List, Any, Tuple
from sqlmodel import Session
from backend.models.models import Portfolio, Holding, User

class PortfolioService:
    def __init__(self):
        self.indian_stock_suffixes = ['.NS', '.BO']  # NSE and BSE suffixes
        self.symbol_mapping = {
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
    
    def parse_portfolio_input(self, input_text: str) -> Tuple[List[Dict[str, Any]], List[str]]:
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
        # Clean and normalize company name
        clean_name = company_name.lower().strip()
        
        # Try exact match first
        if clean_name in self.symbol_mapping:
            return self.symbol_mapping[clean_name]
        
        # Try partial matches
        for key, symbol in self.symbol_mapping.items():
            if key in clean_name or clean_name in key:
                return symbol
        
        # If no mapping found, try the company name as is with .NS suffix
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
    
    def analyze_portfolio(self, input_text: str, user: User, session: Session) -> Dict[str, Any]:
        """
        Parse input and analyze complete portfolio, saving to database
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
                    'company_name': stock_data.get('company_name', holding.get('company', '')),
                    'symbol': symbol,
                    'quantity': holding.get('quantity', 0),
                    'current_price': round(stock_data['current_price'], 2),
                    'total_value': round(holding_value, 2),
                    'sector': stock_data.get('sector', 'Unknown'),
                    'pe_ratio': stock_data.get('pe_ratio'),
                    'dividend_yield': round(stock_data.get('dividend_yield', 0) * 100, 2) if stock_data.get('dividend_yield') else None
                })
            else:
                invalid_holdings.append(holding.get('original_entry', ''))
        
        # Add invalid entries from parsing
        invalid_holdings.extend(invalid_entries)
        
        # Save to database
        portfolio = Portfolio(
            user_id=user.id,
            name=f"Portfolio {len(user.portfolios) + 1}",
            total_value=total_value
        )
        session.add(portfolio)
        session.commit()
        session.refresh(portfolio)
        
        # Save holdings
        for holding_data in valid_holdings:
            holding = Holding(
                portfolio_id=portfolio.id,
                company_name=holding_data['company_name'],
                symbol=holding_data['symbol'],
                quantity=holding_data['quantity'],
                current_price=holding_data['current_price'],
                total_value=holding_data['total_value'],
                sector=holding_data['sector'],
                pe_ratio=holding_data['pe_ratio'],
                dividend_yield=holding_data['dividend_yield']
            )
            session.add(holding)
        
        session.commit()
        
        return {
            'portfolio_id': portfolio.id,
            'valid_holdings': valid_holdings,
            'invalid_holdings': invalid_holdings,
            'total_value': total_value
        }