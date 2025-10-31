# TripAdvisor Agent

A specialized agent for searching TripAdvisor attractions, restaurants, and reviews using the A2A framework and MCP protocol.

## Features

- Search for locations on TripAdvisor
- Find nearby attractions and restaurants
- Get detailed location information and reviews
- Integrated with Google ADK and A2A framework

## Setup

1. Install dependencies (from project root):
   ```bash
   uv sync
   ```

2. Set up environment variables:
   - Copy `.env` and update `TRIPADVISOR_API_KEY` with your actual API key
   - Obtain a TripAdvisor API key from: https://www.tripadvisor.com/developers

3. Run the agent:
   ```bash
   cd D:\airbnb_planner_multiagent-main\tripadvisor_agent
   uv run python -m tripadvisor_agent
   ```

   Or use the PowerShell script from the project root:
   ```powershell
   .\start_tripadvisor.ps1
   ```

## Port

The TripAdvisor agent runs on port **10003** by default.

## Agent Skills

- **ID**: `tripadvisor_search`
- **Name**: Search TripAdvisor
- **Description**: Helps with finding attractions, restaurants, and reviews on TripAdvisor
- **Tags**: tripadvisor, travel, attractions, restaurants

## Example Queries

- "Find restaurants in Paris"
- "Show me attractions near Times Square"
- "What are the best rated hotels in Tokyo?"
- "Find things to do in San Francisco"
