# Airbnb Agent

[中文文档](README_CN.md)

## Overview

Airbnb Agent is a specialized intelligent agent for searching Airbnb listings. Built with Google Agent Development Kit (ADK) and LangGraph, it communicates with other agents via the A2A (Agent-to-Agent) protocol to help users find and filter suitable accommodation options.

**Key Features:**
- Search Airbnb listings by location, dates, and guest count
- Provide detailed listing information (price, ratings, amenities, etc.)
- Filter by price, ratings, and other criteria
- Return listing links, photos, and reviews

**Port:** `10002`

## Getting Started

### Configuration Requirements

1. **Copy Environment Configuration File**

   ```bash
   cd airbnb_agent
   cp "example copy.env" .env
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
cd airbnb_agent
uv run .
```

Once started successfully, the agent will run on **http://0.0.0.0:10002**

### Verify Running Status

Check if the agent is running properly:
- Agent Card: http://localhost:10002/.well-known/agent-card.json
- Health Check: http://localhost:10002/health

## Disclaimer

Important: The sample code provided is for demonstration purposes and illustrates the mechanics of the Agent-to-Agent (A2A) protocol. When building production applications, it is critical to treat any agent operating outside of your direct control as a potentially untrusted entity.

All data received from an external agent—including but not limited to its AgentCard, messages, artifacts, and task statuses—should be handled as untrusted input. For example, a malicious agent could provide an AgentCard containing crafted data in its fields (e.g., description, name, skills.description). If this data is used without sanitization to construct prompts for a Large Language Model (LLM), it could expose your application to prompt injection attacks.  Failure to properly validate and sanitize this data before use can introduce security vulnerabilities into your application.

Developers are responsible for implementing appropriate security measures, such as input validation and secure handling of credentials to protect their systems and users.
