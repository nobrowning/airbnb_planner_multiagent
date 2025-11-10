import requests
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Directory to store flight search results
FLIGHTS_DIR = "flights"

# Initialize FastMCP server
mcp = FastMCP("flight-assistant")

def get_serpapi_key() -> str:
    """Get SerpAPI key from environment variable."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("SERPAPI_KEY environment variable is required")
    return api_key

@mcp.tool()
def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    trip_type: int = 1,
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0,
    travel_class: int = 1,
    currency: str = "USD",
    country: str = "us",
    language: str = "en",
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search for flights using SerpAPI's Google Flights API.
    
    Args:
        departure_id: Departure airport code (e.g., 'LAX', 'JFK') or location kgmid
        arrival_id: Arrival airport code (e.g., 'CDG', 'LHR') or location kgmid
        outbound_date: Departure date in YYYY-MM-DD format (e.g., '2024-12-15')
        return_date: Return date in YYYY-MM-DD format (required for round trips)
        trip_type: Flight type (1=Round trip, 2=One way, 3=Multi-city)
        adults: Number of adult passengers (default: 1)
        children: Number of child passengers (default: 0)
        infants_in_seat: Number of infants in seat (default: 0)
        infants_on_lap: Number of infants on lap (default: 0)
        travel_class: Travel class (1=Economy, 2=Premium economy, 3=Business, 4=First)
        currency: Currency for prices (default: 'USD')
        country: Country code for search (default: 'us')
        language: Language code (default: 'en')
        max_results: Maximum number of results to store (default: 10)
        
    Returns:
        Dict containing flight search results and metadata
    """
    
    try:
        api_key = get_serpapi_key()
        
        # Build search parameters
        params = {
            "engine": "google_flights",
            "api_key": api_key,
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "type": trip_type,
            "adults": adults,
            "children": children,
            "infants_in_seat": infants_in_seat,
            "infants_on_lap": infants_on_lap,
            "travel_class": travel_class,
            "currency": currency,
            "gl": country,
            "hl": language
        }
        
        # Add return date for round trips
        if trip_type == 1 and return_date:
            params["return_date"] = return_date
        elif trip_type == 1 and not return_date:
            return {"error": "Return date is required for round trip flights"}
        
        # Make API request
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        flight_data = response.json()
        
        # Create search identifier
        search_id = f"{departure_id}_{arrival_id}_{outbound_date}"
        if return_date:
            search_id += f"_{return_date}"
        search_id += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(FLIGHTS_DIR, exist_ok=True)
        
        # Process and store flight results
        processed_results = {
            "search_metadata": {
                "search_id": search_id,
                "departure": departure_id,
                "arrival": arrival_id,
                "outbound_date": outbound_date,
                "return_date": return_date,
                "trip_type": "Round trip" if trip_type == 1 else "One way" if trip_type == 2 else "Multi-city",
                "passengers": {
                    "adults": adults,
                    "children": children,
                    "infants_in_seat": infants_in_seat,
                    "infants_on_lap": infants_on_lap
                },
                "travel_class": ["Economy", "Premium economy", "Business", "First"][travel_class - 1],
                "currency": currency,
                "search_timestamp": datetime.now().isoformat()
            },
            "best_flights": flight_data.get("best_flights", [])[:max_results],
            "other_flights": flight_data.get("other_flights", [])[:max_results],
            "price_insights": flight_data.get("price_insights", {}),
            "airports": flight_data.get("airports", [])
        }
        
        # Save results to file
        file_path = os.path.join(FLIGHTS_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_results, f, indent=2)
        
        print(f"Flight search results saved to: {file_path}")
        
        # Return summary for the user
        summary = {
            "search_id": search_id,
            "total_best_flights": len(processed_results["best_flights"]),
            "total_other_flights": len(processed_results["other_flights"]),
            "price_range": {
                "lowest_price": processed_results["price_insights"].get("lowest_price"),
                "currency": currency
            },
            "search_parameters": processed_results["search_metadata"]
        }
        
        return summary
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_flight_details(search_id: str) -> str:
    """
    Get detailed information about a specific flight search.
    
    Args:
        search_id: The search ID returned from search_flights
        
    Returns:
        JSON string with detailed flight information
    """
    
    file_path = os.path.join(FLIGHTS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No flight search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            flight_data = json.load(f)
        return json.dumps(flight_data, indent=2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading flight data for {search_id}: {str(e)}"

@mcp.tool()
def filter_flights_by_price(
    search_id: str,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None
) -> str:
    """
    Filter flights from a search by price range.
    
    Args:
        search_id: The search ID returned from search_flights
        max_price: Maximum price filter (optional)
        min_price: Minimum price filter (optional)
        
    Returns:
        JSON string with filtered flight results
    """
    
    file_path = os.path.join(FLIGHTS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No flight search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            flight_data = json.load(f)
        
        def price_filter(flight):
            price = flight.get("price", 0)
            if min_price is not None and price < min_price:
                return False
            if max_price is not None and price > max_price:
                return False
            return True
        
        filtered_best = [f for f in flight_data.get("best_flights", []) if price_filter(f)]
        filtered_other = [f for f in flight_data.get("other_flights", []) if price_filter(f)]
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "min_price": min_price,
                "max_price": max_price
            },
            "filtered_best_flights": filtered_best,
            "filtered_other_flights": filtered_other,
            "total_filtered": len(filtered_best) + len(filtered_other)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing flight data for {search_id}: {str(e)}"

@mcp.tool()
def filter_flights_by_airline(search_id: str, airlines: List[str]) -> str:
    """
    Filter flights from a search by specific airlines.
    
    Args:
        search_id: The search ID returned from search_flights
        airlines: List of airline names or codes to filter by
        
    Returns:
        JSON string with filtered flight results
    """
    
    file_path = os.path.join(FLIGHTS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No flight search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            flight_data = json.load(f)
        
        def airline_filter(flight):
            flight_airlines = set()
            for leg in flight.get("flights", []):
                airline = leg.get("airline", "").lower()
                flight_airlines.add(airline)
            
            return any(airline.lower() in flight_airlines for airline in airlines)
        
        filtered_best = [f for f in flight_data.get("best_flights", []) if airline_filter(f)]
        filtered_other = [f for f in flight_data.get("other_flights", []) if airline_filter(f)]
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "airlines": airlines
            },
            "filtered_best_flights": filtered_best,
            "filtered_other_flights": filtered_other,
            "total_filtered": len(filtered_best) + len(filtered_other)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing flight data for {search_id}: {str(e)}"

@mcp.resource("flights://searches")
def get_flight_searches() -> str:
    """
    List all available flight searches.
    
    This resource provides a list of all saved flight searches.
    """
    searches = []
    
    if os.path.exists(FLIGHTS_DIR):
        for filename in os.listdir(FLIGHTS_DIR):
            if filename.endswith('.json'):
                search_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(FLIGHTS_DIR, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        metadata = data.get('search_metadata', {})
                        searches.append({
                            'search_id': search_id,
                            'route': f"{metadata.get('departure', 'N/A')} → {metadata.get('arrival', 'N/A')}",
                            'dates': f"{metadata.get('outbound_date', 'N/A')} - {metadata.get('return_date', 'One way')}",
                            'passengers': metadata.get('passengers', {}),
                            'search_time': metadata.get('search_timestamp', 'N/A')
                        })
                except (json.JSONDecodeError, KeyError):
                    continue
    
    content = "# Flight Searches\n\n"
    if searches:
        content += f"Total searches: {len(searches)}\n\n"
        for search in searches:
            content += f"## {search['search_id']}\n"
            content += f"- **Route**: {search['route']}\n"
            content += f"- **Dates**: {search['dates']}\n"
            content += f"- **Passengers**: {search['passengers'].get('adults', 0)} adults"
            if search['passengers'].get('children', 0) > 0:
                content += f", {search['passengers']['children']} children"
            if search['passengers'].get('infants_in_seat', 0) > 0:
                content += f", {search['passengers']['infants_in_seat']} infants in seat"
            if search['passengers'].get('infants_on_lap', 0) > 0:
                content += f", {search['passengers']['infants_on_lap']} infants on lap"
            content += "\n"
            content += f"- **Search Time**: {search['search_time']}\n\n"
            content += "---\n\n"
    else:
        content += "No flight searches found.\n\n"
        content += "Use the search_flights tool to search for flights.\n"
    
    return content

@mcp.resource("flights://{search_id}")
def get_flight_search_details(search_id: str) -> str:
    """
    Get detailed information about a specific flight search.
    
    Args:
        search_id: The flight search ID to retrieve details for
    """
    file_path = os.path.join(FLIGHTS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"# Flight Search Not Found: {search_id}\n\nNo flight search found with this ID."
    
    try:
        with open(file_path, 'r') as f:
            flight_data = json.load(f)
        
        metadata = flight_data.get('search_metadata', {})
        best_flights = flight_data.get('best_flights', [])
        other_flights = flight_data.get('other_flights', [])
        price_insights = flight_data.get('price_insights', {})
        
        content = f"# Flight Search: {search_id}\n\n"
        content += f"## Search Details\n"
        content += f"- **Route**: {metadata.get('departure', 'N/A')} → {metadata.get('arrival', 'N/A')}\n"
        content += f"- **Dates**: {metadata.get('outbound_date', 'N/A')}"
        if metadata.get('return_date'):
            content += f" - {metadata['return_date']}"
        content += "\n"
        content += f"- **Trip Type**: {metadata.get('trip_type', 'N/A')}\n"
        content += f"- **Travel Class**: {metadata.get('travel_class', 'N/A')}\n"
        content += f"- **Currency**: {metadata.get('currency', 'USD')}\n"
        content += f"- **Search Time**: {metadata.get('search_timestamp', 'N/A')}\n\n"
        
        # Price insights
        if price_insights:
            content += f"## Price Insights\n"
            if 'lowest_price' in price_insights:
                content += f"- **Lowest Price**: {price_insights['lowest_price']} {metadata.get('currency', 'USD')}\n"
            if 'price_level' in price_insights:
                content += f"- **Price Level**: {price_insights['price_level']}\n"
            if 'typical_price_range' in price_insights and price_insights['typical_price_range']:
                range_data = price_insights['typical_price_range']
                content += f"- **Typical Range**: {range_data[0]} - {range_data[1]} {metadata.get('currency', 'USD')}\n"
            content += "\n"
        
        # Best flights
        if best_flights:
            content += f"## Best Flights ({len(best_flights)})\n\n"
            for i, flight in enumerate(best_flights[:5]):  # Show top 5
                content += f"### Option {i+1}\n"
                content += f"- **Price**: {flight.get('price', 'N/A')} {metadata.get('currency', 'USD')}\n"
                content += f"- **Total Duration**: {flight.get('total_duration', 0)} minutes\n"
                content += f"- **Flights**: {len(flight.get('flights', []))}\n"
                if flight.get('layovers'):
                    content += f"- **Layovers**: {len(flight['layovers'])}\n"
                
                # Flight details
                for j, leg in enumerate(flight.get('flights', [])):
                    dep_airport = leg.get('departure_airport', {})
                    arr_airport = leg.get('arrival_airport', {})
                    content += f"  - **Flight {j+1}**: {dep_airport.get('id', 'N/A')} → {arr_airport.get('id', 'N/A')}\n"
                    content += f"    - Departure: {dep_airport.get('time', 'N/A')}\n"
                    content += f"    - Arrival: {arr_airport.get('time', 'N/A')}\n"
                    content += f"    - Airline: {leg.get('airline', 'N/A')}\n"
                    content += f"    - Flight Number: {leg.get('flight_number', 'N/A')}\n"
                
                content += "\n"
        
        # Other flights summary
        if other_flights:
            content += f"## Other Flights\n"
            content += f"Total other options: {len(other_flights)}\n"
            content += f"Price range: {min(f.get('price', 0) for f in other_flights)} - {max(f.get('price', 0) for f in other_flights)} {metadata.get('currency', 'USD')}\n\n"
        
        return content
        
    except json.JSONDecodeError:
        return f"# Error\n\nCorrupted flight data for search ID: {search_id}"

@mcp.prompt()
def travel_planning_prompt(
    departure: str,
    destination: str,
    departure_date: str,
    return_date: str = "",
    passengers: int = 1,
    budget: str = "",
    preferences: str = ""
) -> str:
    """Generate a comprehensive travel planning prompt for Claude."""
    
    prompt = f"""Plan a comprehensive trip from {departure} to {destination} departing on {departure_date}"""
    
    if return_date:
        prompt += f" and returning on {return_date}"
    else:
        prompt += " (one way)"
    
    prompt += f" for {passengers} passenger{'s' if passengers != 1 else ''}."
    
    if budget:
        prompt += f" Budget consideration: {budget}."
    
    if preferences:
        prompt += f" Travel preferences: {preferences}."
    
    prompt += f"""

Please help with the following travel planning tasks:

1. **Flight Search**: Use the search_flights tool to find the best flight options:
   - Search for flights from {departure} to {destination}
   - Departure date: {departure_date}"""
    
    if return_date:
        prompt += f"""
   - Return date: {return_date}
   - Trip type: Round trip (1)"""
    else:
        prompt += f"""
   - Trip type: One way (2)"""
    
    prompt += f"""
   - Number of passengers: {passengers}
   - Analyze price insights and recommend best options

2. **Flight Analysis**: Once flights are found, provide:
   - Summary of the best flight options with pros and cons
   - Price comparison and value analysis
   - Duration and layover analysis
   - Airline and aircraft information
   - Carbon emissions comparison if available

3. **Travel Recommendations**: Based on the destination and dates:
   - Best times to book and travel tips
   - Airport information and transportation options
   - Weather considerations for travel dates
   - General destination tips and highlights

4. **Budget Planning**: If budget information provided:
   - Flight cost analysis within budget
   - Tips for finding better deals
   - Alternative travel dates if current search is expensive

Present the information in a clear, organized format with actionable recommendations. Use the flight search tools first, then provide comprehensive analysis and recommendations based on the results."""

    return prompt

@mcp.prompt()
def flight_comparison_prompt(search_id: str) -> str:
    """Generate a prompt for detailed flight comparison and analysis."""
    
    return f"""Analyze and compare the flight options from search ID: {search_id}

Please provide a comprehensive analysis including:

1. **Flight Overview**: Use get_flight_details('{search_id}') to retrieve the complete flight data

2. **Best Options Analysis**:
   - Top 3-5 recommended flights with detailed breakdown
   - Price-to-value ratio analysis
   - Total travel time comparison
   - Layover analysis (duration, airports, overnight stays)

3. **Detailed Comparison Table**:
   - Price comparison across all options
   - Duration comparison (flight time vs total time)
   - Number of stops and layover quality
   - Airlines and aircraft types
   - Departure/arrival times convenience

4. **Filtering Suggestions**:
   - Use filter_flights_by_price to show budget-friendly options
   - Use filter_flights_by_airline for preferred carriers
   - Highlight direct flights vs connections

5. **Decision Recommendations**:
   - Best overall value option
   - Fastest travel option
   - Most convenient schedule option
   - Budget-conscious option

6. **Booking Considerations**:
   - Price trends and booking timing advice
   - Airline policies and baggage considerations
   - Seat selection and upgrade opportunities

Please format the analysis in a clear, easy-to-read structure with specific recommendations for different traveler priorities (speed, cost, convenience, comfort)."""

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')