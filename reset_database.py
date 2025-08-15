#!/usr/bin/env python3
"""
Script to reset the database with the new schema including the answers column
"""

import os
import sqlite3
from pathlib import Path

def reset_database():
    """Reset the database by deleting the existing file and recreating tables"""
    
    db_path = Path("investment_advisor.db")
    
    if db_path.exists():
        print(f"🗑️ Deleting existing database: {db_path}")
        try:
            db_path.unlink()
            print("✅ Database deleted successfully")
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            return False
    else:
        print("ℹ️ No existing database found")
    
    print("🔄 Database will be recreated when the backend starts")
    print("💡 Please restart the backend server to create the new database schema")
    return True

if __name__ == "__main__":
    print("🚀 Database Reset Script")
    print("=" * 40)
    
    try:
        success = reset_database()
        if success:
            print("\n✅ Database reset completed!")
            print("📝 Next steps:")
            print("1. Stop the backend server (Ctrl+C)")
            print("2. Start the backend server again: python run_backend.py")
            print("3. The new database will be created with the correct schema")
        else:
            print("\n❌ Database reset failed!")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
