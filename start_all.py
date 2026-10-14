import subprocess
import sys
import os
import time
import requests

os.chdir(r"C:\Users\JUAN\Desktop\Proyectos\SANDAM")
env = os.environ.copy()
env["PATH"] = r"C:\Users\JUAN\Desktop\Proyectos\SANDAM\.venv\Scripts;" + env.get("PATH", "")

print("=" * 50)
print("SANDAM 2026 - Starting...")
print("=" * 50)

# Start API
print("\n[1/2] Starting API...")
api_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8004"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(6)

# Test API
try:
    r = requests.get("http://127.0.0.1:8004/api/v1/beaches/", timeout=5)
    print(f"   API OK: {r.status_code}")
except:
    print("   API ERROR")

# Start Dashboard
print("\n[2/2] Starting Dashboard...")
dash_proc = subprocess.Popen(
    [sys.executable, "notebooks/dashboard_dash_pro.py"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print("\n" + "=" * 50)
print("DONE! Open: http://127.0.0.1:8050")
print("=" * 50)

api_proc.wait()