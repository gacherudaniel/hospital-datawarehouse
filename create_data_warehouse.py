"""
Data Warehouse Creation Script
Creates a SQLite database with Star Schema for Hospital Data

Schema:
- Dimension Tables: dim_patients, dim_doctors, dim_services
- Fact Table: fact_encounters
- Includes primary keys, foreign keys, and indexes for performance
"""

import sqlite3
import pandas as pd
from datetime import datetime

def create_data_warehouse():
    """Create SQLite data warehouse with star schema"""
    
    # Connect to SQLite database (creates if doesn't exist)
    conn = sqlite3.connect('hospital_datawarehouse.db')
    cursor = conn.cursor()
    
    print("="*80)
    print("CREATING DATA WAREHOUSE")
    print("="*80)
    
    # Drop existing tables if they exist
    print("\n1. Dropping existing tables (if any)...")
    cursor.execute("DROP TABLE IF EXISTS fact_encounters")
    cursor.execute("DROP TABLE IF EXISTS dim_patients")
    cursor.execute("DROP TABLE IF EXISTS dim_doctors")
    cursor.execute("DROP TABLE IF EXISTS dim_services")
    
    # =========================================================================
    # CREATE DIMENSION TABLES
    # =========================================================================
    
    print("\n2. Creating dimension tables...")
    
    # Dimension: Patients
    cursor.execute("""
        CREATE TABLE dim_patients (
            patient_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            region TEXT,
            residence_type TEXT,
            insurance_provider TEXT
        )
    """)
    print("   ✓ Created dim_patients table")
    
    # Dimension: Doctors
    cursor.execute("""
        CREATE TABLE dim_doctors (
            doctor_id INTEGER PRIMARY KEY,
            doctor_name TEXT NOT NULL,
            specialty TEXT
        )
    """)
    print("   ✓ Created dim_doctors table")
    
    # Dimension: Services
    cursor.execute("""
        CREATE TABLE dim_services (
            service_id TEXT PRIMARY KEY,
            category TEXT,
            service_name TEXT NOT NULL,
            unit_cost_ksh INTEGER
        )
    """)
    print("   ✓ Created dim_services table")
    
    # =========================================================================
    # CREATE FACT TABLE
    # =========================================================================
    
    print("\n3. Creating fact table...")
    
    cursor.execute("""
        CREATE TABLE fact_encounters (
            encounter_id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            date DATETIME NOT NULL,
            wing TEXT,
            payment_method TEXT,
            stay_duration_days INTEGER DEFAULT 0,
            total_bill_ksh INTEGER NOT NULL,
            is_inpatient INTEGER DEFAULT 0,
            primary_service_id TEXT,
            FOREIGN KEY (patient_id) REFERENCES dim_patients(patient_id),
            FOREIGN KEY (doctor_id) REFERENCES dim_doctors(doctor_id),
            FOREIGN KEY (primary_service_id) REFERENCES dim_services(service_id)
        )
    """)
    print("   ✓ Created fact_encounters table with foreign keys")
    
    # =========================================================================
    # CREATE INDEXES FOR PERFORMANCE
    # =========================================================================
    
    print("\n4. Creating indexes for query performance...")
    
    cursor.execute("CREATE INDEX idx_encounters_date ON fact_encounters(date)")
    cursor.execute("CREATE INDEX idx_encounters_wing ON fact_encounters(wing)")
    cursor.execute("CREATE INDEX idx_encounters_patient ON fact_encounters(patient_id)")
    cursor.execute("CREATE INDEX idx_encounters_doctor ON fact_encounters(doctor_id)")
    cursor.execute("CREATE INDEX idx_patients_region ON dim_patients(region)")
    cursor.execute("CREATE INDEX idx_patients_gender ON dim_patients(gender)")
    cursor.execute("CREATE INDEX idx_doctors_specialty ON dim_doctors(specialty)")
    
    print("   ✓ Created 7 indexes")
    
    # =========================================================================
    # LOAD DATA FROM CSV FILES
    # =========================================================================
    
    print("\n5. Loading data from CSV files...")
    
    # Load dimension tables
    dim_patients = pd.read_csv('dim_patients.csv')
    dim_patients.to_sql('dim_patients', conn, if_exists='append', index=False)
    print(f"   ✓ Loaded {len(dim_patients)} patients")
    
    dim_doctors = pd.read_csv('dim_doctors.csv')
    dim_doctors.to_sql('dim_doctors', conn, if_exists='append', index=False)
    print(f"   ✓ Loaded {len(dim_doctors)} doctors")
    
    dim_services = pd.read_csv('dim_services.csv')
    dim_services.to_sql('dim_services', conn, if_exists='append', index=False)
    print(f"   ✓ Loaded {len(dim_services)} services")
    
    # Load fact table
    fact_encounters = pd.read_csv('fact_encounters.csv')
    fact_encounters.to_sql('fact_encounters', conn, if_exists='append', index=False)
    print(f"   ✓ Loaded {len(fact_encounters)} encounters")
    
    # =========================================================================
    # VERIFY DATA INTEGRITY
    # =========================================================================
    
    print("\n6. Verifying data integrity...")
    
    # Check for orphaned records
    cursor.execute("""
        SELECT COUNT(*) FROM fact_encounters f
        LEFT JOIN dim_patients p ON f.patient_id = p.patient_id
        WHERE p.patient_id IS NULL
    """)
    orphaned_patients = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM fact_encounters f
        LEFT JOIN dim_doctors d ON f.doctor_id = d.doctor_id
        WHERE d.doctor_id IS NULL
    """)
    orphaned_doctors = cursor.fetchone()[0]
    
    if orphaned_patients == 0 and orphaned_doctors == 0:
        print("   ✓ All foreign key relationships intact")
    else:
        print(f"   ⚠ Warning: {orphaned_patients} orphaned patient records, {orphaned_doctors} orphaned doctor records")
    
    # Get statistics
    cursor.execute("SELECT COUNT(*), SUM(total_bill_ksh), AVG(total_bill_ksh) FROM fact_encounters")
    total_encounters, total_revenue, avg_bill = cursor.fetchone()
    
    print("\n" + "="*80)
    print("DATA WAREHOUSE CREATED SUCCESSFULLY")
    print("="*80)
    print(f"\nDatabase: hospital_datawarehouse.db")
    print(f"Schema: Star Schema (3 dimensions + 1 fact table)")
    print(f"\nStatistics:")
    print(f"  Total Encounters: {total_encounters:,}")
    print(f"  Total Revenue: KSh {total_revenue:,.0f}")
    print(f"  Average Bill: KSh {avg_bill:,.0f}")
    
    # Create views for common queries
    print("\n7. Creating analytical views...")
    
    cursor.execute("""
        CREATE VIEW vw_encounter_details AS
        SELECT 
            f.encounter_id,
            f.date,
            f.wing,
            f.payment_method,
            f.total_bill_ksh,
            f.stay_duration_days,
            f.is_inpatient,
            p.name as patient_name,
            p.age,
            p.gender,
            p.region,
            p.residence_type,
            p.insurance_provider,
            d.doctor_name,
            d.specialty,
            s.service_name,
            s.category as service_category,
            s.unit_cost_ksh
        FROM fact_encounters f
        JOIN dim_patients p ON f.patient_id = p.patient_id
        JOIN dim_doctors d ON f.doctor_id = d.doctor_id
        LEFT JOIN dim_services s ON f.primary_service_id = s.service_id
    """)
    print("   ✓ Created vw_encounter_details view")
    
    cursor.execute("""
        CREATE VIEW vw_revenue_by_wing AS
        SELECT 
            wing,
            COUNT(*) as encounter_count,
            SUM(total_bill_ksh) as total_revenue,
            AVG(total_bill_ksh) as avg_bill,
            SUM(CASE WHEN is_inpatient = 1 THEN 1 ELSE 0 END) as inpatient_count
        FROM fact_encounters
        GROUP BY wing
    """)
    print("   ✓ Created vw_revenue_by_wing view")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("\n" + "="*80)
    print("Ready for OLAP operations!")
    print("="*80)
    
    return True

if __name__ == "__main__":
    try:
        create_data_warehouse()
    except Exception as e:
        print(f"\n❌ Error creating data warehouse: {e}")
        import traceback
        traceback.print_exc()
