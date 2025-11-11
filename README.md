# Multi-Agent Travel Planning System

[中文文档](README_CN.md) | [English](README.md)

----
> **⚠️ DISCLAIMER**: THIS DEMO IS INTENDED FOR DEMONSTRATION PURPOSES ONLY. IT IS NOT INTENDED FOR USE IN A PRODUCTION ENVIRONMENT.
>
> **⚠️ Important:** A2A is a work in progress (WIP). In the near future there might be changes that differ from what is demonstrated here.
>
> **⚠️ Security Notice**: When building production applications, treat all external agents as potentially untrusted entities. All data received from external agents—including AgentCard, messages, artifacts, and task statuses—should be handled as untrusted input and properly validated to prevent security vulnerabilities such as prompt injection attacks.
----

A comprehensive travel planning system built with Agent2Agent (A2A) protocol and Google Agent Development Kit (ADK). The system features a host agent that intelligently coordinates 7 specialized agents to provide end-to-end travel planning services including flights, hotels, Airbnb, weather, events, attractions, restaurants, and financial information.

## 🌟 Key Features

- **Intelligent Multi-Agent Coordination**: Host agent orchestrates 7 specialized agents
- **Real-time Information**: Live weather, flight prices, hotel availability, and event listings
- **Comprehensive Travel Planning**: One-stop solution for all travel needs
- **Interactive Web Interface**: User-friendly Gradio-based chat interface
- **A2A Protocol**: Industry-standard agent-to-agent communication
- **MCP Integration**: Model Context Protocol for tool interactions

## 🏗️ System Architecture

The system uses a hub-and-spoke architecture where the Host Agent coordinates all specialized agents:

```
┌──────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│                   (Gradio Web UI - Port 8083)                │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                       Host Agent                             │
│          (Intelligent Request Router & Coordinator)          │
└──┬────────┬────────┬────────┬────────┬────────┬─────────┬────┘
   │        │        │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼        ▼        ▼
┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐
│Weather││Airbnb ││ Trip  ││ Event ││Finance││Flight ││ Hotel │
│ 10001 ││ 10002 ││Advisor││ 10004 ││ 10005 ││ 10006 ││ 10007 │
│       ││       ││ 10003 ││       ││       ││       ││       │
└───────┘└───────┘└───────┘└───────┘└───────┘└───────┘└───────┘
```

## 🤖 Specialized Agents

### 1. **Host Agent** (Port 8083)
**Purpose**: Central coordination agent and user interface

**Capabilities**:
- Intelligent query analysis and routing to appropriate specialized agents
- Multi-agent response coordination and synthesis
- Real-time streaming interface with Gradio Web UI
- Complex multi-agent query decomposition
- Parallel agent execution for comprehensive results

**Tech Stack**: Google ADK, Gradio, A2A Protocol, LiteLLM

**API Requirements**:
- Google Gemini API Key or Vertex AI credentials

[Documentation](host_agent/README.md) | [中文文档](host_agent/README_CN.md)

---

### 2. **Weather Agent** (Port 10001)
**Purpose**: Weather forecasts and meteorological information

**Capabilities**:
- Current weather conditions by location
- Multi-day weather forecasts
- Global city coverage
- Detailed meteorological data (temperature, humidity, precipitation probability)
- Weather alerts and warnings

**Tech Stack**: Google ADK, FastMCP, Weather APIs

**API Requirements**:
- Google Gemini API Key or Vertex AI credentials

[Documentation](weather_agent/README.md) | [中文文档](weather_agent/README_CN.md)

---

### 3. **Airbnb Agent** (Port 10002)
**Purpose**: Airbnb accommodation search and booking assistance

**Capabilities**:
- Search Airbnb listings by location, dates, and guest count
- Filter by price, ratings, and amenities
- Detailed property information (reviews, photos, host details)
- Availability checking for specific dates
- Support for various property types

**Tech Stack**: Google ADK, LangGraph, MCP, React Agent

**API Requirements**:
- Google Gemini API Key or Vertex AI credentials

[Documentation](airbnb_agent/README.md) | [中文文档](airbnb_agent/README_CN.md)

---

### 4. **TripAdvisor Agent** (Port 10003)
**Purpose**: Attractions and restaurant recommendations

**Capabilities**:
- Search locations and attractions on TripAdvisor
- Find nearby restaurants and dining venues
- Detailed reviews and rating information
- Photo galleries and user-generated content
- Support for major global travel destinations

**Tech Stack**: Google ADK, FastMCP, TripAdvisor API

