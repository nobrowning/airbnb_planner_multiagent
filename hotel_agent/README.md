# Hotel Agent

[中文文档](README_CN.md)

## Overview

Hotel Agent is a specialized intelligent agent for searching hotels and accommodations. Integrated with Google Hotels via SerpAPI, it provides comprehensive hotel search capabilities with various filtering options to help users find the perfect accommodation.

**Key Features:**
- Search multiple accommodation types (hotels, resorts, vacation rentals, apartments, etc.)
- Filter by price, rating, amenities, star rating, and property type
- Provide detailed information (room types, facilities, policies, reviews)
- Compare prices and ratings across properties
- Support free cancellation and special offers filtering

**Port:** `10007`

## Getting Started

### Configuration Requirements

1. **Copy Environment Configuration File**

   ```bash
   cd hotel_agent
   cp example.env .env
   ```

2. **Configure API Keys**

   Edit the `.env` file with the following configuration:

   ```env
   # Google Gemini API (Required)
   GOOGLE_API_KEY=your_google_api_key
   LITELLM_MODEL=gemini-2.5-flash

   # Vertex AI (Optional)
   GOOGLE_GENAI_USE_VERTEXAI=True
   GOOGLE_CLOUD_PROJECT=your_project_id
   GOOGLE_CLOUD_LOCATION=global
   GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

   # SerpAPI (Required)
   SERPAPI_KEY=your_serpapi_key_here
   ```

   **Get API Keys:**
   - Google Gemini API Key: https://makersuite.google.com/app/apikey
   - SerpAPI Key: https://serpapi.com/

### Launch Command

```bash
cd hotel_agent
uv run .
```

Once started successfully, the agent will run on **http://0.0.0.0:10007**

### Verify Running Status

Check if the agent is running properly:
- Agent Card: http://localhost:10007/.well-known/agent-card.json
- Health Check: http://localhost:10007/health

## Overview

The Hotel Agent provides comprehensive hotel and accommodation search capabilities with advanced filtering options for finding the perfect place to stay.

## Features

### Accommodation Search Capabilities
- **Multiple Property Types**: Hotels, resorts, vacation rentals, apartments, B&Bs
- **Advanced Filtering**: Price, rating, amenities, hotel class, property type
- **Detailed Information**: Room types, facilities, policies, reviews
- **Price Comparison**: Compare rates across properties
- **Location Analysis**: Neighborhood insights and proximity to attractions
- **Flexible Booking**: Free cancellation options and special offers

### MCP Server Tools

1. **search_hotels**: Search accommodations with comprehensive filters
   - Location and dates
   - Guest count (adults, children with ages)
   - Currency preferences
   - Sort options (price, rating, reviews)
   - Hotel class (2-5 stars)
   - Amenities filtering
   - Property type filtering
   - Free cancellation and special offers

2. **get_hotel_details**: Detailed property information
3. **get_property_details**: Specific property details by token
4. **filter_hotels_by_price**: Filter by price range
5. **filter_hotels_by_rating**: Filter by minimum rating
6. **filter_hotels_by_amenities**: Filter by required amenities
7. **filter_hotels_by_class**: Filter by hotel star rating

## Architecture

```
hotel_agent/
├── hotel_agent.py         # Main agent definition
├── hotel_executor.py      # A2A protocol executor
├── __main__.py           # Entry point
├── .env                  # Environment configuration
└── hotel_server/         # MCP Server
    ├── main.py          # Server entry point
    ├── hotel_server.py  # Hotel search implementation
    └── pyproject.toml   # Server dependencies
```

## Configuration

### Environment Variables (.env)

```env
# Google Gemini API
GOOGLE_API_KEY=your_google_api_key
LITELLM_MODEL=gemini-2.5-flash

# Vertex AI (Optional)
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# SerpAPI (Required)
SERPAPI_KEY=your_serpapi_key_here
```

## Installation & Running

```bash
cd hotel_agent
uv run .
```

The agent will start on **http://0.0.0.0:10007**

## Usage Examples

### Basic Hotel Search
```
Find hotels in Paris from June 15 to June 20 for 2 adults
```

### Luxury Hotels
```
Search for 5-star hotels in New York with ratings above 4.5
```

### Budget Accommodations
```
Show me hotels in London under $150 per night
```

### Vacation Rentals
```
Find vacation rentals in Bali with a pool and 3 bedrooms
```

### Specific Amenities
```
Search for hotels near Times Square with free Wi-Fi, gym, and free cancellation
```

### Family-Friendly
```
Find family-friendly hotels in Orlando with 4+ rating and kids' facilities
```

## Filter Options

### Price Filters
- Minimum price per night
- Maximum price per night
- Currency selection

### Quality Filters
- Minimum overall rating (1-5)
- Hotel class (2-5 stars)
- Review count threshold

### Amenity Filters
- Pool, Spa, Gym, Restaurant
- Free Wi-Fi, Parking
- Pet-friendly, Wheelchair accessible
- Kitchen, Laundry facilities

### Property Types
- Hotels, Resorts, Motels
- Vacation rentals, Apartments
- B&Bs, Guesthouses
- Hostels, Lodges

### Booking Features
- Free cancellation
- Special offers
- Pay at property options

## API Endpoints

- Agent Card: `http://localhost:10007/.well-known/agent-card.json`
- Health Check: `http://localhost:10007/health`

## Agent Skills

- **Skill ID**: `hotel_search`
- **Name**: Hotel Search
- **Tags**: hotels, accommodation, lodging, vacation rentals, resorts

## Data Storage

Hotel search results are saved in the `hotels/` directory as JSON files for future reference.

## Sort Options

1. **Lowest Price** (3): Sort by cheapest first
2. **Highest Rating** (8): Sort by guest rating
3. **Most Reviewed** (13): Sort by review count

## Troubleshooting

1. **SERPAPI_KEY not found**: Verify `.env` contains valid key
2. **No results found**: Broaden search criteria or try different dates
3. **Invalid dates**: Use YYYY-MM-DD format
4. **Port conflict**: Check if port 10007 is available

## Dependencies

- google-adk: Agent framework
- fastmcp: MCP server framework
- requests: HTTP communication
- python-dotenv: Environment management

## Best Practices

1. **Search Early**: Popular destinations book quickly
2. **Flexible Dates**: Check prices for nearby dates
3. **Read Reviews**: Pay attention to recent guest reviews
4. **Check Policies**: Review cancellation and refund policies
5. **Verify Location**: Confirm proximity to attractions

## License

Part of the Tripadvisor-Airbnb Planner Multi-Agent System.
