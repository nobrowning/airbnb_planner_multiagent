import requests
import json
import os
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Directory to store hotel search results
HOTELS_DIR = "hotels"

# Initialize FastMCP server
mcp = FastMCP("hotel-assistant")

def get_serpapi_key() -> str:
    """Get SerpAPI key from environment variable."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("SERPAPI_KEY environment variable is required")
    return api_key

@mcp.tool()
def search_hotels(
    location: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    children: int = 0,
    children_ages: Optional[List[int]] = None,
    currency: str = "USD",
    country: str = "us",
    language: str = "en",
    sort_by: Optional[int] = None,
    hotel_class: Optional[List[int]] = None,
    amenities: Optional[List[int]] = None,
    property_types: Optional[List[int]] = None,
    brands: Optional[List[int]] = None,
    free_cancellation: bool = False,
    special_offers: bool = False,
    vacation_rentals: bool = False,
    bedrooms: Optional[int] = None,
    max_results: int = 20
) -> Dict[str, Any]:
    """
    Search for hotels using SerpAPI's Google Hotels API.
    
    Args:
        location: Hotel search location (e.g., 'New York', 'Paris', 'Bali Resorts')
        check_in_date: Check-in date in YYYY-MM-DD format (e.g., '2025-06-15')
        check_out_date: Check-out date in YYYY-MM-DD format (e.g., '2025-06-20')
        adults: Number of adult guests (default: 2)
        children: Number of child guests (default: 0)
        children_ages: List of children ages (1-17 years)
        currency: Currency for prices (default: 'USD')
        country: Country code for search (default: 'us')
        language: Language code (default: 'en')
        sort_by: Sort results (3=Lowest price, 8=Highest rating, 13=Most reviewed)
        hotel_class: Filter by hotel class (2-5 stars, e.g., [4, 5])
        amenities: Filter by amenity IDs (e.g., [35, 9, 19])
        property_types: Filter by property type IDs (e.g., [17, 12, 18])
        brands: Filter by brand IDs (e.g., [33, 67, 101])
        free_cancellation: Show only hotels with free cancellation
        special_offers: Show only hotels with special offers
        vacation_rentals: Search for vacation rentals instead of hotels
        bedrooms: Minimum number of bedrooms (vacation rentals only)
        max_results: Maximum number of results to store (default: 20)
        
    Returns:
        Dict containing hotel search results and metadata
    """
    
    try:
        api_key = get_serpapi_key()
        
        # Build search parameters
        params = {
            "engine": "google_hotels",
            "api_key": api_key,
            "q": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "adults": adults,
            "children": children,
            "currency": currency,
            "gl": country,
            "hl": language
        }
        
        # Add optional parameters
        if children_ages:
            params["children_ages"] = ",".join(str(age) for age in children_ages)
        
        if sort_by:
            params["sort_by"] = sort_by
            
        if hotel_class:
            params["hotel_class"] = ",".join(str(hc) for hc in hotel_class)
            
        if amenities:
            params["amenities"] = ",".join(str(a) for a in amenities)
            
        if property_types:
            params["property_types"] = ",".join(str(pt) for pt in property_types)
            
        if brands:
            params["brands"] = ",".join(str(b) for b in brands)
            
        if free_cancellation:
            params["free_cancellation"] = "true"
            
        if special_offers:
            params["special_offers"] = "true"
            
        if vacation_rentals:
            params["vacation_rentals"] = "true"
            
        if bedrooms is not None:
            params["bedrooms"] = bedrooms
        
        # Make API request
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        hotel_data = response.json()
        
        # Create search identifier
        search_id = f"{location.replace(' ', '_')}_{check_in_date}_{check_out_date}"
        search_id += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(HOTELS_DIR, exist_ok=True)
        
        # Process and store hotel results
        processed_results = {
            "search_metadata": {
                "search_id": search_id,
                "location": location,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "guests": {
                    "adults": adults,
                    "children": children,
                    "children_ages": children_ages
                },
                "search_type": "vacation_rentals" if vacation_rentals else "hotels",
                "currency": currency,
                "filters": {
                    "sort_by": sort_by,
                    "hotel_class": hotel_class,
                    "amenities": amenities,
                    "property_types": property_types,
                    "brands": brands,
                    "free_cancellation": free_cancellation,
                    "special_offers": special_offers,
                    "bedrooms": bedrooms
                },
                "search_timestamp": datetime.now().isoformat()
            },
            "search_information": hotel_data.get("search_information", {}),
            "properties": hotel_data.get("properties", [])[:max_results],
            "brands": hotel_data.get("brands", []),
            "serpapi_pagination": hotel_data.get("serpapi_pagination", {})
        }
        
        # Save results to file
        file_path = os.path.join(HOTELS_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_results, f, indent=2)
        
        print(f"Hotel search results saved to: {file_path}")
        
        # Calculate price range
        properties = processed_results["properties"]
        price_range = None
        if properties:
            prices = []
            for prop in properties:
                rate = prop.get("rate_per_night", {})
                if rate.get("extracted_lowest"):
                    prices.append(rate["extracted_lowest"])
            
            if prices:
                price_range = {
                    "min_price": min(prices),
                    "max_price": max(prices),
                    "currency": currency
                }
        
        # Return summary for the user
        summary = {
            "search_id": search_id,
            "total_properties": len(processed_results["properties"]),
            "location": location,
            "dates": f"{check_in_date} to {check_out_date}",
            "guests": f"{adults} adults" + (f", {children} children" if children > 0 else ""),
            "price_range": price_range,
            "search_type": "vacation_rentals" if vacation_rentals else "hotels",
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
def get_hotel_details(search_id: str) -> str:
    """
    Get detailed information about a specific hotel search.
    
    Args:
        search_id: The search ID returned from search_hotels
        
    Returns:
        JSON string with detailed hotel information
    """
    
    file_path = os.path.join(HOTELS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No hotel search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            hotel_data = json.load(f)
        return json.dumps(hotel_data, indent=2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading hotel data for {search_id}: {str(e)}"

@mcp.tool()
def get_property_details(
    property_token: str,
    currency: str = "USD",
    country: str = "us",
    language: str = "en"
) -> str:
    """
    Get detailed information about a specific property using its token.
    
    Args:
        property_token: The property token from hotel search results
        currency: Currency for prices (default: 'USD')
        country: Country code for search (default: 'us')
        language: Language code (default: 'en')
        
    Returns:
        JSON string with detailed property information
    """
    
    try:
        api_key = get_serpapi_key()
        
        params = {
            "engine": "google_hotels",
            "api_key": api_key,
            "property_token": property_token,
            "currency": currency,
            "gl": country,
            "hl": language
        }
        
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        property_data = response.json()
        return json.dumps(property_data, indent=2)
        
    except requests.exceptions.RequestException as e:
        return f"API request failed: {str(e)}"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool()
def filter_hotels_by_price(
    search_id: str,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None
) -> str:
    """
    Filter hotels from a search by price range.
    
    Args:
        search_id: The search ID returned from search_hotels
        max_price: Maximum price per night filter (optional)
        min_price: Minimum price per night filter (optional)
        
    Returns:
        JSON string with filtered hotel results
    """
    
    file_path = os.path.join(HOTELS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No hotel search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            hotel_data = json.load(f)
        
        def price_filter(hotel):
            rate = hotel.get("rate_per_night", {})
            price = rate.get("extracted_lowest", 0)
            if min_price is not None and price < min_price:
                return False
            if max_price is not None and price > max_price:
                return False
            return True
        
        filtered_properties = [h for h in hotel_data.get("properties", []) if price_filter(h)]
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "min_price": min_price,
                "max_price": max_price
            },
            "filtered_properties": filtered_properties,
            "total_filtered": len(filtered_properties)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing hotel data for {search_id}: {str(e)}"

@mcp.tool()
def filter_hotels_by_rating(
    search_id: str,
    min_rating: float = 4.0
) -> str:
    """
    Filter hotels from a search by minimum rating.
    
    Args:
        search_id: The search ID returned from search_hotels
        min_rating: Minimum overall rating filter (default: 4.0)
        
    Returns:
        JSON string with filtered hotel results
    """
    
    file_path = os.path.join(HOTELS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No hotel search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            hotel_data = json.load(f)
        
        def rating_filter(hotel):
            rating = hotel.get("overall_rating", 0)
            return rating >= min_rating
        
        filtered_properties = [h for h in hotel_data.get("properties", []) if rating_filter(h)]
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "min_rating": min_rating
            },
            "filtered_properties": filtered_properties,
            "total_filtered": len(filtered_properties)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing hotel data for {search_id}: {str(e)}"

@mcp.tool()
def filter_hotels_by_amenities(
    search_id: str,
    required_amenities: List[str]
) -> str:
    """
    Filter hotels from a search by required amenities.
    
    Args:
        search_id: The search ID returned from search_hotels
        required_amenities: List of required amenity names (e.g., ['Free Wi-Fi', 'Pool', 'Spa'])
        
    Returns:
        JSON string with filtered hotel results
    """
    
    file_path = os.path.join(HOTELS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No hotel search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            hotel_data = json.load(f)
        
        def amenity_filter(hotel):
            hotel_amenities = hotel.get("amenities", [])
            hotel_amenities_lower = [a.lower() for a in hotel_amenities]
            return all(req.lower() in hotel_amenities_lower for req in required_amenities)
        
        filtered_properties = [h for h in hotel_data.get("properties", []) if amenity_filter(h)]
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "required_amenities": required_amenities
            },
            "filtered_properties": filtered_properties,
            "total_filtered": len(filtered_properties)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing hotel data for {search_id}: {str(e)}"

@mcp.tool()
def filter_hotels_by_class(
    search_id: str,
    hotel_classes: List[int]
) -> str:
    """
    Filter hotels from a search by hotel class (star rating).
    
    Args:
        search_id: The search ID returned from search_hotels
        hotel_classes: List of hotel classes (e.g., [4, 5] for 4-5 star hotels)
        
    Returns:
        JSON string with filtered hotel results
    """
    
    file_path = os.path.join(HOTELS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No hotel search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            hotel_data = json.load(f)
        
        def class_filter(hotel):
            hotel_class = hotel.get("extracted_hotel_class", 0)
            return hotel_class in hotel_classes
        
        filtered_properties = [h for h in hotel_data.get("properties", []) if class_filter(h)]
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "hotel_classes": hotel_classes
            },
            "filtered_properties": filtered_properties,
            "total_filtered": len(filtered_properties)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing hotel data for {search_id}: {str(e)}"

@mcp.resource("hotels://searches")
def get_hotel_searches() -> str:
    """
    List all available hotel searches.
    
    This resource provides a list of all saved hotel searches.
    """
    searches = []
    
    if os.path.exists(HOTELS_DIR):
        for filename in os.listdir(HOTELS_DIR):
            if filename.endswith('.json'):
                search_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(HOTELS_DIR, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        metadata = data.get('search_metadata', {})
                        searches.append({
                            'search_id': search_id,
                            'location': metadata.get('location', 'N/A'),
                            'dates': f"{metadata.get('check_in_date', 'N/A')} - {metadata.get('check_out_date', 'N/A')}",
                            'guests': metadata.get('guests', {}),
                            'search_type': metadata.get('search_type', 'hotels'),
                            'search_time': metadata.get('search_timestamp', 'N/A'),
                            'total_properties': len(data.get('properties', []))
                        })
                except (json.JSONDecodeError, KeyError):
                    continue
    
    content = "# Hotel Searches\n\n"
    if searches:
        content += f"Total searches: {len(searches)}\n\n"
        for search in searches:
            content += f"## {search['search_id']}\n"
            content += f"- **Location**: {search['location']}\n"
            content += f"- **Dates**: {search['dates']}\n"
            content += f"- **Guests**: {search['guests'].get('adults', 0)} adults"
            if search['guests'].get('children', 0) > 0:
                content += f", {search['guests']['children']} children"
            content += "\n"
            content += f"- **Type**: {search['search_type'].title()}\n"
            content += f"- **Properties Found**: {search['total_properties']}\n"
            content += f"- **Search Time**: {search['search_time']}\n\n"
            content += "---\n\n"
    else:
        content += "No hotel searches found.\n\n"
        content += "Use the search_hotels tool to search for hotels.\n"
    
    return content

@mcp.resource("hotels://{search_id}")
def get_hotel_search_details(search_id: str) -> str:
    """
    Get detailed information about a specific hotel search.
    
    Args:
        search_id: The hotel search ID to retrieve details for
    """
    file_path = os.path.join(HOTELS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"# Hotel Search Not Found: {search_id}\n\nNo hotel search found with this ID."
    
    try:
        with open(file_path, 'r') as f:
            hotel_data = json.load(f)
        
        metadata = hotel_data.get('search_metadata', {})
        properties = hotel_data.get('properties', [])
        brands = hotel_data.get('brands', [])
        
        content = f"# Hotel Search: {search_id}\n\n"
        content += f"## Search Details\n"
        content += f"- **Location**: {metadata.get('location', 'N/A')}\n"
        content += f"- **Check-in**: {metadata.get('check_in_date', 'N/A')}\n"
        content += f"- **Check-out**: {metadata.get('check_out_date', 'N/A')}\n"
        content += f"- **Guests**: {metadata.get('guests', {}).get('adults', 0)} adults"
        if metadata.get('guests', {}).get('children', 0) > 0:
            content += f", {metadata['guests']['children']} children"
        content += "\n"
        content += f"- **Search Type**: {metadata.get('search_type', 'hotels').title()}\n"
        content += f"- **Currency**: {metadata.get('currency', 'USD')}\n"
        content += f"- **Search Time**: {metadata.get('search_timestamp', 'N/A')}\n\n"
        
        # Search filters
        filters = metadata.get('filters', {})
        if any(filters.values()):
            content += f"## Applied Filters\n"
            if filters.get('sort_by'):
                sort_names = {3: "Lowest price", 8: "Highest rating", 13: "Most reviewed"}
                content += f"- **Sort By**: {sort_names.get(filters['sort_by'], 'Custom')}\n"
            if filters.get('hotel_class'):
                content += f"- **Hotel Class**: {', '.join(f'{hc}-star' for hc in filters['hotel_class'])}\n"
            if filters.get('free_cancellation'):
                content += f"- **Free Cancellation**: Yes\n"
            if filters.get('special_offers'):
                content += f"- **Special Offers**: Yes\n"
            if filters.get('bedrooms'):
                content += f"- **Min Bedrooms**: {filters['bedrooms']}\n"
            content += "\n"
        
        # Properties summary
        if properties:
            content += f"## Properties Found ({len(properties)})\n\n"
            
            # Calculate price range and ratings
            prices = []
            ratings = []
            for prop in properties[:10]:  # Show top 10
                rate = prop.get("rate_per_night", {})
                if rate.get("extracted_lowest"):
                    prices.append(rate["extracted_lowest"])
                rating = prop.get("overall_rating")
                if rating:
                    ratings.append(rating)
            
            if prices:
                content += f"**Price Range**: ${min(prices)} - ${max(prices)} per night\n"
            if ratings:
                content += f"**Rating Range**: {min(ratings):.1f} - {max(ratings):.1f} stars\n\n"
            
            # Top properties
            for i, prop in enumerate(properties[:5]):  # Show top 5
                content += f"### {i+1}. {prop.get('name', 'N/A')}\n"
                
                # Basic info
                content += f"- **Type**: {prop.get('type', 'N/A').title()}\n"
                if prop.get('hotel_class'):
                    content += f"- **Class**: {prop.get('hotel_class', 'N/A')}\n"
                
                # Pricing
                rate = prop.get("rate_per_night", {})
                if rate.get("lowest"):
                    content += f"- **Rate**: {rate['lowest']} per night"
                    if rate.get("before_taxes_fees"):
                        content += f" (${rate['before_taxes_fees']} before taxes/fees)"
                    content += "\n"
                
                # Rating
                if prop.get("overall_rating"):
                    content += f"- **Rating**: {prop['overall_rating']:.1f}/5"
                    if prop.get("reviews"):
                        content += f" ({prop['reviews']} reviews)"
                    content += "\n"
                
                # Location
                if prop.get("location_rating"):
                    content += f"- **Location Rating**: {prop['location_rating']:.1f}/5\n"
                
                # Key amenities (first 5)
                amenities = prop.get("amenities", [])
                if amenities:
                    content += f"- **Amenities**: {', '.join(amenities[:5])}"
                    if len(amenities) > 5:
                        content += f" (and {len(amenities) - 5} more)"
                    content += "\n"
                
                # Special features
                if prop.get("deal"):
                    content += f"- **Deal**: {prop['deal']}\n"
                if prop.get("eco_certified"):
                    content += f"- **Eco Certified**: Yes\n"
                if prop.get("sponsored"):
                    content += f"- **Sponsored**: Yes\n"
                
                content += "\n"
        
        # Available brands
        if brands:
            content += f"## Available Brands ({len(brands)})\n\n"
            for brand in brands[:10]:  # Show top 10 brands
                content += f"- **{brand.get('name', 'N/A')}** (ID: {brand.get('id', 'N/A')})\n"
                children = brand.get('children', [])
                if children:
                    content += f"  - Sub-brands: {', '.join(child.get('name', 'N/A') for child in children[:3])}"
                    if len(children) > 3:
                        content += f" (and {len(children) - 3} more)"
                    content += "\n"
            content += "\n"
        
        return content
        
    except json.JSONDecodeError:
        return f"# Error\n\nCorrupted hotel data for search ID: {search_id}"

@mcp.prompt()
def hotel_planning_prompt(
    destination: str,
    check_in_date: str,
    check_out_date: str,
    guests: int = 2,
    budget: str = "",
    preferences: str = "",
    hotel_type: str = "hotels"
) -> str:
    """Generate a comprehensive hotel planning prompt for Claude."""
    
    prompt = f"""Plan accommodation for a trip to {destination} from {check_in_date} to {check_out_date} for {guests} guest{'s' if guests != 1 else ''}."""
    
    if budget:
        prompt += f" Budget consideration: {budget}."
    
    if preferences:
        prompt += f" Accommodation preferences: {preferences}."
    
    prompt += f"""

