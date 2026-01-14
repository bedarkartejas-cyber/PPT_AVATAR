import subprocess
import sys
import time
import webbrowser
import os

def run_process(command, cwd=None):
    """Runs a process and prints its output to the console"""
    print(f"🚀 Starting: {command}...")
    
    # Use the current python interpreter
    if sys.platform == "win32":
        # On Windows, start in a new independent window
        return subprocess.Popen(
            f'start "{command}" {sys.executable} {command}',
            cwd=cwd,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # On Mac/Linux, run in background
        return subprocess.Popen(
            [sys.executable] + command.split(),
            cwd=cwd
        )

def main():
    print("==================================================")
    print("      AI PRESENTATION ASSISTANT - WEB LAUNCH      ")
    print("==================================================")

    # 1. Start the Flask Web Server
    server_process = run_process("server.py")
    
    # 2. Start the AI Agent
    # We point to the agent folder
    agent_cwd = os.path.join(os.getcwd(), "agent")
    agent_process = run_process("agent.py start", cwd=agent_cwd)

    print("\n✅ Services are starting...")
    print("⏳ Waiting 3 seconds for initialization...")
    time.sleep(3)

    # 3. Open the Frontend in Browser
    print("🌐 Opening http://localhost:8000")
    webbrowser.open("http://localhost:8000")

    print("\n[INFO] App is running! Close the terminal windows to stop.")

if __name__ == "__main__":
    main()