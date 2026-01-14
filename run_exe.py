import os
import sys
import threading
import webbrowser
import time
import multiprocessing
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger("AIPresenter_Launcher")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load Environment Variables
from dotenv import load_dotenv
env_path = resource_path(".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Import Modules
import server
from livekit.agents import cli, WorkerOptions
# Import Agent Module
from agent import agent as agent_module

# Configure Flask to serve from the correct directory when frozen
server.app.static_folder = resource_path(".")
server.app.static_url_path = ''

def start_agent_process():
    """Runs the LiveKit Agent Locally"""
    logger.info("🤖 Starting AI Presenter Agent...")
    # Important: Set args to 'start' to avoid dev mode watchers
    sys.argv = ["agent", "start"]
    try:
        cli.run_app(WorkerOptions(entrypoint_fnc=agent_module.entrypoint))
    except Exception as e:
        logger.error(f"Agent Crash: {e}")

if __name__ == "__main__":
    multiprocessing.freeze_support()

    # 1. Start UI Server (Thread)
    # Note: We updated server.py to use 'start_server' instead of 'start_server_process'
    server_thread = threading.Thread(target=server.start_server, daemon=True)
    server_thread.start()

    # 2. Open Browser (Thread)
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:8000")
    
    threading.Thread(target=open_browser, daemon=True).start()

    # 3. Start AI Agent (Main Process)
    logger.info("🚀 Launching AI Presentation Assistant...")
    
    # We delay slightly to let the UI server spin up
    time.sleep(1)
    
    try:
        start_agent_process()
    except KeyboardInterrupt:
        sys.exit(0)