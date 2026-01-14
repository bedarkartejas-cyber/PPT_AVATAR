import subprocess
import time
import os
import sys
import webbrowser

def run_process(command, cwd=None, title="Process"):
    """Runs a process in a new independent window"""
    print(f"🚀 Starting {title}...")
    
    if sys.platform == "win32":
        return subprocess.Popen(
            f"start \"{title}\" {command}", 
            cwd=cwd, 
            shell=True, 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        return subprocess.Popen(
            command, 
            cwd=cwd, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

def main():
    print("==================================================")
    print("   AI PRESENTATION ASSISTANT - LAUNCHER")
    print("==================================================")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    agent_dir = os.path.join(root_dir, 'agent')
    
    # 2. Start Web Server
    py_exec = sys.executable 
    server_process = run_process(
        f"\"{py_exec}\" server.py", 
        cwd=root_dir, 
        title="Web Server (Uploads)"
    )
    
    # Give server a moment to init
    time.sleep(2)
    
    # 3. Start AI Agent
    agent_process = run_process(
        f"\"{py_exec}\" agent.py start", 
        cwd=agent_dir, 
        title="AI Presenter Agent"
    )

    print("✅ Services Started.")
    print("⏳ Waiting for initialization...")
    time.sleep(3)
    
    # 4. Open Browser
    print("🌐 Opening Interface...")
    webbrowser.open("http://localhost:8000")
    
    print("\n[INFO] Close the pop-up terminal windows to stop the demo.")

if __name__ == "__main__":
    main()