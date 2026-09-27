import sys
import os

# Add e:\emberground to path
sys.path.insert(0, r"e:\emberground")

from app.db import init_pool, get_conn

def main():
    init_pool()
    with get_conn() as conn:
        conn.execute("ALTER TABLE inbox DROP CONSTRAINT inbox_source_check;")
        conn.execute("ALTER TABLE inbox ADD CONSTRAINT inbox_source_check CHECK (source IN ('whatsapp', 'owner', 'telegram'));")
        conn.commit()
        print("Successfully updated inbox_source_check constraint to include telegram")

if __name__ == "__main__":
    main()
