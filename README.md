# Hospital Data Warehouse - OLAP Operations
## St. Bonaventure Hospital Analytics
### Group Assignment - Data Analytics

---

## 📋 Project Overview

This project implements a complete **Data Warehouse** with **OLAP (Online Analytical Processing)** operations for a fictional hospital system. It demonstrates all major OLAP operations with both Python scripts and interactive web dashboards.

---

## 🗂️ Project Structure

```
├── app.py                          # Data generation script
├── create_data_warehouse.py        # SQL data warehouse creation
├── hospital_datawarehouse.db       # SQLite database (Star Schema)
├── olap_operations.py              # Command-line OLAP demonstrations
├── streamlit_olap_app.py           # Interactive dashboard (CSV-based)
├── streamlit_olap_sql.py           # Interactive dashboard (SQL-based)
├── dim_patients.csv                # Patient dimension table
├── dim_doctors.csv                 # Doctor dimension table
├── dim_services.csv                # Services dimension table
├── fact_encounters.csv             # Fact table (encounters)
└── tableau_export/                 # Tableau-compatible exports
```

---

## 🏗️ Data Warehouse Architecture

### Star Schema Design

**Dimension Tables:**
1. **dim_patients** (2,000 records)
   - patient_id (PK)
   - name, age, gender, region, residence_type, insurance_provider

2. **dim_doctors** (30 records)
   - doctor_id (PK)
   - doctor_name, specialty

3. **dim_services** (15 records)
   - service_id (PK)
   - category, service_name, unit_cost_ksh

**Fact Table:**
4. **fact_encounters** (10,000 records)
   - encounter_id (PK)
   - patient_id (FK), doctor_id (FK), primary_service_id (FK)
   - date, wing, payment_method, stay_duration_days, total_bill_ksh, is_inpatient

### Database Features
- ✅ Primary and Foreign Key constraints
- ✅ 7 indexes for query performance
- ✅ Pre-built analytical views
- ✅ Data integrity verification

---

## 📊 OLAP Operations Implemented

### 1. **Roll-Up (Aggregation)** 🔼
Climb up hierarchies from detailed to summary level.

**Examples:**
- Temporal: Daily → Monthly → Quarterly → Yearly revenue
- Geographic: Residence Type → Region → Country

### 2. **Drill-Down (Disaggregation)** 🔽
Break down aggregated data into finer details.

**Examples:**
- Wing → Payment Method → Specialty → Individual Encounters
- Summary metrics → Detailed transaction records

### 3. **Slice** ✂️
Select a single dimension value (creates a sub-cube).

**Examples:**
- Only "Maternity" wing
- Only "Q1 2023"
- Only "Female" patients

### 4. **Dice** 🎲
Select multiple dimension values simultaneously (creates smaller sub-cube).

**Examples:**
- Maternity + Insurance + Nairobi
- Emergency Room + Age 60+ + Q2 2023
- Urban + Private Insurance + Inpatient

### 5. **Pivot (Rotation)** 🔄
Rotate the data cube to view from different perspectives.

**Examples:**
- Wing (rows) × Payment Method (columns)
- Specialty (rows) × Quarter (columns)
- Region (rows) × Gender (columns)

---

## 🚀 How to Run

### Prerequisites
```bash
# Install Python packages
pip install pandas numpy streamlit plotly
```

### Option 1: Command-Line OLAP Operations
```bash
python3 olap_operations.py
```
This displays all 5 OLAP operations with detailed output in the terminal.

### Option 2: Interactive Streamlit Dashboard (CSV)
```bash
streamlit run streamlit_olap_app.py
```
Opens browser at `http://localhost:8501` with interactive OLAP operations.

### Option 3: Interactive Streamlit Dashboard (SQL)
```bash
# First, create the data warehouse (if not already done)
python3 create_data_warehouse.py

# Then run the SQL-based dashboard
streamlit run streamlit_olap_sql.py
```
Opens browser with SQL-powered OLAP operations + SQL query previews.

### Option 4: Generate Fresh Data
```bash
python3 app.py
```
Regenerates all CSV files with new random data (10,000 encounters).

---

## 💾 Data Warehouse Details

