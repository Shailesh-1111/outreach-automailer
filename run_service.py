import subprocess
import sys
import os
import time

def main():
    print("🚀 Starting Outreach Applier Services...")
    
    # Paths
    root_dir = os.path.dirname(os.path.abspath(__file__))
    service_dir = os.path.join(root_dir, "outreach-service")
    ui_dir = os.path.join(root_dir, "outreach-ui")
    
    # Start Backend (FastAPI on port 8000)
    print("⏳ Starting FastAPI backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=service_dir
    )
    
    # Start Frontend (Vite Dev Server)
    print("⏳ Starting Vue3/Vite frontend server...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=ui_dir,
        shell=True,
        stdout=subprocess.DEVNULL, # Hide Vite logs for a cleaner terminal
        stderr=subprocess.DEVNULL
    )
    
    # Give processes time to initialize or crash (FastAPI can take 5+ seconds if packages are missing)
    time.sleep(7)
    
    # Check if either process crashed during startup
    if backend_process.poll() is not None:
        print("\n❌ Error: FastAPI backend failed to start! Terminating...")
        if frontend_process.poll() is None:
            frontend_process.terminate()
        sys.exit(1)
        
    if frontend_process.poll() is not None:
        print("\n❌ Error: Vue frontend failed to start! Terminating...")
        if backend_process.poll() is None:
            backend_process.terminate()
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎉 All Services are running successfully!")
    print("🌐 FRONTEND LINK: http://localhost:5173")
    print("⚙️  BACKEND API:  http://127.0.0.1:8000")
    print("="*60 + "\n")
    print("Press Ctrl+C to stop all services.")
    
    try:
        # Keep script running and poll for mid-session crashes
        while True:
            if backend_process.poll() is not None:
                print("\n❌ Error: FastAPI backend stopped unexpectedly! Terminating frontend...")
                frontend_process.terminate()
                sys.exit(1)
            if frontend_process.poll() is not None:
                print("\n❌ Error: Vue frontend stopped unexpectedly! Terminating backend...")
                backend_process.terminate()
                sys.exit(1)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    main()
