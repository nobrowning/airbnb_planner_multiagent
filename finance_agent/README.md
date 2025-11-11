# Finance Agent

[中文文档](README_CN.md)

## Overview

Finance Agent is a specialized intelligent agent for providing financial market information. Integrated with Google Finance via SerpAPI, it provides real-time stock quotes, currency exchange rates, and financial market analysis data.

**Key Features:**
- Real-time stock price queries
- Currency exchange rate conversion (supporting major world currencies)
- Market overview and index trends
- Historical stock price analysis
- Stock price movement comparison

**Port:** `10005`

## Getting Started

### Configuration Requirements

1. **Copy Environment Configuration File**

   ```bash
   cd finance_agent
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
cd finance_agent
uv run .
```

Once started successfully, the agent will run on **http://0.0.0.0:10005**

### Verify Running Status

Check if the agent is running properly:
- Agent Card: http://localhost:10005/.well-known/agent-card.json
- Health Check: http://localhost:10005/health

## Overview

The Finance Agent provides real-time financial market data, stock information, currency exchange rates, and market analysis through integration with Google's Agent Development Kit and FastMCP.

## Features

### Financial Capabilities
- **Stock Price Lookup**: Real-time stock prices and company information
- **Currency Conversion**: Convert between major world currencies
- **Market Overview**: Get market trends and indices
- **Historical Data**: Analyze past stock performance
- **Price Comparison**: Compare stocks by price movements
- **Market Insights**: Provide financial analysis and trends

### MCP Server Tools

1. **search_stocks**: Search for stocks with detailed information
2. **get_stock_quote**: Get real-time stock quotes
3. **convert_currency**: Real-time currency conversion
4. **get_market_overview**: View market indices and trends
5. **filter_stocks_by_change**: Filter stocks by price movement

## Architecture

```
finance_agent/
├── finance_agent.py       # Main agent definition
├── finance_executor.py    # A2A protocol executor
├── __main__.py           # Entry point
├── .env                  # Environment configuration
└── finance_server/       # MCP Server
    ├── main.py          # Server entry point
    ├── finance_server.py # Finance data implementation
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
cd finance_agent
uv run .
```

The agent will start on **http://0.0.0.0:10005**

## Usage Examples

```
Look up AAPL stock price
Convert 1000 USD to EUR
Show market overview
Compare TSLA and F stock performance
What is the current price of Bitcoin?
```

## API Endpoints

- Agent Card: `http://localhost:10005/.well-known/agent-card.json`
- Health Check: `http://localhost:10005/health`

## Agent Skills

- **Skill ID**: `finance_search`
- **Name**: Financial Data
- **Tags**: finance, stocks, currency, market, trading

## Data Storage

Financial search results are saved in the `finance/` directory for reference.

## Disclaimer

**IMPORTANT**: This agent provides financial information for informational purposes only. It is NOT financial advice and should NOT be used as the sole basis for investment decisions. Always consult with a qualified financial advisor before making investment decisions.

## Troubleshooting

1. **SERPAPI_KEY not found**: Verify `.env` contains valid SERPAPI_KEY
2. **Agent won't start**: Check port 10005 availability
3. **No data returned**: Verify SerpAPI credits and valid stock symbols

## Dependencies

- google-adk: Agent framework
- fastmcp: MCP server
- requests: API communication
- python-dotenv: Environment management

## License

Part of the Tripadvisor-Airbnb Planner Multi-Agent System.
