import subprocess
import sys
import os
import time

os.chdir(r"C:\Users\JUAN\Desktop\Proyectos\SANDAM")
env = os.environ.copy()
env["PATH"] = r"C:\Users\JUAN\Desktop\Proyectos\SANDAM\.venv\Scripts;" + env.get("PATH", "")

print("=" * 50)
print("SANDAM 2026 - Starting Services")
print("=" * 50)

# Start API
api_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8004"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
print(f"API started on http://127.0.0.1:8004")

time.sleep(5)

# Start Dash
dash_proc = subprocess.Popen(
    [sys.executable, "notebooks/dashboard_dash_pro.py"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
print(f"Dashboard started on http://127.0.0.1:8050")

print("=" * 50)
print("Open in browser: http://127.0.0.1:8050")
print("=" * 50)

api_proc.wait()