**API Requirements**:
- Google Gemini API Key or Vertex AI credentials
- TripAdvisor API Key

[Documentation](tripadvisor_agent/README.md) | [中文文档](tripadvisor_agent/README_CN.md)

---

### 5. **Event Agent** (Port 10004)
**Purpose**: Event discovery and activity planning

**Capabilities**:
- Search events by location, date, and type
- Multiple date filters (today, tomorrow, this week, weekend, next week, this month, custom dates)
- Filter by event categories (concerts, festivals, virtual events, etc.)
- Detailed event information (venue, tickets, time, description)
- Interest-based event recommendations

**Tech Stack**: Google ADK, FastMCP, SerpAPI (Google Events)

**API Requirements**:
- Google Gemini API Key or Vertex AI credentials
- SerpAPI Key

[Documentation](event_agent/README.md) | [中文文档](event_agent/README_CN.md)

---

### 6. **Finance Agent** (Port 10005)
**Purpose**: Financial market data and currency conversion

**Capabilities**:
- Real-time stock price queries and quotes
- Currency exchange rate conversion (supporting major world currencies)
- Market overview, trends, and indices
- Historical stock price analysis
- Stock price movement comparison and filtering

**Tech Stack**: Google ADK, FastMCP, SerpAPI (Google Finance)

**API Requirements**:
- Google Gemini API Key or Vertex AI credentials
- SerpAPI Key

**Disclaimer**: Provides financial information for informational purposes only. NOT financial advice.

[Documentation](finance_agent/README.md) | [中文文档](finance_agent/README_CN.md)

---

### 7. **Flight Agent** (Port 10006)
**Purpose**: Flight search and comparison

**Capabilities**:
- Search round-trip, one-way, and multi-city flights
- Price comparison across airlines and dates
- Filter by price, airline, stops, and duration
- Detailed flight information (layovers, aircraft type, baggage policies)
- Identify best value flights based on price/duration
- Support for multiple passenger types and travel classes

**Tech Stack**: Google ADK, FastMCP, SerpAPI (Google Flights)

**API Requirements**:
- Google Gemini API Key or Vertex AI credentials
- SerpAPI Key

[Documentation](flight_agent/README.md) | [中文文档](flight_agent/README_CN.md)

---

### 8. **Hotel Agent** (Port 10007)
**Purpose**: Hotel and accommodation search

**Capabilities**:
- Search multiple accommodation types (hotels, resorts, vacation rentals, apartments, B&Bs)
- Advanced filtering (price, rating, amenities, star rating, property type)
- Detailed property information (room types, facilities, policies, reviews)
- Price comparison across properties
- Free cancellation and special offers filtering
- Location analysis and proximity to attractions

**Tech Stack**: Google ADK, FastMCP, SerpAPI (Google Hotels)

**API Requirements**:
- Google Gemini API Key or Vertex AI credentials
- SerpAPI Key

[Documentation](hotel_agent/README.md) | [中文文档](hotel_agent/README_CN.md)

## 🚀 Quick Start

### Prerequisites

1. **Python 3.13+** (required for A2A SDK)
2. **uv** - Fast Python package manager
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. **API Keys**:
   - **Google Gemini API Key** (Required for all agents)
     - Get it: https://makersuite.google.com/app/apikey
     - OR **Vertex AI credentials** for production
   - **SerpAPI Key** (Required for Flight, Hotel, Event, Finance agents)
     - Get it: https://serpapi.com/
   - **TripAdvisor API Key** (Required for TripAdvisor agent)
     - Get it: https://www.tripadvisor.com/developers

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd airbnb_planner_multiagent
   ```

2. **Setup Configuration**

   Copy the example configuration file:
   ```bash
   cp .env.example .env
   ```

3. **Configure .env file**

   Edit the `.env` file and configure your credentials:

   **Option A: Gemini Developer API (Recommended for Development)**
   ```env
   # Google Gemini API
   GOOGLE_API_KEY="your-api-key-here"
   GOOGLE_GENAI_MODEL="gemini-2.5-flash"
   ```

   **Option B: Vertex AI (Recommended for Production)**
   ```env
   # Vertex AI Configuration
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT="your-project-id"
   GOOGLE_CLOUD_LOCATION="global"
   GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   GOOGLE_GENAI_MODEL="gemini-2.5-flash"
   ```

   **Add Additional API Keys**:
   ```env
   # SerpAPI (Required for Flight, Hotel, Event, Finance agents)
   SERPAPI_KEY=your_serpapi_key_here

   # TripAdvisor API (Required for TripAdvisor agent)
   TRIPADVISOR_API_KEY=your_tripadvisor_api_key

   # Agent URLs (Default ports - usually no need to change)
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

