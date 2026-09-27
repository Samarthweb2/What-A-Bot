import sys

print("Checking imports...")
try:
    import app.config
    import app.db
    import app.dispatcher
    import app.main
    import app.recovery
    import app.sender
    import app.transactions
    import app.webhook
    print("All imports successful.")
    sys.exit(0)
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)
