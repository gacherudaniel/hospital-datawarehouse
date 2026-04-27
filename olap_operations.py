"""
OLAP Operations on Hospital Data Warehouse
Group Assignment - Data Analytics

This script demonstrates the following OLAP operations:
1. Roll-up (Aggregation)
2. Drill-down (Disaggregation)
3. Slice
4. Dice
5. Pivot

Data Warehouse: St. Bonaventure Hospital
Schema: Star Schema with 3 dimensions + 1 fact table
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Load data
print("="*80)
print("LOADING DATA WAREHOUSE")
print("="*80)

dim_patients = pd.read_csv('dim_patients.csv')
dim_doctors = pd.read_csv('dim_doctors.csv')
dim_services = pd.read_csv('dim_services.csv')
fact_encounters = pd.read_csv('fact_encounters.csv')

# Convert date column to datetime
fact_encounters['date'] = pd.to_datetime(fact_encounters['date'])
fact_encounters['year'] = fact_encounters['date'].dt.year
fact_encounters['month'] = fact_encounters['date'].dt.month
fact_encounters['quarter'] = fact_encounters['date'].dt.quarter

# Join fact table with dimensions
data = fact_encounters.merge(dim_patients, on='patient_id', how='left')
data = data.merge(dim_doctors, on='doctor_id', how='left')
data = data.merge(dim_services, left_on='primary_service_id', right_on='service_id', how='left')

print(f"✓ Loaded {len(dim_patients)} patients")
print(f"✓ Loaded {len(dim_doctors)} doctors")
print(f"✓ Loaded {len(dim_services)} services")
print(f"✓ Loaded {len(fact_encounters)} encounters")
print(f"✓ Created consolidated dataset with {len(data)} records")
print()

# =============================================================================
# OLAP OPERATION 1: ROLL-UP (AGGREGATION)
# =============================================================================
print("="*80)
print("OLAP OPERATION 1: ROLL-UP (AGGREGATION)")
print("="*80)
print("Definition: Aggregate data by climbing up the hierarchy")
print("Example: From daily → monthly → quarterly → yearly revenue")
print()

# Level 1: Daily revenue (most detailed)
daily_revenue = data.groupby(data['date'].dt.date).agg({
    'total_bill_ksh': 'sum',
    'encounter_id': 'count'
}).rename(columns={'encounter_id': 'num_encounters'})
print("LEVEL 1 - Daily Revenue (first 10 days):")
print(daily_revenue.head(10))
print()

# Level 2: Monthly revenue (rolled up)
monthly_revenue = data.groupby(['year', 'month']).agg({
    'total_bill_ksh': 'sum',
    'encounter_id': 'count'
}).rename(columns={'encounter_id': 'num_encounters'})
print("LEVEL 2 - Monthly Revenue (rolled up from daily):")
print(monthly_revenue)
print()

# Level 3: Quarterly revenue (more aggregated)
quarterly_revenue = data.groupby(['year', 'quarter']).agg({
    'total_bill_ksh': 'sum',
    'encounter_id': 'count'
}).rename(columns={'encounter_id': 'num_encounters'})
print("LEVEL 3 - Quarterly Revenue (rolled up from monthly):")
print(quarterly_revenue)
print()

# Level 4: Yearly revenue (highest level)
yearly_revenue = data.groupby('year').agg({
    'total_bill_ksh': 'sum',
    'encounter_id': 'count'
}).rename(columns={'encounter_id': 'num_encounters'})
print("LEVEL 4 - Yearly Revenue (rolled up from quarterly):")
print(yearly_revenue)
print()

# Geographic Roll-up
print("GEOGRAPHIC ROLL-UP:")
print("From patient residence_type → region → country level")
location_revenue = data.groupby(['region', 'residence_type']).agg({
    'total_bill_ksh': 'sum',
    'encounter_id': 'count'
}).rename(columns={'encounter_id': 'num_encounters'})
print("\nLevel 1 - By Region & Residence Type:")
print(location_revenue)

region_revenue = data.groupby('region').agg({
    'total_bill_ksh': 'sum',
    'encounter_id': 'count'
}).rename(columns={'encounter_id': 'num_encounters'})
print("\nLevel 2 - By Region Only (rolled up):")
print(region_revenue)
print()

# =============================================================================
# OLAP OPERATION 2: DRILL-DOWN (DISAGGREGATION)
# =============================================================================
print("="*80)
print("OLAP OPERATION 2: DRILL-DOWN (DISAGGREGATION)")
print("="*80)
print("Definition: Break down aggregated data into finer details")
print("Example: From yearly → quarterly → monthly → daily revenue")
print()

# Start with aggregate: Total revenue by wing
print("STARTING POINT - Total Revenue by Wing:")
wing_summary = data.groupby('wing').agg({
    'total_bill_ksh': ['sum', 'mean', 'count']
})
wing_summary.columns = ['Total Revenue (KSh)', 'Avg Bill (KSh)', 'Num Encounters']
print(wing_summary)
print()

# Drill-down Level 1: Wing → Payment Method
print("DRILL-DOWN LEVEL 1 - Wing → Payment Method:")
wing_payment = data.groupby(['wing', 'payment_method']).agg({
    'total_bill_ksh': ['sum', 'count']
})
wing_payment.columns = ['Total Revenue (KSh)', 'Num Encounters']
print(wing_payment)
print()

# Drill-down Level 2: Wing → Payment Method → Doctor Specialty
print("DRILL-DOWN LEVEL 2 - Wing → Payment Method → Specialty:")
wing_payment_specialty = data.groupby(['wing', 'payment_method', 'specialty']).agg({
    'total_bill_ksh': 'sum',
    'encounter_id': 'count'
}).rename(columns={'encounter_id': 'num_encounters'})
print(wing_payment_specialty.head(20))
print()

# Drill-down Level 3: Individual encounter details
print("DRILL-DOWN LEVEL 3 - Individual Encounter Details (Maternity, Insurance):")
maternity_insurance = data[
    (data['wing'] == 'Maternity') & 
    (data['payment_method'] == 'Insurance')
][['encounter_id', 'patient_id', 'doctor_name', 'date', 'total_bill_ksh', 'stay_duration_days']].head(10)
print(maternity_insurance)
print()

# =============================================================================
# OLAP OPERATION 3: SLICE
# =============================================================================
print("="*80)
print("OLAP OPERATION 3: SLICE")
print("="*80)
print("Definition: Select a single dimension value (creates a sub-cube)")
print("Example: Filter data for only 'Maternity' wing")
print()

# Slice 1: Only Maternity wing
print("SLICE 1 - Maternity Wing Only:")
maternity_slice = data[data['wing'] == 'Maternity']
maternity_summary = maternity_slice.groupby('payment_method').agg({
    'total_bill_ksh': ['sum', 'mean', 'count'],
    'stay_duration_days': 'mean'
})
maternity_summary.columns = ['Total Revenue', 'Avg Bill', 'Count', 'Avg Stay Days']
print(maternity_summary)
print(f"\nTotal Maternity Revenue: KSh {maternity_slice['total_bill_ksh'].sum():,.0f}")
print(f"Total Maternity Encounters: {len(maternity_slice)}")
print()

# Slice 2: Only Q1 2023
print("SLICE 2 - Q1 2023 (January-March) Only:")
q1_slice = data[(data['quarter'] == 1) & (data['year'] == 2023)]
q1_summary = q1_slice.groupby('wing').agg({
    'total_bill_ksh': 'sum',
    'encounter_id': 'count'
}).rename(columns={'encounter_id': 'num_encounters'})
print(q1_summary)
print(f"\nQ1 2023 Total Revenue: KSh {q1_slice['total_bill_ksh'].sum():,.0f}")
print()

# Slice 3: Only Female patients
print("SLICE 3 - Female Patients Only:")
female_slice = data[data['gender'] == 'Female']
female_summary = female_slice.groupby('wing').agg({
    'total_bill_ksh': 'sum',
    'encounter_id': 'count'
}).rename(columns={'encounter_id': 'num_encounters'})
print(female_summary)
print(f"\nFemale Patients Total Revenue: KSh {female_slice['total_bill_ksh'].sum():,.0f}")
print()

# =============================================================================
# OLAP OPERATION 4: DICE
# =============================================================================
print("="*80)
print("OLAP OPERATION 4: DICE")
print("="*80)
print("Definition: Select multiple dimension values (creates a smaller sub-cube)")
print("Example: Filter by multiple conditions simultaneously")
print()

# Dice 1: Maternity + Insurance + Nairobi region
print("DICE 1 - Maternity Wing + Insurance Payment + Nairobi Region:")
dice1 = data[
    (data['wing'] == 'Maternity') & 
    (data['payment_method'] == 'Insurance') & 
    (data['region'] == 'Nairobi')
]
print(f"Number of encounters: {len(dice1)}")
print(f"Total revenue: KSh {dice1['total_bill_ksh'].sum():,.0f}")
print(f"Average bill: KSh {dice1['total_bill_ksh'].mean():,.0f}")
print(f"Average stay: {dice1['stay_duration_days'].mean():.1f} days")
print()

# Dice 2: Emergency Room + Age 60+ + Q2 2023
print("DICE 2 - Emergency Room + Patients Age 60+ + Q2 2023:")
dice2 = data[
    (data['wing'] == 'Emergency Room') & 
    (data['age'] >= 60) & 
    (data['quarter'] == 2) & 
    (data['year'] == 2023)
]
print(f"Number of encounters: {len(dice2)}")
print(f"Total revenue: KSh {dice2['total_bill_ksh'].sum():,.0f}")
print(f"Average bill: KSh {dice2['total_bill_ksh'].mean():,.0f}")
print("\nTop 5 specialties treating elderly in ER (Q2):")
print(dice2.groupby('specialty')['encounter_id'].count().sort_values(ascending=False).head())
print()

# Dice 3: Urban residents + Private insurance + Inpatient
print("DICE 3 - Urban Residents + Private Insurance (A or B) + Inpatient:")
dice3 = data[
    (data['residence_type'] == 'Urban') & 
    (data['insurance_provider'].isin(['Private_A', 'Private_B'])) & 
    (data['is_inpatient'] == 1)
]
print(f"Number of encounters: {len(dice3)}")
print(f"Total revenue: KSh {dice3['total_bill_ksh'].sum():,.0f}")
print(f"Average bill: KSh {dice3['total_bill_ksh'].mean():,.0f}")
print(f"Average stay: {dice3['stay_duration_days'].mean():.1f} days")
print("\nRevenue by Wing:")
print(dice3.groupby('wing')['total_bill_ksh'].sum().sort_values(ascending=False))
print()

# =============================================================================
# OLAP OPERATION 5: PIVOT (ROTATION)
# =============================================================================
print("="*80)
print("OLAP OPERATION 5: PIVOT (ROTATION)")
print("="*80)
print("Definition: Rotate the data cube to view from different perspectives")
print("Example: Transform rows into columns to change the view")
print()

# Pivot 1: Wing (rows) × Payment Method (columns) → Revenue
print("PIVOT 1 - Revenue by Wing (rows) × Payment Method (columns):")
pivot1 = data.pivot_table(
    values='total_bill_ksh',
    index='wing',
    columns='payment_method',
    aggfunc='sum',
    fill_value=0
)
print(pivot1)
print()

# Pivot 2: Doctor Specialty (rows) × Quarter (columns) → Number of Encounters
print("PIVOT 2 - Number of Encounters by Specialty (rows) × Quarter (columns):")
pivot2 = data.pivot_table(
    values='encounter_id',
    index='specialty',
    columns='quarter',
    aggfunc='count',
    fill_value=0
)
print(pivot2)
print()

# Pivot 3: Region (rows) × Gender (columns) → Average Bill
print("PIVOT 3 - Average Bill by Region (rows) × Gender (columns):")
pivot3 = data.pivot_table(
    values='total_bill_ksh',
    index='region',
    columns='gender',
    aggfunc='mean',
    fill_value=0
)
print(pivot3.round(0))
print()

# Pivot 4: Multi-level pivot - Month (rows) × Wing + Inpatient Status (columns)
print("PIVOT 4 - Revenue by Month (rows) × Wing-Inpatient Combination (columns):")
data['inpatient_label'] = data['is_inpatient'].map({0: 'Outpatient', 1: 'Inpatient'})
pivot4 = data.pivot_table(
    values='total_bill_ksh',
    index='month',
    columns=['wing', 'inpatient_label'],
    aggfunc='sum',
    fill_value=0
)
print(pivot4)
print()

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================
print("="*80)
print("DATA WAREHOUSE SUMMARY STATISTICS")
print("="*80)

print("\n1. Overall Financial Performance:")
print(f"   Total Revenue: KSh {data['total_bill_ksh'].sum():,.0f}")
print(f"   Average Bill: KSh {data['total_bill_ksh'].mean():,.0f}")
print(f"   Total Encounters: {len(data):,}")

print("\n2. Top Revenue-Generating Wing:")
wing_revenue = data.groupby('wing')['total_bill_ksh'].sum().sort_values(ascending=False)
print(f"   {wing_revenue.index[0]}: KSh {wing_revenue.iloc[0]:,.0f} ({wing_revenue.iloc[0]/wing_revenue.sum()*100:.1f}%)")

print("\n3. Most Common Payment Method:")
payment_counts = data['payment_method'].value_counts()
print(f"   {payment_counts.index[0]}: {payment_counts.iloc[0]:,} encounters ({payment_counts.iloc[0]/len(data)*100:.1f}%)")

print("\n4. Busiest Doctor Specialty:")
specialty_counts = data['specialty'].value_counts()
print(f"   {specialty_counts.index[0]}: {specialty_counts.iloc[0]:,} encounters")

print("\n5. Patient Demographics:")
print(f"   Average Age: {data['age'].mean():.1f} years")
print(f"   Gender Distribution: {data['gender'].value_counts().to_dict()}")

print("\n6. Inpatient vs Outpatient:")
inpatient_revenue = data.groupby('is_inpatient')['total_bill_ksh'].agg(['sum', 'count', 'mean'])
print(f"   Outpatient: {int(inpatient_revenue.loc[0, 'count']):,} encounters, KSh {inpatient_revenue.loc[0, 'sum']:,.0f}")
print(f"   Inpatient: {int(inpatient_revenue.loc[1, 'count']):,} encounters, KSh {inpatient_revenue.loc[1, 'sum']:,.0f}")

print("\n" + "="*80)
print("OLAP OPERATIONS DEMONSTRATION COMPLETED")
print("="*80)
