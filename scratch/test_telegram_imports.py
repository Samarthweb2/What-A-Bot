import sys
import os
import asyncio

# Setup fake env vars
os.environ["DATABASE_URL"] = "postgresql://dummy:dummy@localhost/dummy"
os.environ["TELEGRAM_BOT_TOKEN"] = "dummy"
os.environ["TELEGRAM_WEBHOOK_SECRET"] = "dummy"

# Import modules to verify no syntax errors
try:
    import app.webhook
    import app.sender
    import app.config
    import app.main
    print("Imports successful!")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)
