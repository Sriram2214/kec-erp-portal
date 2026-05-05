@echo off
start cmd /k "title KEC-BACKEND && .venv\Scripts\python wsgi.py"
start cmd /k "title KEC-FRONTEND && cd frontend && npm run dev"
echo Servers are starting in separate windows...
