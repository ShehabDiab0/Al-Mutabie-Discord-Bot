import caribou
import sqlite3
import sys

# Config
db_url = sys.argv[1] if len(sys.argv) >= 2 else "tasks.db"
migrations_dir = './migrations/'

# Auto apply migrations
caribou.upgrade(db_url, migrations_dir)

# Connect to database
connection = sqlite3.connect(db_url, check_same_thread=False)
connection.execute("PRAGMA foreign_keys = ON")
