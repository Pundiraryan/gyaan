import os
import sys
import uvicorn

if __name__ == "__main__" and __package__ is None:
    root_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    if root_dir not in sys.path:
        sys.path.append(root_dir)

from backend.app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=False)
