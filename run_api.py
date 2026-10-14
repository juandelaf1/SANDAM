import subprocess
import sys
import os
import time

os.chdir(r"C:\Users\JUAN\Desktop\Proyectos\SANDAM")
env = os.environ.copy()
env["PATH"] = r"C:\Users\JUAN\Desktop\Proyectos\SANDAM\.venv\Scripts;" + env.get("PATH", "")

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8003"],
    env=env,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
)

print(f"API started on port 8003 (PID: {proc.pid})")
print("Press Ctrl+C to stop")

try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()