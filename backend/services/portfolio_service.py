import yfinance as yf
import re
from typing import Dict, List, Any, Tuple
from sqlmodel import Session
from backend.models.models import Portfolio, Holding, User
import plotly.express as px
import pandas as pd
from backend.utils.retry import retry_with_backoff
from backend.utils.logger import app_logger
import time

class PortfolioService:
    def __init__(self):
        # A comprehensive mapping of common Indian company names to NSE symbols.
        # This list can be expanded to include more stocks.
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
        Parses a natural-language text input for portfolio holdings.
        
        Args:
            input_text (str): The raw text input (e.g., "100 shares of Reliance, 50 Infosys").
            
        Returns:
            Tuple[List[Dict[str, Any]], List[str]]:
                - A list of successfully parsed holdings (company name + quantity).
                - A list of entries that could not be parsed.
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
        Converts a company name into an official stock ticker symbol.
        
        Args:
            company_name (str): The name of the company.
            
        Returns:
            str: The official stock ticker symbol (e.g., "TCS.NS").
        """
        # Clean and normalize company name
        clean_name = company_name.lower().strip()
        
        # Try exact match first from the pre-defined dictionary
        if clean_name in self.symbol_mapping:
            return self.symbol_mapping[clean_name]
        
        # Try partial matches
        for key, symbol in self.symbol_mapping.items():
            if key in clean_name or clean_name in key:
                return symbol
        
        # If no mapping found, try the company name as is with .NS suffix
        potential_symbol = clean_name.upper().replace(' ', '') + '.NS'
        return potential_symbol
    
    @retry_with_backoff(max_retries=3, base_delay=1.0, exceptions=(Exception,))
    def fetch_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetches current stock data for a given symbol using yfinance with retry logic.
        
        Args:
            symbol (str): The stock ticker symbol.
            
        Returns:
            Dict[str, Any]: A dictionary containing stock information, or an error if invalid.
        """
        try:
            app_logger.info(f"Fetching stock data for symbol: {symbol}")
            start_time = time.time()
            
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not current_price:
                # Try to get from history if direct price is not available
                hist = stock.history(period="1d")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
            
            # Validate that we got a price
            if not current_price or current_price <= 0:
                raise ValueError(f"No valid price found for {symbol}")
            
            fetch_time = time.time() - start_time
            app_logger.info(f"Successfully fetched data for {symbol} in {fetch_time:.2f}s")
            
            # Retrieve specific metrics required by the application
            return {
                'symbol': symbol,
                'current_price': current_price,
                'company_name': info.get('longName', symbol),
                'currency': info.get('currency', 'INR'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'sector': info.get('sector'),
                'valid': True
            }
        except Exception as e:
            app_logger.error(f"Failed to fetch stock data for {symbol}: {str(e)}")
            # Handle cases where the stock symbol is invalid or data cannot be fetched
            return {
                'symbol': symbol,
                'error': str(e),
                'valid': False
            }

    def get_portfolio_metrics(self, valid_holdings: List[Dict[str, Any]], total_value: float) -> Dict[str, Any]:
        """
        Calculates key portfolio-level metrics.
        
        Args:
            valid_holdings (List[Dict[str, Any]]): A list of valid holdings with fetched data.
            total_value (float): The total value of the portfolio.

        Returns:
            Dict[str, Any]: A dictionary of calculated metrics.
        """
        if not valid_holdings:
            return {
                'holdings_count': 0,
                'average_pe_ratio': None,
                'average_dividend_yield': None,
                'concentration_percentage': 0.0
            }

        # Calculate weighted averages for P/E ratio and dividend yield
        total_pe_sum = 0
        total_dividend_yield_sum = 0
        largest_holding_value = 0

        for holding in valid_holdings:
            holding_value = holding.get('total_value', 0)
            if holding.get('pe_ratio'):
                total_pe_sum += holding.get('pe_ratio') * holding_value
            if holding.get('dividend_yield'):
                total_dividend_yield_sum += holding.get('dividend_yield') * holding_value
            
            if holding_value > largest_holding_value:
                largest_holding_value = holding_value

        # Calculate averages, handling division by zero
        average_pe = (total_pe_sum / total_value) if total_value > 0 else None
        average_dividend_yield = (total_dividend_yield_sum / total_value) if total_value > 0 else None
        
        # Calculate concentration
        concentration = (largest_holding_value / total_value) * 100 if total_value > 0 else 0.0

        return {
            'holdings_count': len(valid_holdings),
            'average_pe_ratio': round(average_pe, 2) if average_pe else None,
            'average_dividend_yield': round(average_dividend_yield, 2) if average_dividend_yield else None,
            'concentration_percentage': round(concentration, 2)
        }


    def visualize_portfolio(self, valid_holdings: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generates interactive plots for portfolio visualization using plotly.express.

        Args:
            valid_holdings (List[Dict[str, Any]]): A list of valid holdings with fetched data.
            
        Returns:
            Dict[str, str]: A dictionary of plots in JSON format.
        """
        if not valid_holdings:
            return {
                "pie_chart": "{}",
                "sector_bar_chart": "{}",
                "holdings_bar_chart": "{}"
            }

        df = pd.DataFrame(valid_holdings)

        # Pie chart for portfolio composition
        pie_fig = px.pie(
            df,
            values='total_value',
            names='company_name',
            title='Portfolio Composition',
            hole=0.3
        )
        pie_fig.update_traces(textinfo='percent+label', marker_line_color='rgb(0,0,0)', marker_line_width=1)
        
        # Bar chart for sector allocation
        sector_allocation = df.groupby('sector')['total_value'].sum().reset_index()
        sector_fig = px.bar(
            sector_allocation,
            x='sector',
            y='total_value',
            title='Sector Allocation'
        )
        sector_fig.update_traces(marker_color='#1f77b4', selector=dict(type='bar'))
        sector_fig.update_layout(xaxis_title="Sector", yaxis_title="Total Value")

        # Bar chart for individual holding values
        holdings_fig = px.bar(
            df,
            x='company_name',
            y='total_value',
            title='Individual Holding Values'
        )
        holdings_fig.update_traces(marker_color='#2ca02c', selector=dict(type='bar'))
        holdings_fig.update_layout(xaxis_title="Company", yaxis_title="Total Value")

        return {
            "pie_chart": pie_fig.to_json(),
            "sector_bar_chart": sector_fig.to_json(),
            "holdings_bar_chart": holdings_fig.to_json()
        }

    def analyze_portfolio(self, input_text: str, user: User, session: Session) -> Dict[str, Any]:
        """
        Orchestrates the full portfolio analysis flow: parsing input, fetching data,
        calculating metrics, generating visualizations, and saving to the database.
        
        Args:
            input_text (str): The natural language text input for the portfolio.
            user (User): The authenticated user object.
            session (Session): The database session.
            
        Returns:
            Dict[str, Any]: A comprehensive dictionary with portfolio details, metrics, and plots.
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
                
                # Append stock data to valid holdings list
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
        
        # Add any entries that couldn't be parsed
        invalid_holdings.extend(invalid_entries)

        # Calculate metrics and generate visualizations
        metrics = self.get_portfolio_metrics(valid_holdings, total_value)
        visualizations = self.visualize_portfolio(valid_holdings)
        
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
            'total_value': total_value,
            'metrics': metrics,
            'visualizations': visualizations
        }
