# Host Agent - Travel Planning Coordinator

The central orchestration agent that coordinates all specialized travel planning agents to provide comprehensive trip planning assistance.

## Overview

The Host Agent acts as the main entry point for users, intelligently routing requests to specialized agents (Weather, Airbnb, TripAdvisor, Events, Finance, Flights, Hotels) and coordinating their responses to deliver comprehensive travel planning solutions.

## Architecture

The Host Agent implements the Agent-to-Agent (A2A) protocol and uses a routing system to delegate tasks to appropriate specialized agents based on the user's query.

```
host_agent/
├── routing_agent.py              # Main routing logic and agent coordination
├── remote_agent_connection.py   # A2A connection management
├── __main__.py                   # Gradio web interface
└── .env                          # Environment configuration
```

## Coordinated Agents

The Host Agent coordinates the following specialized agents:

1. **Weather Agent** (Port 10001)
   - Weather forecasts and conditions

2. **Airbnb Agent** (Port 10002)
   - Accommodation search on Airbnb

3. **TripAdvisor Agent** (Port 10003)
   - Attractions and restaurant recommendations

4. **Event Agent** (Port 10004)
   - Concerts, festivals, and activities

5. **Finance Agent** (Port 10005)
   - Currency conversion and financial data

6. **Flight Agent** (Port 10006)
   - Flight search and comparison

7. **Hotel Agent** (Port 10007)
   - Hotel and accommodation search

## Features

### Intelligent Routing
- Analyzes user queries to determine which agent(s) to invoke
- Routes multi-faceted queries to multiple agents
- Coordinates responses from multiple agents

### Multi-Agent Coordination
- Parallel agent execution for complex queries
- Response aggregation and synthesis
- Error handling and fallback strategies

### User Interface
- **Gradio Web Interface**: Interactive chat interface at http://127.0.0.1:8083
- Real-time streaming responses
- Tool call visualization
- Clean, user-friendly design

### Supported Query Types

#### Weather Queries
```
What's the weather in Los Angeles?
Check weather forecast for Paris next week
```

#### Accommodation Queries
```
Find a room in LA from April 15-18 for 2 adults
Search for hotels in New York under $200
Find vacation rentals in Bali with a pool
```

#### Attraction & Restaurant Queries
```
Find restaurants in Paris
Show me attractions near Times Square
What to do in Tokyo?
```

#### Event Queries
```
Find concerts in New York this weekend
Show me festivals in Austin next month
```

#### Financial Queries
```
Convert 1000 USD to EUR
What's the AAPL stock price?
```

#### Flight Queries
```
Find flights from LAX to JFK on Dec 15
Compare prices for round trip to London
```

#### Complex Multi-Agent Queries
```
Plan a 5-day trip to Paris including flights, hotel, attractions, and events
Find accommodation and restaurants near Central Park
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

# Agent URLs (customize if using different ports)
WEA_AGENT_URL=http://localhost:10001
AIR_AGENT_URL=http://localhost:10002
TRI_AGENT_URL=http://localhost:10003
EVE_AGENT_URL=http://localhost:10004
FIN_AGENT_URL=http://localhost:10005
FLI_AGENT_URL=http://localhost:10006
HOT_AGENT_URL=http://localhost:10007

# Application Settings
APP_URL=http://127.0.0.1:8083
```

## Installation & Running

### Prerequisites

Ensure all specialized agents are running before starting the Host Agent:

```bash
# Start all agents in separate terminals
cd weather_agent && uv run .
cd airbnb_agent && uv run .
cd tripadvisor_agent && uv run .
cd event_agent && uv run .
cd finance_agent && uv run .
cd flight_agent && uv run .
cd hotel_agent && uv run .
```

### Start Host Agent

```bash
cd host_agent
uv run .
```

The Gradio interface will be available at **http://127.0.0.1:8083**

## Usage

1. Open your browser to `http://127.0.0.1:8083`
2. Type your travel planning query in the chat interface
3. The Host Agent will automatically route to appropriate agents
4. View real-time responses and tool calls
5. Ask follow-up questions or refine your request

## Agent Communication Protocol

The Host Agent uses the A2A (Agent-to-Agent) protocol for communication:

- **Protocol Version**: 0.3.0
- **Transport**: JSON-RPC over HTTP
- **Features**: Streaming responses, task management, state tracking

## Error Handling

The Host Agent includes robust error handling for:
- Agent unavailability (503 errors with retry logic)
- Network timeouts (300-second timeout for card resolution)
- Invalid queries (graceful error messages)
- Agent failures (fallback to available agents)

## Response Features

### Tool Call Visualization
```
🛠️ Tool Call: search_hotels
{
  "location": "Paris",
  "check_in_date": "2025-06-15",
  "check_out_date": "2025-06-20",
  ...
}
```

### Tool Response Display
```
⚡ Tool Response from search_hotels
{
  "total_properties": 150,
  "price_range": {"min": 80, "max": 500},
  ...
}
```

## Debugging

### Check Agent Status

Visit the agent card endpoints to verify agents are running:
- Weather: http://localhost:10001/.well-known/agent-card.json
- Airbnb: http://localhost:10002/.well-known/agent-card.json
- (etc.)

### Common Issues

1. **503 Errors**: Ensure all required agents are running
2. **Gradio Warnings**: Update to latest Gradio version with `type='messages'`
3. **Connection Timeouts**: Check network and firewall settings
4. **Agent Not Found**: Verify agent URLs in `.env` match running services

## Development

### Adding New Agents

1. Add agent URL to `.env`
2. Update `routing_agent.py` to include new agent in initialization
3. Restart Host Agent

### Customizing Routing Logic

Edit `routing_agent.py` to modify how queries are routed to agents based on keywords, intent, or other criteria.

## Dependencies

- google-adk: Agent Development Kit
- gradio: Web interface
- httpx: HTTP client for A2A communication
- a2a-client: A2A protocol implementation
- python-dotenv: Environment management

## Architecture Diagram

```
User → Gradio UI → Host Agent → Routing Agent
                                       ↓
                    ┌──────────────────┼──────────────────┐
                    ↓                  ↓                  ↓
              Weather Agent    TripAdvisor Agent   Event Agent
              Airbnb Agent     Finance Agent       Flight Agent
                               Hotel Agent
```

## Performance

- **Concurrent Agent Calls**: Supports parallel execution
- **Streaming Responses**: Real-time response streaming
- **Connection Pooling**: Efficient HTTP connection reuse
- **Timeout Management**: Configurable timeouts per agent

## License

Part of the Tripadvisor-Airbnb Planner Multi-Agent System.

## Support

For issues or questions:
1. Check agent logs for error messages
2. Verify all agents are running and accessible
3. Review environment configuration
4. Check network connectivity between agents
