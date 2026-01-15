#!/bin/bash

# Start the Flask Server in the background
echo "🚀 Starting Server..."
python server.py &

# Start the AI Agent in the background
echo "🤖 Starting AI Agent..."
python agent/agent.py start &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
