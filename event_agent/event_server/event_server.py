import requests
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Directory to store event search results
EVENTS_DIR = "events"

# Initialize FastMCP server
mcp = FastMCP("event-assistant")

def get_serpapi_key() -> str:
    """Get SerpAPI key from environment variable."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("SERPAPI_KEY environment variable is required")
    return api_key

@mcp.tool()
def search_events(
    query: str,
    location: Optional[str] = None,
    date_filter: Optional[str] = None,
    event_type: Optional[str] = None,
    language: str = "en",
    country: str = "us",
    max_results: int = 20
) -> Dict[str, Any]:
    """
    Search for events using SerpAPI's Google Events API.
    
    Args:
        query: Search query for events (e.g., "concerts", "festivals", "art shows")
        location: Location to search events in (e.g., "New York", "San Francisco")
        date_filter: Time filter (today, tomorrow, week, weekend, next_week, month, next_month)
        event_type: Type of event filter (Virtual-Event for online events)
        language: Language code (default: 'en')
        country: Country code (default: 'us')
        max_results: Maximum number of results to store (default: 20)
        
    Returns:
        Dict containing event search results and metadata
    """
    
    try:
        api_key = get_serpapi_key()
        
        # Build search query
        search_query = query
        if location:
            search_query += f" in {location}"
        
        # Build search parameters
        params = {
            "engine": "google_events",
            "api_key": api_key,
            "q": search_query,
            "hl": language,
            "gl": country
        }
        
        # Build advanced filters
        filters = []
        if date_filter:
            filters.append(f"date:{date_filter}")
        if event_type:
            filters.append(f"event_type:{event_type}")
        
        if filters:
            params["htichips"] = ",".join(filters)
        
        # Make API request
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        event_data = response.json()
        
        # Create search identifier
        search_id = f"{query.replace(' ', '_')}_{location or 'global'}"
        if date_filter:
            search_id += f"_{date_filter}"
        if event_type:
            search_id += f"_{event_type}"
        search_id += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(EVENTS_DIR, exist_ok=True)
        
        # Process and store event results
        events_results = event_data.get("events_results", [])[:max_results]
        
        processed_results = {
            "search_metadata": {
                "search_id": search_id,
                "query": query,
                "location": location,
                "date_filter": date_filter,
                "event_type": event_type,
                "language": language,
                "country": country,
                "search_timestamp": datetime.now().isoformat(),
                "total_results": len(events_results)
            },
            "search_parameters": event_data.get("search_parameters", {}),
            "search_information": event_data.get("search_information", {}),
            "events_results": events_results
        }
        
        # Save results to file
        file_path = os.path.join(EVENTS_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_results, f, indent=2)
        
        print(f"Event search results saved to: {file_path}")
        
        # Return summary for the user
        summary = {
            "search_id": search_id,
            "total_events": len(events_results),
            "query": query,
            "location": location,
            "filters_applied": {
                "date_filter": date_filter,
                "event_type": event_type
            },
            "sample_events": [
                {
                    "title": event.get("title", "N/A"),
                    "date": event.get("date", {}).get("when", "N/A"),
                    "venue": event.get("venue", {}).get("name", "N/A") if event.get("venue") else "N/A"
                } for event in events_results[:3]
            ],
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
def get_event_details(search_id: str) -> str:
    """
    Get detailed information about a specific event search.
    
    Args:
        search_id: The search ID returned from search_events
        
    Returns:
        JSON string with detailed event information
    """
    
    file_path = os.path.join(EVENTS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No event search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            event_data = json.load(f)
        return json.dumps(event_data, indent=2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading event data for {search_id}: {str(e)}"

@mcp.tool()
def filter_events_by_date(
    search_id: str,
    date_range: Optional[str] = None,
    specific_date: Optional[str] = None
) -> str:
    """
    Filter events from a search by date criteria.
    
    Args:
        search_id: The search ID returned from search_events
        date_range: Date range filter (today, tomorrow, week, weekend, next_week, month)
        specific_date: Filter by specific date (YYYY-MM-DD format)
        
    Returns:
        JSON string with filtered event results
    """
    
    file_path = os.path.join(EVENTS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No event search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            event_data = json.load(f)
        
        events = event_data.get("events_results", [])
        filtered_events = []
        
        for event in events:
            event_date = event.get("date", {})
            if date_range:
                # This is a simplified filter - in reality, you'd need more complex date parsing
                if date_range.lower() in event_date.get("when", "").lower():
                    filtered_events.append(event)
            elif specific_date:
                if specific_date in event_date.get("when", ""):
                    filtered_events.append(event)
            else:
                filtered_events.append(event)
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "date_range": date_range,
                "specific_date": specific_date
            },
            "filtered_events": filtered_events,
            "total_filtered": len(filtered_events)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing event data for {search_id}: {str(e)}"

@mcp.tool()
def filter_events_by_type(
    search_id: str,
    event_types: List[str]
) -> str:
    """
    Filter events from a search by event type or category.
    
    Args:
        search_id: The search ID returned from search_events
        event_types: List of event types to filter by (e.g., ['concert', 'festival', 'art'])
        
    Returns:
        JSON string with filtered event results
    """
    
    file_path = os.path.join(EVENTS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No event search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            event_data = json.load(f)
        
        events = event_data.get("events_results", [])
        filtered_events = []
        
        for event in events:
            event_title = event.get("title", "").lower()
            event_description = event.get("description", "").lower()
            
            if any(event_type.lower() in event_title or event_type.lower() in event_description 
                   for event_type in event_types):
                filtered_events.append(event)
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "event_types": event_types
            },
            "filtered_events": filtered_events,
            "total_filtered": len(filtered_events)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing event data for {search_id}: {str(e)}"

@mcp.tool()
def filter_events_by_venue(
    search_id: str,
    venue_names: List[str]
) -> str:
    """
    Filter events from a search by venue names.
    
    Args:
        search_id: The search ID returned from search_events
        venue_names: List of venue names to filter by
        
    Returns:
        JSON string with filtered event results
    """
    
    file_path = os.path.join(EVENTS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No event search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            event_data = json.load(f)
        
        events = event_data.get("events_results", [])
        filtered_events = []
        
        for event in events:
            venue_info = event.get("venue", {})
            venue_name = venue_info.get("name", "").lower()
            
            if any(venue.lower() in venue_name for venue in venue_names):
                filtered_events.append(event)
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "venue_names": venue_names
            },
            "filtered_events": filtered_events,
            "total_filtered": len(filtered_events)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing event data for {search_id}: {str(e)}"

@mcp.resource("events://searches")
def get_event_searches() -> str:
    """
    List all available event searches.
    
    This resource provides a list of all saved event searches.
    """
    searches = []
    
    if os.path.exists(EVENTS_DIR):
        for filename in os.listdir(EVENTS_DIR):
            if filename.endswith('.json'):
                search_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(EVENTS_DIR, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        metadata = data.get('search_metadata', {})
                        searches.append({
                            'search_id': search_id,
                            'query': metadata.get('query', 'N/A'),
                            'location': metadata.get('location', 'N/A'),
                            'date_filter': metadata.get('date_filter', 'None'),
                            'event_type': metadata.get('event_type', 'None'),
                            'total_results': metadata.get('total_results', 0),
                            'search_time': metadata.get('search_timestamp', 'N/A')
                        })
                except (json.JSONDecodeError, KeyError):
                    continue
    
    content = "# Event Searches\n\n"
    if searches:
        content += f"Total searches: {len(searches)}\n\n"
        for search in searches:
            content += f"## {search['search_id']}\n"
            content += f"- **Query**: {search['query']}\n"
            content += f"- **Location**: {search['location']}\n"
            content += f"- **Date Filter**: {search['date_filter']}\n"
            content += f"- **Event Type**: {search['event_type']}\n"
            content += f"- **Total Results**: {search['total_results']}\n"
            content += f"- **Search Time**: {search['search_time']}\n\n"
            content += "---\n\n"
    else:
        content += "No event searches found.\n\n"
        content += "Use the search_events tool to search for events.\n"
    
    return content

@mcp.resource("events://{search_id}")
def get_event_search_details(search_id: str) -> str:
    """
    Get detailed information about a specific event search.
    
    Args:
        search_id: The event search ID to retrieve details for
    """
    file_path = os.path.join(EVENTS_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"# Event Search Not Found: {search_id}\n\nNo event search found with this ID."
    
    try:
        with open(file_path, 'r') as f:
            event_data = json.load(f)
        
        metadata = event_data.get('search_metadata', {})
        events = event_data.get('events_results', [])
        
        content = f"# Event Search: {search_id}\n\n"
        content += f"## Search Details\n"
        content += f"- **Query**: {metadata.get('query', 'N/A')}\n"
        content += f"- **Location**: {metadata.get('location', 'N/A')}\n"
        content += f"- **Date Filter**: {metadata.get('date_filter', 'None')}\n"
        content += f"- **Event Type**: {metadata.get('event_type', 'None')}\n"
        content += f"- **Language**: {metadata.get('language', 'N/A')}\n"
        content += f"- **Country**: {metadata.get('country', 'N/A')}\n"
        content += f"- **Total Results**: {metadata.get('total_results', 0)}\n"
        content += f"- **Search Time**: {metadata.get('search_timestamp', 'N/A')}\n\n"
        
        # Event results
        if events:
            content += f"## Events Found ({len(events)})\n\n"
            for i, event in enumerate(events[:10]):  # Show top 10
                content += f"### {i+1}. {event.get('title', 'N/A')}\n"
                
                # Date information
                date_info = event.get('date', {})
                content += f"- **When**: {date_info.get('when', 'N/A')}\n"
                
                # Location information
                address = event.get('address', [])
                if address:
                    content += f"- **Address**: {', '.join(address)}\n"
                
                # Venue information
                venue = event.get('venue', {})
                if venue:
                    content += f"- **Venue**: {venue.get('name', 'N/A')}"
                    if venue.get('rating'):
                        content += f" (Rating: {venue['rating']}/5, {venue.get('reviews', 0)} reviews)"
                    content += "\n"
                
                # Description
                description = event.get('description', '')
                if description:
                    content += f"- **Description**: {description[:200]}{'...' if len(description) > 200 else ''}\n"
                
                # Ticket information
                ticket_info = event.get('ticket_info', [])
                if ticket_info:
                    content += f"- **Tickets Available**: {len(ticket_info)} sources\n"
                    for ticket in ticket_info[:2]:  # Show first 2 ticket sources
                        content += f"  - {ticket.get('source', 'N/A')}: {ticket.get('link_type', 'info')}\n"
                
                content += f"- **Event Link**: {event.get('link', 'N/A')}\n\n"
                content += "---\n\n"
        else:
            content += "No events found for this search.\n"
        
        return content
        
    except json.JSONDecodeError:
        return f"# Error\n\nCorrupted event data for search ID: {search_id}"

@mcp.prompt()
def event_discovery_prompt(
    location: str,
    interests: str = "",
    date_preference: str = "",
    event_type: str = "",
    budget: str = ""
) -> str:
    """Generate a comprehensive event discovery prompt for Claude."""
    
    prompt = f"""Help me discover interesting events in {location}"""
    
    if interests:
        prompt += f" related to my interests: {interests}"
    
    if date_preference:
        prompt += f" for {date_preference}"
    
    if event_type:
        prompt += f", specifically {event_type} events"
    
    prompt += "."
    
    if budget:
        prompt += f" My budget consideration: {budget}."
    
    prompt += f"""

