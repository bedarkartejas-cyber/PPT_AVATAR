import subprocess
import sys
import time
import webbrowser
import os

def run_process(command, cwd=None, title="Process"):
    print(f"🚀 Starting {title}...")
    
    # Windows: Open in new window so you can see logs
    if sys.platform == "win32":
        return subprocess.Popen(
            f'start "{title}" {command}', 
            cwd=cwd, 
            shell=True, 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    # Mac/Linux: Run in background
    else:
        return subprocess.Popen(
            command, 
            cwd=cwd, 
            shell=True
        )

def main():
    print("==================================================")
    print("       AI PRESENTATION ASSISTANT - LAUNCHER       ")
    print("==================================================")

    # 1. Start the Flask Web Server (server.py)
    # Uses the current python executable
    server_cmd = f'"{sys.executable}" server.py'
    run_process(server_cmd, title="Web Server")
    
    # 2. Start the AI Agent (agent/agent.py)
    agent_cwd = os.path.join(os.getcwd(), "agent")
    agent_cmd = f'"{sys.executable}" agent.py start'
    run_process(agent_cmd, cwd=agent_cwd, title="AI Agent")

    print("\n✅ Systems Launching...")
    print("⏳ Waiting 4 seconds for initialization...")
    time.sleep(4)

    # 3. Open the Browser
    print("🌐 Opening App...")
    webbrowser.open("http://localhost:8000")

    print("\n[INFO] App is running! Close the popup windows to stop.")

if __name__ == "__main__":
    main()