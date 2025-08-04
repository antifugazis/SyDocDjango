#!/usr/bin/env python
"""
Script to fix migration issues with MemberStatusLog and ActivityGroupAssignment models.
"""

import os
import sys
import sqlite3
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append('/Users/morti/Documents/Projects/SyDocDjango/sydoc_project')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sydoc_project.settings')
django.setup()

from django.db import connection


def check_table_exists(table_name):
    """Check if a table exists in the database."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, [table_name])
        return cursor.fetchone() is not None


def create_memberstatuslog_table():
    """Create the MemberStatusLog table if it doesn't exist."""
    if check_table_exists('core_memberstatuslog'):
        print("MemberStatusLog table already exists.")
        return
    
    print("Creating MemberStatusLog table...")
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE core_memberstatuslog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_type VARCHAR(20) NOT NULL,
                reason TEXT,
                changed_at DATETIME NOT NULL,
                changed_by_id INTEGER,
                member_id INTEGER NOT NULL,
                FOREIGN KEY (changed_by_id) REFERENCES auth_user(id),
                FOREIGN KEY (member_id) REFERENCES core_member(id)
            )
        """)
    print("MemberStatusLog table created successfully.")


def mark_migration_applied(app, migration_name):
    """Mark a migration as applied in Django's migration table."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT OR IGNORE INTO django_migrations (app, name, applied)
            VALUES (?, ?, datetime('now'))
        "", [app, migration_name])
    print(f"Marked migration {app}.{migration_name} as applied.")


def main():
    """Main function to fix migration issues."""
    print("Checking migration status...")
    
    # Create MemberStatusLog table if it doesn't exist
    create_memberstatuslog_table()
    
    # Mark migrations as applied
    mark_migration_applied('core', '0041_activitygroupassignment')
    mark_migration_applied('core', '0042_memberstatuslog')
    
    print("Migration fix completed successfully.")


if __name__ == "__main__":
    main()