Please help me find and explore events using the following approach:

1. **Event Search**: Use the search_events tool to find events:
   - Location: {location}
   - Query: {interests if interests else "events"}"""
    
    if date_preference:
        prompt += f"""
   - Date filter: {date_preference}"""
    
    if event_type:
        prompt += f"""
   - Event type: {event_type}"""
    
    prompt += f"""

2. **Event Analysis**: Once events are found, provide:
   - Summary of the most interesting events with highlights
   - Categorization by event type (concerts, festivals, arts, sports, etc.)
   - Date and time analysis for planning
   - Venue information and accessibility
   - Ticket availability and pricing insights

3. **Personalized Recommendations**: Based on my interests and preferences:
   - Top 5 recommended events with detailed reasoning
   - Alternative events that might be of interest
   - Hidden gems or lesser-known events
   - Seasonal or timely events I shouldn't miss

4. **Practical Information**: For recommended events:
   - Venue details and how to get there
   - Parking and transportation options
   - What to expect and how to prepare
   - Ticket purchasing recommendations

5. **Event Planning**: Help me plan around the events:
   - Suggested itineraries if multiple events are selected
   - Nearby restaurants or activities
   - Timing considerations and scheduling tips

Use the event search tools first, then provide comprehensive analysis and personalized recommendations based on the results. Focus on events that align with my interests and preferences."""

    return prompt

@mcp.prompt()
def event_comparison_prompt(search_id: str) -> str:
    """Generate a prompt for detailed event comparison and analysis."""
    
    return f"""Analyze and compare the events from search ID: {search_id}

