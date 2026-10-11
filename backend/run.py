import uvicorn
import os
import sys

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("Starting AI Phishing Email Detection Backend Server...")
    print("Documentation available at: http://127.0.0.1:8000/docs")
    print("WebSocket endpoint available at: ws://127.0.0.1:8000/ws/alerts")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
