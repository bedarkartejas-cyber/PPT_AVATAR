import subprocess
import time
import sys
import os

def main():
    print("=======================================")
    print("   CROMA DEV RUNNER (Server + Client)  ")
    print("=======================================")

    # 1. Start the Agent (Simulating Cloud Server)
    print("🤖 Starting AI Agent (Server)...")
    agent_process = subprocess.Popen(
        [sys.executable, "agent/agent.py", "dev"],
        cwd=os.getcwd()
    )

    # Give agent a moment to spin up
    time.sleep(2)

    # 2. Start the Client (Simulating User EXE)
    print("💻 Starting Client App...")
    # We run run_exe.py directly as if it were the exe
    client_process = subprocess.Popen(
        [sys.executable, "run_exe.py"],
        cwd=os.getcwd()
    )

    print("\n✅ BOTH SERVICES RUNNING.")
    print("Press Ctrl+C to stop everything.\n")

    try:
        agent_process.wait()
        client_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        agent_process.terminate()
        client_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