Please provide a comprehensive analysis including:

1. **Event Overview**: Use get_event_details('{search_id}') to retrieve the complete event data

2. **Event Categorization**:
   - Group events by type (concerts, festivals, arts, sports, networking, etc.)
   - Identify recurring events vs one-time events
   - Highlight free vs paid events

3. **Detailed Comparison**:
   - Date and time analysis (weekday vs weekend, time of day)
   - Venue comparison (indoor vs outdoor, capacity, accessibility)
   - Ticket pricing and availability analysis
   - Duration and format of events

4. **Quality Indicators**:
   - Venue ratings and reviews
   - Event popularity and attendance expectations
   - Organizer reputation and event history

5. **Filtering Recommendations**:
   - Use filter_events_by_date for specific time preferences
   - Use filter_events_by_type for category-specific events
   - Use filter_events_by_venue for preferred locations

6. **Top Recommendations**:
   - Best value events (quality vs price)
   - Most unique or special events
   - Most accessible events
   - Events suitable for different group sizes

7. **Planning Considerations**:
   - Events that can be combined in a single day/weekend
   - Advance booking requirements
   - Weather considerations for outdoor events
   - Transportation and parking logistics

Please format the analysis in a clear, organized structure with specific recommendations for different types of event-goers (families, couples, solo attendees, groups)."""

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')