Please help with the following hotel planning tasks:

1. **Hotel Search**: Use the search_hotels tool to find the best accommodation options:
   - Location: {destination}
   - Check-in: {check_in_date}
   - Check-out: {check_out_date}
   - Guests: {guests}
   - Type: {hotel_type}
   - Analyze results and recommend best options

2. **Hotel Analysis**: Once hotels are found, provide:
   - Summary of the top 5-10 hotel options with pros and cons
   - Price comparison and value analysis
   - Location analysis and proximity to attractions
   - Amenities comparison
   - Guest rating and review analysis
   - Room type and accommodation details

3. **Filtering and Recommendations**: Apply relevant filters:
   - Use filter_hotels_by_price for budget considerations
   - Use filter_hotels_by_rating for quality assurance
   - Use filter_hotels_by_amenities for specific requirements
   - Use filter_hotels_by_class for luxury or budget preferences

4. **Detailed Property Information**: For top choices:
   - Use get_property_details to get comprehensive information
   - Include photos, detailed amenities, policies, and reviews
   - Nearby attractions and transportation options

5. **Accommodation Recommendations**: Based on the destination and preferences:
   - Best neighborhoods to stay in
   - Transportation considerations
   - Local attractions and accessibility
   - Dining and entertainment options nearby

6. **Budget Planning**: If budget information provided:
   - Accommodation cost analysis within budget
   - Tips for finding better deals
   - Alternative date suggestions if current search is expensive
   - Additional costs to consider (taxes, fees, parking, resort fees)

