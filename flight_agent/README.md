# Flight Agent

[中文文档](README_CN.md)

## Overview

Flight Agent is a specialized intelligent agent for searching flights, comparing prices, and planning air travel. Integrated with Google Flights via SerpAPI, it helps users find round-trip, one-way, and multi-city flights with comprehensive pricing and schedule information.

**Key Features:**
- Search round-trip, one-way, and multi-city flights
- Compare prices and flight times across airlines
- Filter by price, airline, stops, and duration
- Provide detailed flight information (layovers, aircraft type, baggage policies, etc.)
- Identify best value flights

**Port:** `10006`

## Getting Started

### Configuration Requirements

1. **Copy Environment Configuration File**

   ```bash
   cd flight_agent
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
cd flight_agent
uv run .
```

Once started successfully, the agent will run on **http://0.0.0.0:10006**

### Verify Running Status

Check if the agent is running properly:
- Agent Card: http://localhost:10006/.well-known/agent-card.json
- Health Check: http://localhost:10006/health

## Overview

The Flight Agent helps users find and compare flight options for round trips, one-way journeys, and multi-city itineraries with comprehensive pricing and schedule information.

## Features

### Flight Search Capabilities
- **Multi-Trip Types**: Round trip, one-way, and multi-city searches
- **Flexible Dates**: Search across date ranges
- **Price Comparison**: Compare prices across airlines
- **Flight Filtering**: Filter by price, airline, stops, and duration
- **Detailed Information**: Layovers, aircraft type, baggage policies
- **Best Value Analysis**: Identify optimal price/duration combinations

### MCP Server Tools

1. **search_flights**: Search flights with advanced filters
   - Departure and arrival airports
   - Outbound and return dates
   - Passenger count (adults, children, infants)
   - Travel class (Economy, Premium, Business, First)
   - Currency preferences

2. **get_flight_details**: Retrieve detailed flight information
3. **filter_flights_by_price**: Filter by price range
4. **filter_flights_by_airline**: Filter by specific airlines
5. **get_flight_searches**: List all saved searches

## Architecture

```
flight_agent/
├── flight_agent.py        # Main agent definition
├── flight_executor.py     # A2A protocol executor
├── __main__.py           # Entry point
├── .env                  # Environment configuration
└── flight_server/        # MCP Server
    ├── main.py          # Server entry point
    ├── flight_server.py # Flight search implementation
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
cd flight_agent
uv run .
```

The agent will start on **http://0.0.0.0:10006**

## Usage Examples

### Round Trip Flights
```
Find flights from LAX to JFK on December 15, returning December 22
```

### One-Way Flights
```
Search one-way flights from San Francisco to Tokyo on Jan 10
```

### Multi-City
```
Plan multi-city trip: NYC to Paris to Rome to NYC
```

### Price Comparison
```
Compare flight prices to London for 2 adults next month
```

### Specific Airlines
```
Show me Delta flights from Seattle to Atlanta
```

## API Endpoints

- Agent Card: `http://localhost:10006/.well-known/agent-card.json`
- Health Check: `http://localhost:10006/health`

## Agent Skills

- **Skill ID**: `flight_search`
- **Name**: Flight Search
- **Tags**: flights, travel, booking, airlines, airfare

## Data Storage

Flight search results are saved in the `flights/` directory as JSON files.

## Travel Classes

1. **Economy** (1): Standard seating
2. **Premium Economy** (2): Extra legroom
3. **Business** (3): Business class
4. **First** (4): First class

## Troubleshooting

1. **SERPAPI_KEY not found**: Check `.env` file
2. **No flights found**: Verify airport codes (IATA format: LAX, JFK, etc.)
3. **Invalid dates**: Use YYYY-MM-DD format
4. **API limits**: Check SerpAPI credit balance

## Dependencies

- google-adk: Agent framework
- fastmcp: MCP server
- requests: API communication
- python-dotenv: Environment management

## License

Part of the Tripadvisor-Airbnb Planner Multi-Agent System.
