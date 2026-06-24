import sqlite3
from datetime import datetime

DATABASE = 'health_records.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            email TEXT NOT NULL,
            glucose REAL NOT NULL,
            haemoglobin REAL NOT NULL,
            cholesterol REAL NOT NULL,
            remarks TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def create_patient(data):
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO patients (full_name, date_of_birth, email, glucose, haemoglobin, cholesterol, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['full_name'],
        data['date_of_birth'],
        data['email'],
        data['glucose'],
        data['haemoglobin'],
        data['cholesterol'],
        data.get('remarks', '')
    ))
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id

def get_all_patients():
    conn = get_db_connection()
    patients = conn.execute('SELECT * FROM patients ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(p) for p in patients]

def get_patient(patient_id):
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
    conn.close()
    return dict(patient) if patient else None

def update_patient(patient_id, data):
    conn = get_db_connection()
    conn.execute('''
        UPDATE patients 
        SET full_name = ?, date_of_birth = ?, email = ?, glucose = ?, 
            haemoglobin = ?, cholesterol = ?, remarks = ?, updated_at = ?
        WHERE id = ?
    ''', (
        data['full_name'],
        data['date_of_birth'],
        data['email'],
        data['glucose'],
        data['haemoglobin'],
        data['cholesterol'],
        data.get('remarks', ''),
        datetime.now().isoformat(),
        patient_id
    ))
    conn.commit()
    conn.close()

def delete_patient(patient_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
    conn.commit()
    conn.close()