### Volume
- **Patients:** 2,000
- **Doctors:** 30
- **Services:** 15
- **Encounters:** 10,000
- **Total Revenue:** KSh 252,800,000

### Key Metrics
- **Average Bill:** KSh 25,280
- **Inpatient %:** 14.1%
- **Average Patient Age:** 46.7 years
- **Top Revenue Wing:** Maternity (72.1%)

### SQL Views
The database includes pre-built views:
1. **vw_encounter_details** - Fully joined data for analysis
2. **vw_revenue_by_wing** - Aggregated wing performance

---

## 📈 Features

### Interactive Dashboard Features:
- 📊 Real-time filtering and aggregation
- 📉 Interactive Plotly visualizations
- 🔍 Multi-dimensional data exploration
- 📋 Dynamic pivot tables
- 🎨 Heatmaps for correlation analysis
- 💾 SQL query previews (SQL version)
- 📱 Responsive layout

### OLAP Capabilities:
- ✅ Temporal aggregation (day/month/quarter/year)
- ✅ Geographic rollup (residence/region/country)
- ✅ Multi-level drill-down
- ✅ Single and multi-dimension slicing
- ✅ Complex dicing with 6+ filters
- ✅ Customizable pivot tables

---

## 🎯 Assignment Requirements Met

✅ **Task 1:** Generated fictional data for 3+ tables (4 tables total)
✅ **Task 2:** Demonstrated all major OLAP operations
✅ **Task 3:** Used Python, SQL, and Streamlit (multiple tools)

---

## 🔍 Example SQL Queries

### Roll-Up: Monthly Revenue
```sql
SELECT strftime('%Y-%m', date) as month,
       SUM(total_bill_ksh) as revenue,
       COUNT(*) as encounters
FROM fact_encounters
GROUP BY month
ORDER BY month;
```

### Drill-Down: Wing → Payment → Specialty
```sql
SELECT f.wing, f.payment_method, d.specialty,
       SUM(f.total_bill_ksh) as revenue,
       COUNT(*) as encounters
FROM fact_encounters f
JOIN dim_doctors d ON f.doctor_id = d.doctor_id
GROUP BY f.wing, f.payment_method, d.specialty;
```

### Slice: Maternity Wing Only
```sql
SELECT payment_method,
       SUM(total_bill_ksh) as revenue,
       COUNT(*) as encounters
FROM fact_encounters
WHERE wing = 'Maternity'
GROUP BY payment_method;
```

### Dice: Multiple Filters
```sql
SELECT f.*, p.age, p.gender, p.region
FROM fact_encounters f
JOIN dim_patients p ON f.patient_id = p.patient_id
WHERE f.wing = 'Maternity'
  AND f.payment_method = 'Insurance'
  AND p.region = 'Nairobi';
```

---

## 📊 Business Insights Discovered

1. **Maternity is the revenue driver** - 72% of total revenue
2. **Insurance dominates** - 64.6% of all encounters
3. **Inpatients are high-value** - Average KSh 138K vs KSh 6.9K for outpatients
4. **General Practitioners are busiest** - 2,011 encounters
5. **Regional demand is balanced** - Nakuru leads with 2,054 encounters

---

## 🎓 Learning Outcomes

This project demonstrates:
- ⭐ Star schema data warehouse design
- ⭐ SQL database creation with constraints and indexes
- ⭐ All 5 major OLAP operations
- ⭐ Data visualization with Plotly
- ⭐ Interactive web dashboards with Streamlit
- ⭐ Data integrity and foreign key relationships
- ⭐ Query optimization techniques

---

## 👥 Group Members

[Add your group member names here]

---

## 📝 Notes

- The database uses SQLite for portability (no server required)
- CSV files are included for Tableau compatibility
- Random seed (42) ensures reproducible data generation
- All monetary values are in Kenyan Shillings (KSh)

---

## 🔗 Technology Stack

- **Python 3.x** - Core programming language
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical operations
- **SQLite3** - Embedded database
- **Streamlit** - Web dashboard framework
- **Plotly** - Interactive visualizations

---

## 📧 Contact

For questions about this project, please contact the group members.

---

**Last Updated:** April 27, 2026
