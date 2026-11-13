import sqlite3
import os
from flask import g, current_app

def get_db():
    """Get or create SQLite database connection for the current application context."""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE_PATH', 'uzhavar.db')
        if not os.path.isabs(db_path):
            db_path = os.path.join(current_app.root_path, db_path)
            
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        # Enable foreign keys
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """Convenience helper to query the database and return dictionary-like Row objects."""
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=(), commit=True):
    """Convenience helper to execute an INSERT, UPDATE, or DELETE query and return lastrowid."""
    db = get_db()
    cur = db.execute(query, args)
    if commit:
        db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id
