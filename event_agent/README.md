# Event Agent

[中文文档](README_CN.md)

## Overview

Event Agent is a specialized intelligent agent for searching and discovering events. Integrated with Google Events via SerpAPI, it helps users find concerts, festivals, art exhibitions, and various other activities.

**Key Features:**
- Search events by location, date, and type
- Support multiple date filters (today, tomorrow, this week, weekend, next week, this month, or custom dates)
- Filter by event categories (concerts, festivals, virtual events, etc.)
- Provide detailed event information (venue, tickets, time, description)
- Discover events based on user interests

**Port:** `10004`

## Getting Started

### Configuration Requirements

1. **Copy Environment Configuration File**

   ```bash
   cd event_agent
   cp example.env .env
   ```

2. **Configure API Keys**

   Edit the `.env` file with the following configuration:

   ```env
   # Google Gemini API (Required)
   GOOGLE_API_KEY=your_google_api_key_here
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
cd event_agent
uv run .
```

Once started successfully, the agent will run on **http://0.0.0.0:10004**

### Verify Running Status

Check if the agent is running properly:
- Agent Card: http://localhost:10004/.well-known/agent-card.json
- Health Check: http://localhost:10004/health

## Overview

The Event Agent is built on Google's Agent Development Kit (ADK) and integrates with a FastMCP server to provide comprehensive event search capabilities. It helps users discover interesting events based on location, date, and preferences.

## Features

### Event Search Capabilities
- **Location-based Search**: Find events in specific cities or regions
- **Date Filtering**: Search by today, tomorrow, this week, weekend, next week, month, or custom dates
- **Event Type Filtering**: Filter by event categories (concerts, festivals, virtual events, etc.)
- **Detailed Information**: Get venue details, ticket information, dates, times, and descriptions

### MCP Server Tools
The Event Agent uses the following tools provided by the MCP server:

1. **search_events**: Search for events with advanced filters
   - Query-based search
   - Location filtering
   - Date range filtering
   - Event type filtering
   - Language and country customization

2. **get_event_details**: Retrieve detailed information for specific events
3. **filter_events_by_date**: Filter search results by date range
4. **get_event_searches**: List all saved event searches

## Architecture

```
event_agent/
├── event_agent.py          # Main agent definition and configuration
├── event_executor.py       # A2A protocol executor
├── __main__.py            # Entry point for running the agent
├── .env                   # Environment configuration
└── event_server/          # MCP Server
    ├── main.py           # Server entry point
    ├── event_server.py   # Event search implementation
    └── pyproject.toml    # Server dependencies
```

## Configuration

### Environment Variables (.env)

```env
# Google Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here
LITELLM_MODEL=gemini-2.5-flash

# Vertex AI Configuration (Optional)
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# SerpAPI Configuration (Required)
SERPAPI_KEY=your_serpapi_key_here
```

### Required API Keys

1. **Google Gemini API Key** or **Vertex AI Credentials**
   - Get from: https://makersuite.google.com/app/apikey
   - Or set up Vertex AI project

2. **SerpAPI Key** (Required for event search)
   - Get from: https://serpapi.com/
   - Used for Google Events API access

## Installation

1. Install dependencies:
```bash
cd event_agent
pip install -r requirements.txt
```

2. Configure environment variables in `.env`

3. Run the agent:
```bash
uv run .
```

The agent will start on **http://0.0.0.0:10004**

## Usage Examples

### Search for Concerts
```
Find concerts in New York this weekend
```

### Search for Festivals
```
Show me art festivals in Paris next month
```

### Virtual Events
```
Search for virtual tech events this week
```

### Specific Queries
```
Find jazz concerts in San Francisco tomorrow
```

## API Endpoints

- **Agent Card**: `http://localhost:10004/.well-known/agent-card.json`
- **Health Check**: `http://localhost:10004/health`

## Integration

The Event Agent is designed to work as part of the multi-agent travel planning system and can be coordinated by the host agent for comprehensive travel planning.

### Agent Skills

- **Skill ID**: `event_search`
- **Name**: Search Events
- **Tags**: events, activities, concerts, festivals, entertainment

## Data Storage

Event search results are automatically saved in the `events/` directory as JSON files for later reference and analysis.

## Error Handling

The agent includes comprehensive error handling for:
- Missing API keys
- Network failures
- Invalid search parameters
- API rate limits

## Dependencies

Main dependencies:
- `google-adk`: Google Agent Development Kit
- `fastmcp`: FastMCP server framework
- `requests`: HTTP library for API calls
- `python-dotenv`: Environment variable management

## Development

### Project Structure
- Uses Google ADK for agent orchestration
- FastMCP for tool integration
- A2A protocol for agent-to-agent communication
- SerpAPI for event data retrieval

### Running in Development Mode
```bash
python -m event_agent
```

## Troubleshooting

### Common Issues

1. **SERPAPI_KEY not found**
   - Ensure `.env` file contains `SERPAPI_KEY=your_key`
   - Verify the key is valid at https://serpapi.com/

2. **Agent won't start**
   - Check if port 10004 is available
   - Verify all dependencies are installed
   - Check Google API credentials

3. **No events returned**
   - Verify SerpAPI key has remaining credits
   - Check search query formatting
   - Try broader location or date filters

## License

Part of the Tripadvisor-Airbnb Planner Multi-Agent System.