### Running the System

The system consists of **8 agents** that must run simultaneously. The Host Agent (port 8083) coordinates all other agents, so it must start **last**.

**Option 1: Automated Startup with Control Script (Recommended)**

The `agent_control.sh` script provides unified management for all agents:

```bash
# Start all agents in the correct order
./agent_control.sh start
# Or simply:
./agent_control.sh

# Check status of all agents
./agent_control.sh status

# View all log files
./agent_control.sh logs

# View specific agent log
./agent_control.sh logs weather_agent

# Stop all agents gracefully
./agent_control.sh stop

# Clean log files
./agent_control.sh clean

# Show help
./agent_control.sh help
```

**What the script does:**
1. Starts all 7 specialized agents (Weather, Airbnb, TripAdvisor, Event, Finance, Flight, Hotel)
2. Waits for them to initialize (default: 5 seconds)
3. Starts the Host Agent with Gradio UI
4. Provides log files in the `logs/` directory
5. Handles graceful shutdown on Ctrl+C

**Option 2: Manual Startup (For Development/Debugging)**

Start each agent in a **separate terminal window**:

```bash
# Terminal 1 - Weather Agent (Port 10001)
cd weather_agent && uv run .

# Terminal 2 - Airbnb Agent (Port 10002)
cd airbnb_agent && uv run .

# Terminal 3 - TripAdvisor Agent (Port 10003)
cd tripadvisor_agent && uv run .

# Terminal 4 - Event Agent (Port 10004)
cd event_agent && uv run .

# Terminal 5 - Finance Agent (Port 10005)
cd finance_agent && uv run .

# Terminal 6 - Flight Agent (Port 10006)
cd flight_agent && uv run .

# Terminal 7 - Hotel Agent (Port 10007)
cd hotel_agent && uv run .

# Terminal 8 - Host Agent (Port 8083) - MUST START LAST
cd host_agent && uv run .
```

**⚠️ Important**: Wait 5-10 seconds after starting all specialized agents before starting the Host Agent to ensure all agents are fully initialized.

### Access the Application

Once all agents are running, open your browser and navigate to:

**http://127.0.0.1:8083**

You should see the Gradio chat interface ready for your travel planning queries.

## 💬 Example Queries

### Weather Queries
```
What's the weather in Los Angeles?
Check weather forecast for Paris next week
```

### Accommodation Queries
```
Find a room in LA from April 15-18 for 2 adults
Search for hotels in New York under $200
Find vacation rentals in Bali with a pool
```

### Attraction & Restaurant Queries
```
Find restaurants in Paris
Show me attractions near Times Square
What to do in Tokyo?
```

### Event Queries
```
Find concerts in New York this weekend
Show me festivals in Austin next month
```

### Financial Queries
```
Convert 1000 USD to EUR
What's the AAPL stock price?
```

### Flight Queries
```
Find flights from LAX to JFK on Dec 15
Compare prices for round trip to London
```

### Complex Multi-Agent Queries
```
Plan a 5-day trip to Paris including flights, hotel, attractions, and events
Find accommodation and restaurants near Central Park
What's the weather in Tokyo and find events this weekend?
```

## 🔧 Configuration & Management

### Configuration Architecture

The system uses a **simplified two-file configuration**:

1. **`.env`** - Application configuration (API keys, credentials, agent URLs)
2. **`agent_control.sh`** - Unified control script (agent definitions, ports, and all commands)

**Benefits**:
- ✅ **70% fewer files** - 2 files instead of 4+
- ✅ **No duplication** - Ports and configuration defined once
- ✅ **Single interface** - One command for everything
- ✅ **Easier maintenance** - Edit configuration in one place
- ✅ **Compatible** - Works with bash 3.2+

### Agent Control Script

The `agent_control.sh` script is your **unified control center** for all operations:

```bash
# Start all agents (default command)
./agent_control.sh
./agent_control.sh start      # Explicit start

# Check status of all agents
./agent_control.sh status

# View logs
./agent_control.sh logs                # List all available logs
./agent_control.sh logs weather_agent  # View specific agent log
./agent_control.sh logs host_agent     # View Host Agent log

# Stop all agents gracefully
./agent_control.sh stop

# Clean log files
./agent_control.sh clean

# Migrate from old configuration
./agent_control.sh migrate

# Show help and available commands
./agent_control.sh help
```

