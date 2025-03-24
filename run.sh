#!/bin/bash

# Load environment variables from the .env file
set -a
source ./backend/.env
set +a

# Function to handle errors
handle_error() {
  echo "Error: $1"
  exit 1
}

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
  echo "Warning: OPENAI_API_KEY environment variable is not set."
  echo "You will need to set this in backend/.env for the LLM functionality to work."
  read -p "Do you want to continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Create .env file if it doesn't exist
if [ ! -f "./backend/.env" ]; then
  echo "Creating .env file from .env.example..."
  cp ./backend/.env.example ./backend/.env || handle_error "Failed to create .env file"
  
  # If OPENAI_API_KEY is set in environment, add it to .env
  if [ ! -z "$OPENAI_API_KEY" ]; then
    sed -i '' "s/your_openai_api_key_here/$OPENAI_API_KEY/g" ./backend/.env || handle_error "Failed to update API key in .env"
  fi
fi

# Start backend server in the background
echo "Starting backend server..."
cd backend || handle_error "Failed to change to backend directory"
python3 -m venv venv || handle_error "Failed to create virtual environment"
source venv/bin/activate || handle_error "Failed to activate virtual environment"
pip install -r requirements.txt || handle_error "Failed to install backend dependencies"
python app.py &
BACKEND_PID=$!
cd ..

# Start frontend server in the background
echo "Starting frontend server..."
cd frontend || handle_error "Failed to change to frontend directory"
npm install || handle_error "Failed to install frontend dependencies"
npm run dev &
FRONTEND_PID=$!

# Function to kill processes on exit
cleanup() {
  echo "Shutting down servers..."
  kill $BACKEND_PID 2>/dev/null
  kill $FRONTEND_PID 2>/dev/null
  exit 0
}

# Set up trap to catch SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "Servers are running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:5005"
echo "Press Ctrl+C to stop the servers"

# Wait for user to press Ctrl+C
wait
