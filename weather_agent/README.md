# Weather Agent

[中文文档](README_CN.md)

## Overview

Weather Agent is a specialized intelligent agent for providing weather information. Built on Google Agent Development Kit (ADK), it communicates with other agents via the A2A (Agent-to-Agent) protocol to provide accurate weather forecasts and meteorological data.

**Key Features:**
- Query current weather conditions for specified locations
- Provide weather forecasts for upcoming days
- Support weather queries for major cities worldwide
- Return detailed meteorological data (temperature, humidity, precipitation probability, etc.)

**Port:** `10001`

## Getting Started

### Configuration Requirements

1. **Copy Environment Configuration File**

   ```bash
   cd weather_agent
   cp example.env .env
   ```

2. **Configure API Keys**

   Edit the `.env` file with the following configuration:

   ```env
   # For Gemini Developer API
   GOOGLE_API_KEY="your_google_api_key"

   # Or use Vertex AI
   GOOGLE_GENAI_MODEL="gemini-2.5-flash"
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT="your_project_id"
   GOOGLE_CLOUD_LOCATION="global"
   ```

   **Get API Keys:**
   - Google Gemini API Key: https://makersuite.google.com/app/apikey
   - Vertex AI: Set up a Google Cloud project

### Launch Command

```bash
cd weather_agent
uv run .
```

Once started successfully, the agent will run on **http://0.0.0.0:10001**

### Verify Running Status

Check if the agent is running properly:
- Agent Card: http://localhost:10001/.well-known/agent-card.json
- Health Check: http://localhost:10001/health

## Running the example

1. Create a .env file using the `example.env` file as a template.

2. Run the example

   ```bash
   uv run .
   ```