### Customizing Agent Ports

To change agent ports or add new agents, edit `agent_control.sh` and modify the `AGENT_CONFIGS` array:

```bash
# In agent_control.sh
AGENT_CONFIGS=(
    "weather_agent:10001"
    "airbnb_agent:10002"
    "tripadvisor_agent:10003"
    "event_agent:10004"
    "finance_agent:10005"
    "flight_agent:10006"
    "hotel_agent:10007"
    "your_new_agent:10008"    # Add new agent here
)
```

After modifying ports in `agent_control.sh`, remember to update corresponding URLs in `.env`:

```env
YOUR_NEW_AGENT_URL=http://localhost:10008
```

### Adjusting Timing Parameters

Edit timing variables in `agent_control.sh` if agents need more time to start:

```bash
# In agent_control.sh
AGENT_STARTUP_DELAY=1      # Delay between starting each sub-agent (seconds)
AGENT_INIT_WAIT=5          # Wait time for sub-agents to initialize (seconds)
HOST_STARTUP_WAIT=3        # Wait time after starting host agent (seconds)
```

**When to adjust:**
- Increase `AGENT_STARTUP_DELAY` if agents fail to start due to resource constraints
- Increase `AGENT_INIT_WAIT` if the Host Agent shows "503 Service Unavailable" errors
- Increase `HOST_STARTUP_WAIT` if the UI becomes available before agents are ready

## 📊 System Status & Monitoring

### Check Agent Health

Visit agent card endpoints:
- Weather: http://localhost:10001/.well-known/agent-card.json
- Airbnb: http://localhost:10002/.well-known/agent-card.json
- TripAdvisor: http://localhost:10003/.well-known/agent-card.json
- Event: http://localhost:10004/.well-known/agent-card.json
- Finance: http://localhost:10005/.well-known/agent-card.json
- Flight: http://localhost:10006/.well-known/agent-card.json
- Hotel: http://localhost:10007/.well-known/agent-card.json

### View Logs

```bash
# List all logs
./agent_control.sh logs

# View specific agent log
./agent_control.sh logs weather_agent

# Real-time monitoring
tail -f logs/*.log
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. **Agent won't start**

**Symptoms**: Agent fails to launch or exits immediately

**Solutions**:
```bash
# Check if port is already in use
lsof -i :<port>
# macOS/Linux: Kill process using the port
kill -9 <PID>

# Verify .env file exists and is properly formatted
ls -la .env
cat .env

# Check uv is installed and in PATH
which uv
uv --version

# Verify Python version
python --version  # Should be 3.13+

# Check agent-specific logs
./agent_control.sh logs <agent_name>
```

#### 2. **503 Service Unavailable Errors**

**Symptoms**: Host Agent shows "503 Service Unavailable" when trying to contact other agents

**Solutions**:
```bash
# Ensure all required agents are running
./agent_control.sh status

# Check agent health by visiting agent cards
curl http://localhost:10001/.well-known/agent-card.json
curl http://localhost:10002/.well-known/agent-card.json
# ... (check all agents)

# Verify agent URLs in .env match running services
grep "_URL" .env

# Increase initialization wait time in agent_control.sh
# Edit: AGENT_INIT_WAIT=10  (increase from 5 to 10 seconds)
```

#### 3. **API Key Errors**

**Symptoms**: "Invalid API Key", "Unauthorized", "Authentication failed"

**Solutions**:
```bash
# Verify .env file has all required keys
cat .env | grep -E "(GOOGLE_API_KEY|SERPAPI_KEY|TRIPADVISOR_API_KEY)"

# Check API key validity
# Google Gemini: Visit https://makersuite.google.com/app/apikey
# SerpAPI: Check https://serpapi.com/dashboard
# TripAdvisor: Check https://www.tripadvisor.com/developers

# For Vertex AI users, verify credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
gcloud auth application-default login

# Check API quota and limits
# Google Cloud Console: https://console.cloud.google.com/apis/dashboard
# SerpAPI Dashboard: https://serpapi.com/dashboard
```

#### 4. **Connection Timeouts**

**Symptoms**: Agents time out when communicating

**Solutions**:
```bash
# Check firewall settings (macOS)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Verify agents are listening on correct ports
lsof -i :10001
lsof -i :10002
# ... (check all ports)

# Test connectivity between agents
curl -X GET http://localhost:10001/.well-known/agent-card.json

