import sqlite3
import os

# Get database path
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "database", "hospital.db")

# Connect to database
conn = sqlite3.connect(db_path)

# Get all saved records
cursor = conn.cursor()

cursor.execute("SELECT * FROM patient_predictions")

rows = cursor.fetchall()

# Print records
for row in rows:
    print(row)

# Close database
conn.close()