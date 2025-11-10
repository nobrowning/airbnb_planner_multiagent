import requests
import json
import os
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Directory to store finance search results
FINANCE_DIR = "finance"

# Initialize FastMCP server
mcp = FastMCP("finance-assistant")

def get_serpapi_key() -> str:
    """Get SerpAPI key from environment variable."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("SERPAPI_KEY environment variable is required")
    return api_key

@mcp.tool()
def lookup_stock(
    symbol: str,
    exchange: Optional[str] = None,
    window: Optional[str] = None,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Lookup stock information and current price using Google Finance.
    
    Args:
        symbol: Stock symbol (e.g., 'GOOGL', 'AAPL', 'TSLA')
        exchange: Optional exchange (e.g., 'NASDAQ', 'NYSE', 'LSE')
        window: Time window for historical data ('1D', '5D', '1M', '6M', '1Y', '5Y', 'MAX')
        language: Language code (default: 'en')
        
    Returns:
        Dict containing stock information, price, and historical data
    """
    
    try:
        api_key = get_serpapi_key()
        
        # Format query
        query = symbol.upper()
        if exchange:
            query = f"{symbol.upper()}:{exchange.upper()}"
        
        # Build search parameters
        params = {
            "engine": "google_finance",
            "api_key": api_key,
            "q": query,
            "hl": language
        }
        
        # Add window parameter if specified
        if window:
            params["window"] = window.upper()
        
        # Make API request
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        stock_data = response.json()
        
        # Create search identifier
        search_id = f"stock_{symbol.lower()}"
        if exchange:
            search_id += f"_{exchange.lower()}"
        search_id += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(FINANCE_DIR, exist_ok=True)
        
        # Process and store stock results
        processed_results = {
            "search_metadata": {
                "search_id": search_id,
                "symbol": symbol.upper(),
                "exchange": exchange,
                "query": query,
                "window": window,
                "search_timestamp": datetime.now().isoformat(),
                "search_type": "stock"
            },
            "summary": stock_data.get("summary", {}),
            "graph": stock_data.get("graph", []),
            "knowledge_graph": stock_data.get("knowledge_graph", {}),
            "news_results": stock_data.get("news_results", []),
            "financials": stock_data.get("financials", []),
            "key_events": stock_data.get("key_events", []),
            "discover_more": stock_data.get("discover_more", [])
        }
        
        # Save results to file
        file_path = os.path.join(FINANCE_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_results, f, indent=2)
        
        print(f"Stock lookup results saved to: {file_path}")
        
        # Return summary for the user
        summary = processed_results.get("summary", {})
        return {
            "search_id": search_id,
            "symbol": symbol.upper(),
            "company_name": summary.get("title", "N/A"),
            "exchange": summary.get("exchange", exchange or "N/A"),
            "current_price": summary.get("extracted_price", 0),
            "currency": summary.get("currency", "USD"),
            "price_movement": summary.get("price_movement", {}),
            "market_status": summary.get("market", {}),
            "last_updated": datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: float = 1.0,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Convert currency using Google Finance exchange rates.
    
    Args:
        from_currency: Source currency code (e.g., 'USD', 'EUR', 'GBP')
        to_currency: Target currency code (e.g., 'USD', 'EUR', 'GBP')
        amount: Amount to convert (default: 1.0)
        language: Language code (default: 'en')
        
    Returns:
        Dict containing conversion rate and converted amount
    """
    
    try:
        api_key = get_serpapi_key()
        
        # Format currency pair query
        query = f"{from_currency.upper()}-{to_currency.upper()}"
        
        # Build search parameters
        params = {
            "engine": "google_finance",
            "api_key": api_key,
            "q": query,
            "hl": language
        }
        
        # Make API request
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        currency_data = response.json()
        
        # Create search identifier
        search_id = f"currency_{from_currency.lower()}_{to_currency.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(FINANCE_DIR, exist_ok=True)
        
        # Process and store currency results
        processed_results = {
            "search_metadata": {
                "search_id": search_id,
                "from_currency": from_currency.upper(),
                "to_currency": to_currency.upper(),
                "amount": amount,
                "query": query,
                "search_timestamp": datetime.now().isoformat(),
                "search_type": "currency"
            },
            "summary": currency_data.get("summary", {}),
            "graph": currency_data.get("graph", []),
            "markets": currency_data.get("markets", {})
        }
        
        # Save results to file
        file_path = os.path.join(FINANCE_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_results, f, indent=2)
        
        print(f"Currency conversion results saved to: {file_path}")
        
        # Extract conversion rate
        summary = processed_results.get("summary", {})
        exchange_rate = summary.get("extracted_price", 0)
        
        if exchange_rate == 0:
            # Try to find rate in markets data
            markets = currency_data.get("markets", {})
            for region, currencies in markets.items():
                if isinstance(currencies, list) and region == "currencies":
                    for currency_pair in currencies:
                        if currency_pair.get("stock") == query:
                            exchange_rate = currency_pair.get("price", 0)
                            break
        
        converted_amount = amount * exchange_rate
        
        return {
            "search_id": search_id,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "original_amount": amount,
            "exchange_rate": exchange_rate,
            "converted_amount": converted_amount,
            "rate_change": summary.get("price_movement", {}),
            "last_updated": datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_market_overview(language: str = "en") -> Dict[str, Any]:
    """
    Get overview of major markets including stocks, currencies, and crypto.
    
    Args:
        language: Language code (default: 'en')
        
    Returns:
        Dict containing market overview data
    """
    
    try:
        api_key = get_serpapi_key()
        
        # Use a major stock to get market overview
        params = {
            "engine": "google_finance",
            "api_key": api_key,
            "q": "GOOGL:NASDAQ",
            "hl": language
        }
        
        # Make API request
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        market_data = response.json()
        
        # Create search identifier
        search_id = f"market_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(FINANCE_DIR, exist_ok=True)
        
        # Process markets data
        markets = market_data.get("markets", {})
        
        processed_results = {
            "search_metadata": {
                "search_id": search_id,
                "search_timestamp": datetime.now().isoformat(),
                "search_type": "market_overview"
            },
            "markets": markets
        }
        
        # Save results to file
        file_path = os.path.join(FINANCE_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_results, f, indent=2)
        
        print(f"Market overview results saved to: {file_path}")
        
        # Return organized market data
        result = {
            "search_id": search_id,
            "us_markets": markets.get("us", [])[:5],  # Top 5 US indices
            "european_markets": markets.get("europe", [])[:5],  # Top 5 European indices
            "asian_markets": markets.get("asia", [])[:5],  # Top 5 Asian indices
            "major_currencies": markets.get("currencies", [])[:10],  # Top 10 currency pairs
            "cryptocurrencies": markets.get("crypto", [])[:10],  # Top 10 cryptos
            "futures": markets.get("futures", [])[:5],  # Top 5 futures
            "last_updated": datetime.now().isoformat()
        }
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_finance_details(search_id: str) -> str:
    """
    Get detailed information about a specific finance search.
    
    Args:
        search_id: The search ID returned from lookup_stock, convert_currency, or get_market_overview
        
    Returns:
        JSON string with detailed finance information
    """
    
    file_path = os.path.join(FINANCE_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No finance search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            finance_data = json.load(f)
        return json.dumps(finance_data, indent=2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading finance data for {search_id}: {str(e)}"

@mcp.tool()
def filter_stocks_by_price_movement(
    search_id: str,
    min_percentage: Optional[float] = None,
    max_percentage: Optional[float] = None,
    movement_type: Optional[str] = None
) -> str:
    """
    Filter stocks from market overview by price movement criteria.
    
    Args:
        search_id: The search ID returned from get_market_overview
        min_percentage: Minimum percentage change filter
        max_percentage: Maximum percentage change filter  
        movement_type: Filter by movement type ('Up', 'Down', or None for both)
        
    Returns:
        JSON string with filtered results
    """
    
    file_path = os.path.join(FINANCE_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No finance search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            finance_data = json.load(f)
        
        def movement_filter(item):
            price_movement = item.get("price_movement", {})
            percentage = abs(price_movement.get("percentage", 0))
            movement = price_movement.get("movement", "")
            
            # Check percentage filters
            if min_percentage is not None and percentage < min_percentage:
                return False
            if max_percentage is not None and percentage > max_percentage:
                return False
            
            # Check movement type filter
            if movement_type and movement != movement_type:
                return False
                
            return True
        
        markets = finance_data.get("markets", {})
        filtered_markets = {}
        
        for region, items in markets.items():
            if isinstance(items, list):
                filtered_items = [item for item in items if movement_filter(item)]
                if filtered_items:
                    filtered_markets[region] = filtered_items
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "min_percentage": min_percentage,
                "max_percentage": max_percentage,
                "movement_type": movement_type
            },
            "filtered_markets": filtered_markets,
            "total_filtered": sum(len(items) for items in filtered_markets.values())
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing finance data for {search_id}: {str(e)}"

@mcp.tool()
def get_historical_data(
    symbol: str,
    exchange: Optional[str] = None,
    window: str = "1Y",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Get historical price data for a stock with specific time window.
    
    Args:
        symbol: Stock symbol (e.g., 'GOOGL', 'AAPL', 'TSLA')
        exchange: Optional exchange (e.g., 'NASDAQ', 'NYSE')
        window: Time window ('1D', '5D', '1M', '6M', '1Y', '5Y', 'MAX')
        language: Language code (default: 'en')
        
    Returns:
        Dict containing historical price data and key events
    """
    
    try:
        api_key = get_serpapi_key()
        
        # Format query
        query = symbol.upper()
        if exchange:
            query = f"{symbol.upper()}:{exchange.upper()}"
        
        # Build search parameters
        params = {
            "engine": "google_finance",
            "api_key": api_key,
            "q": query,
            "window": window.upper(),
            "hl": language
        }
        
        # Make API request
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        historical_data = response.json()
        
        # Create search identifier
        search_id = f"historical_{symbol.lower()}"
        if exchange:
            search_id += f"_{exchange.lower()}"
        search_id += f"_{window.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(FINANCE_DIR, exist_ok=True)
        
        # Process historical data
        graph_data = historical_data.get("graph", [])
        key_events = historical_data.get("key_events", [])
        
        processed_results = {
            "search_metadata": {
                "search_id": search_id,
                "symbol": symbol.upper(),
                "exchange": exchange,
                "window": window.upper(),
                "search_timestamp": datetime.now().isoformat(),
                "search_type": "historical"
            },
            "summary": historical_data.get("summary", {}),
            "graph": graph_data,
            "key_events": key_events,
            "data_points": len(graph_data)
        }
        
        # Save results to file
        file_path = os.path.join(FINANCE_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_results, f, indent=2)
        
        print(f"Historical data results saved to: {file_path}")
        
        # Calculate basic statistics
        prices = [point.get("price", 0) for point in graph_data if point.get("price")]
        
        statistics = {}
        if prices:
            statistics = {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "price_range": max(prices) - min(prices),
                "total_data_points": len(prices)
            }
        
        return {
            "search_id": search_id,
            "symbol": symbol.upper(),
            "window": window.upper(),
            "statistics": statistics,
            "key_events_count": len(key_events),
            "has_data": len(graph_data) > 0,
            "last_updated": datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.resource("finance://searches")
def get_finance_searches() -> str:
    """
    List all available finance searches.
    
    This resource provides a list of all saved finance searches including stocks, currencies, and market data.
    """
    searches = []
    
    if os.path.exists(FINANCE_DIR):
        for filename in os.listdir(FINANCE_DIR):
            if filename.endswith('.json'):
                search_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(FINANCE_DIR, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        metadata = data.get('search_metadata', {})
                        searches.append({
                            'search_id': search_id,
                            'type': metadata.get('search_type', 'unknown'),
                            'symbol': metadata.get('symbol', 'N/A'),
                            'query': metadata.get('query', 'N/A'),
                            'search_time': metadata.get('search_timestamp', 'N/A')
                        })
                except (json.JSONDecodeError, KeyError):
                    continue
    
    # Sort by search time (most recent first)
    searches.sort(key=lambda x: x['search_time'], reverse=True)
    
    content = "# Finance Searches\n\n"
    if searches:
        content += f"Total searches: {len(searches)}\n\n"
        
        # Group by search type
        search_types = {}
        for search in searches:
            search_type = search['type']
            if search_type not in search_types:
                search_types[search_type] = []
            search_types[search_type].append(search)
        
        for search_type, type_searches in search_types.items():
            content += f"## {search_type.title()} Searches ({len(type_searches)})\n\n"
            
            for search in type_searches[:10]:  # Show max 10 per type
                content += f"### {search['search_id']}\n"
                content += f"- **Type**: {search['type']}\n"
                if search['symbol'] != 'N/A':
                    content += f"- **Symbol**: {search['symbol']}\n"
                content += f"- **Query**: {search['query']}\n"
                content += f"- **Search Time**: {search['search_time']}\n\n"
                content += "---\n\n"
            
            if len(type_searches) > 10:
                content += f"... and {len(type_searches) - 10} more {search_type} searches\n\n"
    else:
        content += "No finance searches found.\n\n"
        content += "Use the following tools to search for financial data:\n"
        content += "- `lookup_stock` for stock information\n"
        content += "- `convert_currency` for currency conversion\n"
        content += "- `get_market_overview` for market data\n"
        content += "- `get_historical_data` for historical prices\n"
    
    return content

@mcp.resource("finance://{search_id}")
def get_finance_search_details(search_id: str) -> str:
    """
    Get detailed information about a specific finance search.
    
    Args:
        search_id: The finance search ID to retrieve details for
    """
    file_path = os.path.join(FINANCE_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"# Finance Search Not Found: {search_id}\n\nNo finance search found with this ID."
    
    try:
        with open(file_path, 'r') as f:
            finance_data = json.load(f)
        
        metadata = finance_data.get('search_metadata', {})
        search_type = metadata.get('search_type', 'unknown')
        
        content = f"# Finance Search: {search_id}\n\n"
        content += f"## Search Details\n"
        content += f"- **Type**: {search_type.title()}\n"
        content += f"- **Search Time**: {metadata.get('search_timestamp', 'N/A')}\n"
        
        if search_type == 'stock':
            content += f"- **Symbol**: {metadata.get('symbol', 'N/A')}\n"
            content += f"- **Exchange**: {metadata.get('exchange', 'N/A')}\n"
            if metadata.get('window'):
                content += f"- **Time Window**: {metadata.get('window')}\n"
            
            # Summary information
            summary = finance_data.get('summary', {})
            if summary:
                content += f"\n## Current Stock Information\n"
                content += f"- **Company**: {summary.get('title', 'N/A')}\n"
                content += f"- **Price**: {summary.get('price', 'N/A')}\n"
                content += f"- **Currency**: {summary.get('currency', 'N/A')}\n"
                
                price_movement = summary.get('price_movement', {})
                if price_movement:
                    content += f"- **Price Change**: {price_movement.get('movement', 'N/A')} {price_movement.get('percentage', 0):.2f}% ({price_movement.get('value', 'N/A')})\n"
            
            # Key statistics
            knowledge_graph = finance_data.get('knowledge_graph', {})
            key_stats = knowledge_graph.get('key_stats', {})
            stats = key_stats.get('stats', [])
            if stats:
                content += f"\n## Key Statistics\n"
                for stat in stats[:10]:  # Show top 10 stats
                    content += f"- **{stat.get('label', 'N/A')}**: {stat.get('value', 'N/A')}\n"
        
        elif search_type == 'currency':
            content += f"- **From**: {metadata.get('from_currency', 'N/A')}\n"
            content += f"- **To**: {metadata.get('to_currency', 'N/A')}\n"
            content += f"- **Amount**: {metadata.get('amount', 1.0)}\n"
            
            # Exchange rate information
            summary = finance_data.get('summary', {})
            if summary:
                content += f"\n## Exchange Rate Information\n"
                content += f"- **Rate**: {summary.get('extracted_price', 'N/A')}\n"
                content += f"- **Currency Pair**: {summary.get('title', 'N/A')}\n"
                
                price_movement = summary.get('price_movement', {})
                if price_movement:
                    content += f"- **Rate Change**: {price_movement.get('movement', 'N/A')} {price_movement.get('percentage', 0):.2f}%\n"
        
        elif search_type == 'market_overview':
            markets = finance_data.get('markets', {})
            content += f"\n## Market Overview\n"
            
            for region, items in markets.items():
                if isinstance(items, list) and items:
                    content += f"\n### {region.title()} ({len(items)} items)\n"
                    for item in items[:5]:  # Show top 5 per region
                        name = item.get('name', 'N/A')
                        price = item.get('price', 'N/A')
                        movement = item.get('price_movement', {})
                        movement_str = f"{movement.get('movement', '')} {movement.get('percentage', 0):.2f}%" if movement else "N/A"
                        content += f"- **{name}**: {price} ({movement_str})\n"
        
        elif search_type == 'historical':
            content += f"- **Symbol**: {metadata.get('symbol', 'N/A')}\n"
            content += f"- **Time Window**: {metadata.get('window', 'N/A')}\n"
            
            data_points = finance_data.get('data_points', 0)
            key_events = finance_data.get('key_events', [])
            content += f"- **Data Points**: {data_points}\n"
            content += f"- **Key Events**: {len(key_events)}\n"
            
            # Show key events
            if key_events:
                content += f"\n## Key Events\n"
                for event in key_events[:5]:  # Show top 5 events
                    content += f"- **{event.get('date', 'N/A')}**: {event.get('title', 'N/A')}\n"
                    content += f"  - Source: {event.get('source', 'N/A')}\n"
                    movement = event.get('price_movement', {})
                    if movement:
                        content += f"  - Impact: {movement.get('movement', 'N/A')} {movement.get('percentage', 0):.2f}%\n"
                    content += "\n"
        
        # News results (if available)
        news_results = finance_data.get('news_results', [])
        if news_results:
            content += f"\n## Recent News ({len(news_results)} articles)\n"
            for news_section in news_results[:3]:  # Show top 3 news sections
                title = news_section.get('title', 'News')
                items = news_section.get('items', [])
                if items:
                    content += f"\n### {title}\n"
                    for item in items[:3]:  # Show top 3 articles per section
                        content += f"- **{item.get('title', 'N/A')}**\n"
                        content += f"  - Source: {item.get('source', 'N/A')}\n"
                        content += f"  - Date: {item.get('date', 'N/A')}\n\n"
        
        return content
        
    except json.JSONDecodeError:
        return f"# Error\n\nCorrupted finance data for search ID: {search_id}"

@mcp.prompt()
def stock_analysis_prompt(
    symbol: str,
    exchange: str = "",
    time_period: str = "1Y",
    analysis_type: str = "comprehensive"
) -> str:
    """Generate a comprehensive stock analysis prompt for Claude."""
    
    prompt = f"""Analyze the stock {symbol.upper()}"""
    
    if exchange:
        prompt += f" listed on {exchange.upper()}"
    
    prompt += f" with a focus on the {time_period} time period."
    
    prompt += f"""

Please provide a {analysis_type} analysis including the following:

1. **Current Stock Information**: Use the lookup_stock tool to get current price and basic information:
   - Current stock price and market status
   - Recent price movements and trends
   - Key company information and statistics

2. **Historical Analysis**: Use the get_historical_data tool with window="{time_period}" to analyze:
   - Price performance over the specified period
   - Significant price movements and volatility
   - Key events that impacted the stock price
   - Support and resistance levels

3. **Fundamental Analysis** (if available in the data):
   - Revenue and earnings trends
   - Financial ratios and key metrics
   - Balance sheet health
   - Cash flow analysis

4. **Market Context**:
   - Compare performance to major market indices
   - Sector and industry comparison
   - Market sentiment and news analysis

5. **Technical Analysis**:
   - Price trends and patterns
   - Volume analysis
   - Moving averages and technical indicators

6. **Risk Assessment**:
   - Volatility analysis
   - Key risk factors
   - External factors affecting the stock

7. **Investment Recommendation**:
   - Summary of strengths and weaknesses
   - Potential catalysts and risks
   - Suggested investment approach based on the analysis

Please use the stock analysis tools first to gather comprehensive data, then provide detailed insights and actionable recommendations. Format the analysis in a clear, professional structure suitable for investment decision-making."""

    return prompt


@mcp.prompt()
def currency_analysis_prompt(
    base_currency: str,
    target_currencies: Union[str, List[str]],
    amount: float = 1000.0
) -> str:
    """
    Generate a comprehensive currency analysis and conversion prompt.
    
    Args:
        base_currency: The base currency code (e.g., 'USD', 'EUR', 'GBP')
        target_currencies: Target currencies as comma-separated string (e.g., 'EUR,GBP,JPY') 
                          or list of currency codes (e.g., ['EUR', 'GBP', 'JPY'])
        amount: Amount to convert (default: 1000.0)
    """
    
    # Handle both string and list inputs for target currencies
    if isinstance(target_currencies, str):
        # Split comma-separated string into list and clean up whitespace
        target_currencies_list = [currency.strip().upper() for currency in target_currencies.split(',')]
    else:
        target_currencies_list = [currency.upper() for currency in target_currencies]
    
    target_list = ", ".join(target_currencies_list)
    
    return f"""Analyze currency conversion from {base_currency.upper()} to multiple target currencies: {target_list}

Please provide a comprehensive currency analysis for converting {amount:,.2f} {base_currency.upper()}:

1. **Currency Conversions**: Use the convert_currency tool for each target currency:"""
    
    + "".join([f"""
   - Convert {amount:,.2f} {base_currency.upper()} to {currency}"""
              for currency in target_currencies_list]) + f"""

2. **Exchange Rate Analysis**:
   - Current exchange rates for all currency pairs
   - Recent rate movements and trends
   - Rate volatility and stability assessment

3. **Market Overview**: Use get_market_overview to understand:
   - Major currency pair performances
   - Global economic factors affecting rates
   - Regional economic indicators

4. **Economic Context**:
   - Economic factors affecting {base_currency.upper()}
   - Economic outlook for target currency regions
   - Central bank policies and interest rate impacts

5. **Conversion Recommendations**:
   - Best value conversions based on current rates
   - Timing considerations for currency conversion
   - Risk factors for each currency pair

6. **Practical Advice**:
   - Transaction costs and fee considerations
   - Best practices for currency conversion
   - Hedging strategies if applicable

Present the analysis in a clear format with specific conversion amounts, rates, and actionable recommendations for currency exchange decisions."""
@mcp.prompt()
def us_market_overview_prompt() -> str:
    """Generate a US market overview analysis prompt."""
    return _market_overview_template(["us"])

@mcp.prompt()
def global_market_overview_prompt() -> str:
    """Generate a global market overview analysis prompt."""
    return _market_overview_template(["us", "europe", "asia"])

@mcp.prompt()
def market_overview_prompt(regions: Union[str, List[str]] = "us,europe,asia") -> str:
    """Generate a comprehensive market overview analysis prompt."""
    
    # Handle both string and list inputs
    if isinstance(regions, str):
        regions_list = [region.strip() for region in regions.split(',')]
    else:
        regions_list = regions
    
    return _market_overview_template(regions_list)

def _market_overview_template(regions_list: List[str]) -> str:
    """Template function for market overview prompts."""
    regions_str = ", ".join([region.title() for region in regions_list])
    
    return f"""Provide a comprehensive market overview analysis focusing on {regions_str} markets.

Please analyze current market conditions and trends:

1. **Market Overview**: Use get_market_overview to gather current data on:
   - Major stock indices performance
   - Currency market movements  
   - Cryptocurrency trends
   - Futures market activity

2. **Regional Analysis** for each region ({regions_str}):
   - Key index performance and trends
   - Market sentiment indicators
   - Economic factors driving market movements
   - Notable gainers and losers

3. **Cross-Market Analysis**:
   - Correlations between different regional markets
   - Currency impacts on international markets
   - Global economic themes affecting all regions

4. **Sector Performance**:
   - Leading and lagging sectors across markets
   - Sector rotation trends
   - Industry-specific news and developments

5. **Risk Assessment**:
   - Market volatility indicators
   - Economic and geopolitical risks
   - Central bank policies and impacts

6. **Trading Opportunities**:
   - Potential arbitrage opportunities
   - Currency trade considerations
   - Market timing insights

7. **Outlook and Recommendations**:
   - Short-term market expectations
   - Key events and dates to watch
   - Investment strategy suggestions

Use filtering tools to highlight significant price movements and provide insights into market momentum. Present the analysis in a structured format suitable for investment professionals and active traders."""

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')