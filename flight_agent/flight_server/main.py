import os
from dotenv import load_dotenv
from flight_server import mcp

def main():
    # Load environment variables from the flight_agent's .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)

    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
