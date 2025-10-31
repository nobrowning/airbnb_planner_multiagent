# TripAdvisor Vacation Planner MCP Server

This MCP server provides access to TripAdvisor data for planning vacations, finding attractions, restaurants, and hotels.

## Features

- Search for locations by name and category
- Get detailed information about specific locations
- Find nearby attractions, restaurants, and hotels
- View photos and reviews
- Interactive vacation planning prompt

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- TripAdvisor API key (get one from [TripAdvisor Developer Portal](https://developer.tripadvisor.com/))
- Claude Desktop
- Google Maps MCP Server (https://github.com/modelcontextprotocol/servers/tree/main/src/google-maps)

### Installation with uv

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   uv venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   uv add "mcp[cli]"
   ```

### Running the Server

You can run the server directly with:

```bash
# Set your API key as an environment variable
export TRIPADVISOR_API_KEY=your_api_key_here  # Linux/macOS
set TRIPADVISOR_API_KEY=your_api_key_here     # Windows Command Prompt
$env:TRIPADVISOR_API_KEY="your_api_key_here"  # Windows PowerShell

# Run the server
mcp run server.py
```

### Setting up for Claude Desktop

Set up the MCP Server with:

```bash
mcp install server.py
```

### Configuring Claude Desktop

1. Open Claude Desktop
2. Go to Settings > MCP Servers
3. Add a new server with the following configuration:
   ```json
   {
     "tripadvisor": {
       "command": "uv",
       "args": [
         "run",
         "--with",
         "mcp[cli]",
         "mcp",
         "run",
         "PATH_TO_YOUR_PROJECT\\server.py"
       ],
       "env": {
         "TRIPADVISOR_API_KEY": "YOUR_API_KEY_HERE"
       }
     }
   }
   ```
4. Replace `PATH_TO_YOUR_PROJECT` with the absolute path to your project directory
5. Replace `YOUR_API_KEY_HERE` with your actual TripAdvisor API key

### Using the Vacation Planner

1. Start a new conversation in Claude
2. Just prompt anything with "Vacation Planner" prompt
3. Follow the interactive prompts to plan your perfect vacation!

## API Endpoints Used

- Location Search: Find locations by name and category
- Location Details: Get comprehensive information about a location
- Location Photos: View photos of a location
- Location Reviews: Read reviews of a location
- Nearby Search: Find locations near a specific point

## Troubleshooting

- If you see 401 Unauthorized errors, check that your API key is correct and that your IP is whitelisted in the TripAdvisor Developer Portal
- For issues with Claude Desktop integration, verify your configuration settings and ensure the path to server.py is correct
- If Claude is failing to complete, then there is a high chance that you are using too many input tokens. get_location_details_tool is usually the culprit.