# Check for network issues
ping localhost
```

#### 5. **uv not found**

**Symptoms**: "command not found: uv"

**Solutions**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.cargo/bin:$PATH"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

#### 6. **Port Already in Use**

**Symptoms**: "Address already in use", "Port XXX is already allocated"

**Solutions**:
```bash
# Find process using the port
lsof -i :10001

# Kill the process (replace <PID> with actual process ID)
kill -9 <PID>

# Or change port in agent_control.sh
# Edit AGENT_CONFIGS array with new port numbers
```

### Debug Commands

```bash
# Check overall system status
./agent_control.sh status

# View recent logs for specific agent
./agent_control.sh logs weather_agent
./agent_control.sh logs host_agent

# View real-time logs for all agents
tail -f logs/*.log

# Stop all stuck processes gracefully
./agent_control.sh stop

# Force kill all agent processes if needed
pkill -9 -f "uv run.*agent"

# Verify configuration is loaded
source .env && env | grep -E "(GOOGLE|SERP|TRIP)"

# Test individual agent in isolation
cd weather_agent
uv run .
# Press Ctrl+C to stop

# Check if all dependencies are installed
cd <agent_name>
uv sync

# Clean and restart
./agent_control.sh stop
./agent_control.sh clean
./agent_control.sh start
```

### Verification Checklist

Before starting the system, verify:

- [ ] Python 3.13+ is installed: `python --version`
- [ ] uv is installed: `uv --version`
- [ ] `.env` file exists and contains all required API keys
- [ ] No processes are using ports 8083, 10001-10007
- [ ] All API keys are valid and have sufficient quota
- [ ] Network connectivity is working: `ping localhost`

### Getting Help

If you're still experiencing issues:

1. Check the agent-specific README in each agent directory
2. Review the logs: `./agent_control.sh logs`
3. Verify your configuration matches `.env.example`
4. Check the A2A protocol documentation: https://github.com/google/a2a-python
5. Review Google ADK documentation: https://google.github.io/adk-docs/

## 📁 Project Structure

```
airbnb_planner_multiagent/
├── .env                      # 🔑 Configuration (API keys, credentials, agent URLs)
├── .env.example              # 📝 Configuration template
├── agent_control.sh          # 🎯 Unified control script (start/stop/status/logs)
├── migrate_config.sh         # 🔄 Migration helper for old configs
├── README.md                 # 📖 This file (English)
├── README_CN.md              # 📖 Chinese documentation
├── CONFIG.md                 # ⚙️  Configuration guide (merged into README)
├── STARTUP.md                # 🚀 Startup guide (merged into README)
├── CLAUDE.md                 # 🤖 Claude Code instructions
│
├── weather_agent/            # ☁️  Weather Agent (Port 10001)
│   ├── weather_agent.py
│   ├── weather_executor.py
│   ├── weather_mcp.py       # MCP server for weather tools
│   ├── __main__.py
│   ├── .env → ../. env       # Uses root .env
│   └── README.md
│
├── airbnb_agent/            # 🏠 Airbnb Agent (Port 10002)
│   ├── airbnb_agent.py      # LangGraph React agent
│   ├── agent_executor.py    # A2A executor
│   ├── __main__.py
│   ├── .env → ../.env       # Uses root .env
│   └── README.md
│
├── tripadvisor_agent/       # 🗺️  TripAdvisor Agent (Port 10003)
│   ├── tripadvisor_agent.py
│   ├── tripadvisor_executor.py
│   ├── tripadvisor_server/  # MCP server
│   ├── __main__.py
│   ├── .env → ../.env       # Uses root .env
│   └── README.md
│
├── event_agent/             # 🎉 Event Agent (Port 10004)
│   ├── event_agent.py
│   ├── event_executor.py
│   ├── event_server/        # MCP server for SerpAPI events
│   ├── __main__.py
│   ├── .env → ../.env       # Uses root .env
│   └── README.md
│
├── finance_agent/           # 💰 Finance Agent (Port 10005)
│   ├── finance_agent.py
│   ├── finance_executor.py
│   ├── finance_server/      # MCP server for financial data
│   ├── __main__.py
│   ├── .env → ../.env       # Uses root .env
│   └── README.md
│
├── flight_agent/            # ✈️  Flight Agent (Port 10006)
│   ├── flight_agent.py
│   ├── flight_executor.py
│   ├── flight_server/       # MCP server for flight search
│   ├── __main__.py
│   ├── .env → ../.env       # Uses root .env
│   └── README.md
│
├── hotel_agent/             # 🏨 Hotel Agent (Port 10007)
│   ├── hotel_agent.py
│   ├── hotel_executor.py
│   ├── hotel_server/        # MCP server for hotel search
│   ├── __main__.py
│   ├── .env → ../.env       # Uses root .env
│   └── README.md
│
├── host_agent/              # 🎛️  Host Agent (Port 8083)
│   ├── routing_agent.py     # Main routing logic
│   ├── remote_agent_connection.py  # A2A client
│   ├── __main__.py          # Gradio UI
│   ├── .env → ../.env       # Uses root .env
│   └── README.md
│
└── logs/                    # 📋 Agent logs (auto-created by agent_control.sh)
    ├── weather_agent.log
    ├── airbnb_agent.log
    ├── tripadvisor_agent.log
    ├── event_agent.log
    ├── finance_agent.log
    ├── flight_agent.log
    ├── hotel_agent.log
    └── host_agent.log
```

**Key Files:**
- **`.env`**: Centralized configuration for all agents (API keys, URLs, model settings)
- **`agent_control.sh`**: Single script for all operations (start, stop, status, logs)
- **`README.md`**: Comprehensive documentation (this file)
- **`logs/`**: Automatically created directory containing logs for each agent

## 🔐 Security Considerations

**Important**: This demo is for demonstration purposes. When building production applications:

- ✅ Treat all external agents as potentially untrusted
- ✅ Validate and sanitize all received data
- ✅ Implement proper authentication and authorization
- ✅ Use secure credential management (e.g., secret managers)
- ✅ Validate agent cards and responses before processing
- ✅ Implement rate limiting and quota management
- ✅ Monitor for suspicious activity

**Warning**: A malicious agent could provide crafted data that, if used without sanitization in LLM prompts, could lead to prompt injection attacks.

## 📚 Additional Resources

### Project Documentation
- **[README.md](README.md)** - Complete project documentation (this file, English)
- **[README_CN.md](README_CN.md)** - Complete project documentation (Chinese)
- **[CLAUDE.md](CLAUDE.md)** - Instructions for Claude Code
- **[.env.example](.env.example)** - Configuration template with all required variables
- **Individual Agent READMEs**:
  - [Host Agent](host_agent/README.md) | [中文](host_agent/README_CN.md)
  - [Weather Agent](weather_agent/README.md) | [中文](weather_agent/README_CN.md)
  - [Airbnb Agent](airbnb_agent/README.md) | [中文](airbnb_agent/README_CN.md)
  - [TripAdvisor Agent](tripadvisor_agent/README.md) | [中文](tripadvisor_agent/README_CN.md)
  - [Event Agent](event_agent/README.md) | [中文](event_agent/README_CN.md)
  - [Finance Agent](finance_agent/README.md) | [中文](finance_agent/README_CN.md)
  - [Flight Agent](flight_agent/README.md) | [中文](flight_agent/README_CN.md)
  - [Hotel Agent](hotel_agent/README.md) | [中文](hotel_agent/README_CN.md)

### Framework & Protocol Documentation
- **[A2A Protocol](https://github.com/google/a2a-python)** - Agent-to-Agent communication protocol
- **[Google ADK Documentation](https://google.github.io/adk-docs/)** - Agent Development Kit
- **[A2A Purchasing Concierge Tutorial](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge#1)** - Hands-on A2A tutorial
- **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)** - Tool integration protocol
- **[LangGraph Documentation](https://langchain-ai.github.io/langgraph/)** - Agent framework used in Airbnb Agent
- **[FastMCP Documentation](https://github.com/jlowin/fastmcp)** - Fast MCP server framework

### API Documentation & Keys
- **[Google Gemini API](https://makersuite.google.com/app/apikey)** - Get your Gemini API key
- **[Google Cloud Console](https://console.cloud.google.com/)** - For Vertex AI setup
- **[Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)** - Production AI platform
- **[SerpAPI](https://serpapi.com/)** - Google search and data API
  - [SerpAPI Dashboard](https://serpapi.com/dashboard) - Manage API keys and credits
  - [SerpAPI Documentation](https://serpapi.com/docs) - API reference
- **[TripAdvisor Developer Portal](https://www.tripadvisor.com/developers)** - Get TripAdvisor API key

### Related Tools
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[Gradio](https://www.gradio.app/)** - Web UI framework used for Host Agent
- **[LiteLLM](https://docs.litellm.ai/)** - Multi-LLM proxy used in agents

