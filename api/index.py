import sys
from pathlib import Path

# Add project root to sys.path so 'backend' imports work on Vercel
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import app
