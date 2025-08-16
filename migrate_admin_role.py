#!/usr/bin/env python3
"""
Database Migration Script for Admin Role

This script adds the admin role field to existing users in the database.
Run this script after updating the models but before starting the application.

Usage:
    python migrate_admin_role.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_database():
    """Migrate the database to add admin role field"""
    
    print("🔄 Database Migration: Adding Admin Role Field")
    print("=" * 50)
    
    try:
        # Import database components
        from backend.models.database import get_session
        from backend.models.models import User, UserRole
        from sqlmodel import text
        
        print("✅ Database models imported successfully")
        
        # Get database session
        session = next(get_session())
        
        # Check if admin role column exists
        try:
            # Try to query the role field
            result = session.exec(text("SELECT role FROM user LIMIT 1"))
            print("✅ Admin role field already exists in database")
            return True
        except Exception:
            print("📝 Admin role field not found, adding it...")
        
        # Add admin role column to existing users table
        try:
            # SQLite specific ALTER TABLE command
            session.exec(text("ALTER TABLE user ADD COLUMN role VARCHAR(10) DEFAULT 'user'"))
            session.commit()
            print("✅ Admin role field added successfully")
            
            # Update existing users to have 'user' role
            session.exec(text("UPDATE user SET role = 'user' WHERE role IS NULL"))
            session.commit()
            print("✅ Existing users updated with 'user' role")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding admin role field: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please ensure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting Database Migration...")
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Database migration completed successfully!")
        print("   You can now run the application with admin role support.")
    else:
        print("\n❌ Database migration failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
