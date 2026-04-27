import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_st_bonaventure_data():
    np.random.seed(42)
    num_patients = 2000    # Massive patient pool
    num_encounters = 10000  # Professional volume for Tableau
    
    # 1. Dimension: Patients
    patients = pd.DataFrame({
        'patient_id': range(1001, 1001 + num_patients),
        'name': [f'Patient_{i:04d}' for i in range(num_patients)],
        'age': np.random.randint(0, 96, num_patients),
        'gender': np.random.choice(['Male', 'Female', 'Non-Binary'], num_patients, p=[0.4, 0.55, 0.05]),
        'region': np.random.choice(['Nairobi', 'Kiambu', 'Machakos', 'Kajiado', 'Nakuru'], num_patients),
        'residence_type': np.random.choice(['Urban', 'Rural'], num_patients),
        'insurance_provider': np.random.choice(['NHIF', 'Private_A', 'Private_B', 'Self_Pay'], num_patients)
    })

    # 2. Dimension: Doctors (St. Bonaventure staff)
    specialties = ['General Practitioner', 'Cardiologist', 'Neurologist', 'Orthopedic Surgeon', 'Oncologist', 'Obstetrician', 'Pediatrician']
    doctors = pd.DataFrame({
        'doctor_id': range(2001, 2031), # 30 doctors
        'doctor_name': [f'Dr. Specialist_{i}' for i in range(30)],
        'specialty': np.random.choice(specialties, 30)
    })

    # 3. Dimension: Services (Catalog)
    services_data = [
        ('S001', 'Consultation', 'Base Consultation Fee', 2500),
        ('S002', 'Diagnostics', 'Laboratory Tests', 1500),
        ('S003', 'Diagnostics', 'X-Ray Scan', 3500),
        ('S004', 'Diagnostics', 'MRI Scan', 25000),
        ('S005', 'Diagnostics', 'CT Scan', 15000),
        ('S006', 'Treatment', 'General Medication', 1200),
        ('S007', 'Maternity', 'Normal Delivery Package', 55000),
        ('S008', 'Maternity', 'C-Section Delivery Package', 165000),
        ('S009', 'Maternity', 'Nursery / Baby Area Care', 5000), 
        ('S010', 'Inpatient', 'General Ward Bed', 2500), 
        ('S011', 'Inpatient', 'HDU Bed', 18000), 
        ('S012', 'Inpatient', 'ICU Bed', 40000), 
        ('S013', 'Treatment', 'Casting (Hand/Leg Fracture)', 12500),
        ('S014', 'Treatment', 'Major Orthopedic Surgery', 280000),
        ('S015', 'Referral', 'Specialist Referral', 4500)
    ]
    services = pd.DataFrame(services_data, columns=['service_id', 'category', 'service_name', 'unit_cost_ksh'])

    # 4. Fact Table: Encounters
    encounters = []
    base_date = datetime(2023, 1, 1)
    wings = ['General Outpatient', 'Maternity', 'Emergency Room']
    pay_methods = ['Insurance', 'Personal Cash', 'Mobile Money']

    # Weighting factors to make Maternity the cash cow
    for i in range(num_encounters):
        enc_id = 10000 + i
        p_id = np.random.choice(patients['patient_id'])
        gender = patients.loc[patients['patient_id'] == p_id, 'gender'].values[0]
        
        # Wing Logic
        if gender == 'Female' and np.random.random() < 0.25:
            wing = 'Maternity'
        else:
            wing = np.random.choice(['General Outpatient', 'Emergency Room'], p=[0.75, 0.25])
            
        d_id = np.random.choice(doctors['doctor_id'])
        date = base_date + timedelta(days=np.random.randint(0, 365), hours=np.random.randint(0, 24))
        pay_method = np.random.choice(pay_methods, p=[0.65, 0.15, 0.2])
        
        cost_items = []
        stay_days = 0
        
        # Base Billing
        if wing != 'Emergency Room':
            cost_items.append(('S001', 2500))

        if wing == 'Maternity':
            delivery_type = np.random.choice(['S007', 'S008'], p=[0.6, 0.4])
            cost_items.append((delivery_type, services.loc[services['service_id']==delivery_type, 'unit_cost_ksh'].values[0]))
            
            stay_days = np.random.randint(2, 7)
            cost_items.append(('S010', 2500 * stay_days)) # Mother's Ward
            cost_items.append(('S009', 5000 * stay_days)) # Baby Area
            
        elif wing == 'Emergency Room':
            if np.random.random() < 0.7:
                diag = np.random.choice(['S003', 'S004', 'S005'], p=[0.5, 0.2, 0.3])
                cost_items.append((diag, services.loc[services['service_id']==diag, 'unit_cost_ksh'].values[0]))
            
            if np.random.random() < 0.3:
                acc_treat = np.random.choice(['S013', 'S014'], p=[0.7, 0.3])
                cost_items.append((acc_treat, services.loc[services['service_id']==acc_treat, 'unit_cost_ksh'].values[0]))
                
            if np.random.random() < 0.1:
                stay_days = np.random.randint(1, 12)
                cost_items.append(('S012', 40000 * stay_days))
        
        else:
            if np.random.random() < 0.4: cost_items.append(('S002', 1500))
            if np.random.random() < 0.5: cost_items.append(('S006', 1200))

        total_cost = sum([item[1] for item in cost_items])
        
        encounters.append({
            'encounter_id': enc_id,
            'patient_id': p_id,
            'doctor_id': d_id,
            'date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'wing': wing,
            'payment_method': pay_method,
            'stay_duration_days': stay_days,
            'total_bill_ksh': total_cost,
            'is_inpatient': 1 if stay_days > 0 else 0,
            'primary_service_id': cost_items[1][0] if len(cost_items) > 1 else (cost_items[0][0] if cost_items else 'S001')
        })

    df_encounters = pd.DataFrame(encounters)

    os.makedirs('tableau_export', exist_ok=True)
    patients.to_csv('tableau_export/dim_patients.csv', index=False)
    doctors.to_csv('tableau_export/dim_doctors.csv', index=False)
    services.to_csv('tableau_export/dim_services.csv', index=False)
    df_encounters.to_csv('tableau_export/fact_encounters.csv', index=False)
    
    return {
        'row_counts': {
            'patients': len(patients),
            'doctors': len(doctors),
            'services': len(services),
            'encounters': len(df_encounters)
        },
        'files': ['dim_patients.csv', 'dim_doctors.csv', 'dim_services.csv', 'fact_encounters.csv']
    }

if __name__ == "__main__":
    import json
    result = generate_st_bonaventure_data()
    print(json.dumps(result))
