import os
from dotenv import load_dotenv
from hotel_server import mcp

def main():
    # Load environment variables from the hotel_agent's .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    # Check if the env file exists
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment variables from: {env_path}")
    else:
        print(f"Warning: .env file not found at {env_path}")
        print("Attempting to use environment variables from parent process...")

    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
