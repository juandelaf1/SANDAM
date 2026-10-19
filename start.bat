@echo off
REM SANDAM - Arranca la API en modo desarrollo
setlocal

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

if not exist ".env" (
    echo [!] No existe .env. Copia .env.example a .env antes de continuar.
    exit /b 1
)

echo Arrancando SANDAM API en http://127.0.0.1:8000
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
