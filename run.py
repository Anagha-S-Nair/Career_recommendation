"""
Application Entry Point.
Launches the Flask Career Recommendation Server connected to MySQL.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in python search path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    print(f"[*] Starting Career Recommendation Platform on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
