"""
SQL Query Tool for Hospital Data Warehouse
Execute custom SQL queries and view results
"""

import sqlite3
import pandas as pd
import sys

def execute_query(query):
    """Execute a SQL query and display results"""
    try:
        conn = sqlite3.connect('hospital_datawarehouse.db')
        
        # If query is a SELECT, show results
        if query.strip().upper().startswith('SELECT'):
            df = pd.read_sql_query(query, conn)
            print("\n" + "="*80)
            print(f"QUERY RESULTS: {len(df)} rows")
            print("="*80)
            print(df.to_string())
        else:
            # For non-SELECT queries (INSERT, UPDATE, etc.)
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            print(f"\n✓ Query executed successfully. Rows affected: {cursor.rowcount}")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error executing query: {e}")

def show_schema():
    """Display database schema"""
    conn = sqlite3.connect('hospital_datawarehouse.db')
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("DATABASE SCHEMA")
    print("="*80)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    for (table_name,) in tables:
        print(f"\n📋 Table: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"{'Column':<25} {'Type':<15} {'Not Null':<10} {'PK':<5}")
        print("-" * 60)
        for col in columns:
            col_id, name, type_, not_null, default, pk = col
            print(f"{name:<25} {type_:<15} {bool(not_null)!s:<10} {bool(pk)!s:<5}")
    
    # Show views
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
    views = cursor.fetchall()
    
    if views:
        print("\n" + "="*80)
        print("VIEWS")
        print("="*80)
        for (view_name,) in views:
            print(f"📊 {view_name}")
    
    conn.close()

def show_sample_queries():
    """Display sample SQL queries"""
    print("\n" + "="*80)
    print("SAMPLE SQL QUERIES")
    print("="*80)
    
    queries = {
        "1. Total revenue by wing": """
SELECT wing, 
       SUM(total_bill_ksh) as total_revenue,
       COUNT(*) as encounters
FROM fact_encounters
GROUP BY wing
ORDER BY total_revenue DESC;
        """,
        
        "2. Monthly revenue trend": """
SELECT strftime('%Y-%m', date) as month,
       SUM(total_bill_ksh) as revenue
FROM fact_encounters
GROUP BY month
ORDER BY month;
        """,
        
        "3. Top 10 patients by spending": """
SELECT p.name, p.age, p.region,
       COUNT(f.encounter_id) as visits,
       SUM(f.total_bill_ksh) as total_spent
FROM dim_patients p
JOIN fact_encounters f ON p.patient_id = f.patient_id
GROUP BY p.patient_id
ORDER BY total_spent DESC
LIMIT 10;
        """,
        
        "4. Doctor performance by specialty": """
SELECT d.specialty,
       COUNT(DISTINCT d.doctor_id) as num_doctors,
       COUNT(f.encounter_id) as total_encounters,
       AVG(f.total_bill_ksh) as avg_bill
FROM dim_doctors d
JOIN fact_encounters f ON d.doctor_id = f.doctor_id
GROUP BY d.specialty
ORDER BY total_encounters DESC;
        """,
        
        "5. Insurance vs Cash payment analysis": """
SELECT f.payment_method,
       COUNT(*) as encounters,
       SUM(f.total_bill_ksh) as revenue,
       AVG(f.total_bill_ksh) as avg_bill,
       AVG(f.stay_duration_days) as avg_stay
FROM fact_encounters f
GROUP BY f.payment_method;
        """,
        
        "6. Maternity wing detailed analysis": """
SELECT p.insurance_provider,
       COUNT(*) as deliveries,
       SUM(f.total_bill_ksh) as total_revenue,
       AVG(f.stay_duration_days) as avg_stay_days
FROM fact_encounters f
JOIN dim_patients p ON f.patient_id = p.patient_id
WHERE f.wing = 'Maternity'
GROUP BY p.insurance_provider;
        """,
        
        "7. Regional patient demographics": """
SELECT p.region,
       p.gender,
       COUNT(*) as patient_count,
       AVG(p.age) as avg_age
FROM dim_patients p
GROUP BY p.region, p.gender
ORDER BY p.region, p.gender;
        """,
        
        "8. Emergency room patterns": """
SELECT strftime('%w', date) as day_of_week,
       COUNT(*) as er_visits,
       AVG(total_bill_ksh) as avg_cost
FROM fact_encounters
WHERE wing = 'Emergency Room'
GROUP BY day_of_week
ORDER BY er_visits DESC;
        """
    }
    
    for name, query in queries.items():
        print(f"\n{name}:")
        print(query)

def interactive_mode():
    """Interactive SQL query mode"""
    print("\n" + "="*80)
    print("INTERACTIVE SQL QUERY MODE")
    print("="*80)
    print("\nCommands:")
    print("  - Type SQL query and press Enter")
    print("  - 'schema' - Show database schema")
    print("  - 'samples' - Show sample queries")
    print("  - 'exit' or 'quit' - Exit")
    print("="*80)
    
    while True:
        try:
            query = input("\nSQL> ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit']:
                print("\nGoodbye!")
                break
            
            if query.lower() == 'schema':
                show_schema()
                continue
            
            if query.lower() == 'samples':
                show_sample_queries()
                continue
            
            execute_query(query)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break

def main():
    """Main function"""
    print("="*80)
    print("HOSPITAL DATA WAREHOUSE - SQL QUERY TOOL")
    print("="*80)
    
    # Check if database exists
    import os
    if not os.path.exists('hospital_datawarehouse.db'):
        print("\n❌ Error: Database 'hospital_datawarehouse.db' not found!")
        print("Run 'python create_data_warehouse.py' first.")
        return
    
    # Get database stats
    conn = sqlite3.connect('hospital_datawarehouse.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM fact_encounters")
    total_encounters = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(total_bill_ksh) FROM fact_encounters")
    total_revenue = cursor.fetchone()[0]
    
    print(f"\nDatabase: hospital_datawarehouse.db")
    print(f"Total Encounters: {total_encounters:,}")
    print(f"Total Revenue: KSh {total_revenue:,.0f}")
    
    conn.close()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'schema':
            show_schema()
        elif command == 'samples':
            show_sample_queries()
        else:
            # Treat as SQL query
            query = ' '.join(sys.argv[1:])
            execute_query(query)
    else:
        # Start interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
