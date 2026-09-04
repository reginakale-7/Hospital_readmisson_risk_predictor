import sqlite3
import os

# Get current project folder
base_dir = os.path.dirname(os.path.abspath(__file__))

# Database folder path
database_dir = os.path.join(base_dir, "database")

# Create database folder if it does not exist
os.makedirs(database_dir, exist_ok=True)

# Database file path
db_path = os.path.join(database_dir, "hospital.db")

# Connect to database
conn = sqlite3.connect(db_path)

# Create cursor
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS patient_predictions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    admission_type_id INTEGER,
    time_in_hospital INTEGER,
    num_lab_procedures INTEGER,
    num_procedures INTEGER,
    num_medications INTEGER,
    number_outpatient INTEGER,
    number_emergency INTEGER,
    number_inpatient INTEGER,
    number_diagnoses INTEGER,

    race TEXT,
    gender TEXT,
    age TEXT,

    max_glu_serum TEXT,
    A1Cresult TEXT,
    insulin TEXT,
    change_medication TEXT,
    diabetesMed TEXT,

    prediction TEXT,
    probability REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Save database
conn.commit()

# Close database
conn.close()

print("Database created successfully!")