Present the information in a clear, organized format with actionable recommendations. Use the hotel search tools first, then provide comprehensive analysis and recommendations based on the results."""

    return prompt

@mcp.prompt()
def hotel_comparison_prompt(search_id: str) -> str:
    """Generate a prompt for detailed hotel comparison and analysis."""
    
    return f"""Analyze and compare the hotel options from search ID: {search_id}

Please provide a comprehensive analysis including:

1. **Hotel Overview**: Use get_hotel_details('{search_id}') to retrieve the complete hotel data

2. **Top Recommendations Analysis**:
   - Top 5-8 recommended hotels with detailed breakdown
   - Price-to-value ratio analysis
   - Location convenience comparison
   - Amenity and service analysis

3. **Detailed Comparison Table**:
   - Price comparison (per night and total cost)
   - Star rating and guest review scores
   - Key amenities and facilities
   - Location ratings and nearby attractions
   - Room types and sizes available

4. **Filtering Suggestions**:
   - Use filter_hotels_by_price to show budget-friendly options
   - Use filter_hotels_by_rating for highly-rated accommodations
   - Use filter_hotels_by_amenities for specific requirements (pool, spa, gym, etc.)
   - Use filter_hotels_by_class for different luxury levels

5. **Decision Recommendations**:
   - Best overall value option
   - Luxury/premium option
   - Budget-conscious option
   - Best location option
   - Best amenities option

6. **Booking Considerations**:
   - Cancellation policies and flexibility
   - Additional fees and taxes
   - Check-in/check-out times
   - Special offers or packages available
   - Seasonal pricing considerations

7. **Neighborhood Analysis**:
   - Safety and walkability
   - Proximity to attractions, restaurants, and transportation
   - Local character and atmosphere
   - Shopping and entertainment options

Please format the analysis in a clear, easy-to-read structure with specific recommendations for different traveler priorities (budget, luxury, location, amenities, business travel, family travel)."""

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')