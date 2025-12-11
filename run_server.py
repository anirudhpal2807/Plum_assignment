#!/usr/bin/env python3
"""
Simple startup script for the Medical Report API
Ensures correct working directory and starts the server
"""

import os
import sys
import subprocess

# Change to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("=" * 60)
print("  🏥 Medical Report Simplifier - API Server")
print("=" * 60)
print(f"\n📂 Working directory: {os.getcwd()}")
print(f"🐍 Python: {sys.executable}")
print(f"📦 Python version: {sys.version.split()[0]}")
print("\n" + "=" * 60)
print("  Starting FastAPI Server...")
print("=" * 60)
print("\n🌐 API will be available at: http://localhost:8000")
print("📖 Swagger docs at:           http://localhost:8000/docs")
print("⚙️  ReDoc at:                  http://localhost:8000/redoc")
print("\n💡 Tip: Open frontend.html in a browser to test the UI")
print("\n⏹️  Press Ctrl+C to stop the server\n")

# Start the server
try:
    subprocess.run([
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--reload',
        '--port', '8000'
    ])
except KeyboardInterrupt:
    print("\n\n❌ Server stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
