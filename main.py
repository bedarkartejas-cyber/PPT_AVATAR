import subprocess
import sys
import time
import webbrowser
import os
import signal
from threading import Thread

# Config
SERVER_SCRIPT = "server.py"
AGENT_SCRIPT = "agent/agent.py"
PORT = 8000
URL = f"http://localhost:{PORT}"

def run_script(script_name):
    """Runs a python script in a subprocess"""
    # Use 'python' for Windows, 'python3' for Mac/Linux
    cmd = [sys.executable, script_name, "start"]
    return subprocess.Popen(cmd)

def main():
    print(f"🚀 Starting Neural Presenter System...")

    # 1. Start Web Server
    print(f"   [1/3] Launching Server ({SERVER_SCRIPT})...")
    server_process = run_script(SERVER_SCRIPT)
    time.sleep(2) # Give it a moment to boot

    # 2. Start AI Agent
    print(f"   [2/3] Launching AI Agent ({AGENT_SCRIPT})...")
    agent_process = run_script(AGENT_SCRIPT)
    time.sleep(2)

    # 3. Open Browser
    print(f"   [3/3] Opening Interface: {URL}")
    webbrowser.open(URL)

    print("\n✅ SYSTEM ONLINE. Press Ctrl+C to stop.")

    try:
        # Keep the main script alive to monitor child processes
        while True:
            time.sleep(1)
            # If server died, exit
            if server_process.poll() is not None:
                print("❌ Server process ended unexpectedly.")
                break
            # If agent died, exit
            if agent_process.poll() is not None:
                print("❌ Agent process ended unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

    finally:
        # cleanup
        server_process.terminate()
        agent_process.terminate()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()