"""
Interactive OLAP Operations Dashboard
Hospital Data Warehouse - St. Bonaventure Hospital
Group Assignment - Data Analytics

Run with: streamlit run streamlit_olap_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="OLAP Operations Dashboard",
    page_icon="🏥",
    layout="wide"
)

# Cache data loading
@st.cache_data
def load_data():
    """Load and prepare data warehouse"""
    dim_patients = pd.read_csv('dim_patients.csv')
    dim_doctors = pd.read_csv('dim_doctors.csv')
    dim_services = pd.read_csv('dim_services.csv')
    fact_encounters = pd.read_csv('fact_encounters.csv')
    
    # Convert date and add time dimensions
    fact_encounters['date'] = pd.to_datetime(fact_encounters['date'])
    fact_encounters['year'] = fact_encounters['date'].dt.year
    fact_encounters['month'] = fact_encounters['date'].dt.month
    fact_encounters['quarter'] = fact_encounters['date'].dt.quarter
    fact_encounters['month_name'] = fact_encounters['date'].dt.strftime('%B')
    fact_encounters['day_of_week'] = fact_encounters['date'].dt.day_name()
    
    # Join all tables
    data = fact_encounters.merge(dim_patients, on='patient_id', how='left')
    data = data.merge(dim_doctors, on='doctor_id', how='left')
    data = data.merge(dim_services, left_on='primary_service_id', right_on='service_id', how='left')
    
    return data, dim_patients, dim_doctors, dim_services, fact_encounters

# Load data
data, dim_patients, dim_doctors, dim_services, fact_encounters = load_data()

# Header
st.title("🏥 Hospital Data Warehouse - OLAP Operations")
st.markdown("### St. Bonaventure Hospital Analytics Dashboard")
st.markdown("---")

# Sidebar - OLAP Operation Selection
st.sidebar.title("📊 OLAP Operations")
st.sidebar.markdown("Select an operation to explore:")

operation = st.sidebar.radio(
    "Choose Operation:",
    ["📈 Overview", "🔼 Roll-Up", "🔽 Drill-Down", "✂️ Slice", "🎲 Dice", "🔄 Pivot"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Summary**")
st.sidebar.metric("Total Encounters", f"{len(data):,}")
st.sidebar.metric("Total Revenue", f"KSh {data['total_bill_ksh'].sum():,.0f}")
st.sidebar.metric("Avg Bill", f"KSh {data['total_bill_ksh'].mean():,.0f}")

# =============================================================================
# OVERVIEW
# =============================================================================
if operation == "📈 Overview":
    st.header("Data Warehouse Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Patients", f"{len(dim_patients):,}")
        st.metric("Doctors", f"{len(dim_doctors):,}")
    
    with col2:
        st.metric("Services", f"{len(dim_services):,}")
        st.metric("Encounters", f"{len(fact_encounters):,}")
    
    with col3:
        st.metric("Total Revenue", f"KSh {data['total_bill_ksh'].sum()/1e6:.1f}M")
        st.metric("Avg Age", f"{data['age'].mean():.1f} years")
    
    with col4:
        inpatient_count = data[data['is_inpatient'] == 1].shape[0]
        st.metric("Inpatient %", f"{inpatient_count/len(data)*100:.1f}%")
        st.metric("Avg Stay", f"{data[data['is_inpatient']==1]['stay_duration_days'].mean():.1f} days")
    
    st.markdown("---")
    
    # Revenue by Wing
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Wing")
        wing_revenue = data.groupby('wing')['total_bill_ksh'].sum().sort_values(ascending=True)
        fig = px.bar(
            x=wing_revenue.values,
            y=wing_revenue.index,
            orientation='h',
            labels={'x': 'Revenue (KSh)', 'y': 'Wing'},
            color=wing_revenue.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Encounters by Payment Method")
        payment_counts = data['payment_method'].value_counts()
        fig = px.pie(
            values=payment_counts.values,
            names=payment_counts.index,
            hole=0.4
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    st.subheader("Daily Revenue Trend")
    daily_revenue = data.groupby(data['date'].dt.date)['total_bill_ksh'].sum().reset_index()
    daily_revenue.columns = ['Date', 'Revenue']
    fig = px.line(
        daily_revenue,
        x='Date',
        y='Revenue',
        labels={'Revenue': 'Revenue (KSh)'}
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# ROLL-UP (AGGREGATION)
# =============================================================================
elif operation == "🔼 Roll-Up":
    st.header("🔼 Roll-Up (Aggregation)")
    st.markdown("""
    **Definition:** Aggregate data by climbing up the hierarchy (from detailed to summary level)
    
    **Example:** Daily → Monthly → Quarterly → Yearly
    """)
    
    st.markdown("---")
    
    # Time-based Roll-up
    st.subheader("Temporal Roll-Up: Revenue Aggregation")
    
    rollup_level = st.selectbox(
        "Select Aggregation Level:",
        ["Daily", "Monthly", "Quarterly", "Yearly"]
    )
    
    if rollup_level == "Daily":
        grouped = data.groupby(data['date'].dt.date).agg({
            'total_bill_ksh': 'sum',
            'encounter_id': 'count'
        }).reset_index()
        grouped.columns = ['Date', 'Revenue (KSh)', 'Encounters']
        x_col = 'Date'
        
    elif rollup_level == "Monthly":
        grouped = data.groupby(['year', 'month_name']).agg({
            'total_bill_ksh': 'sum',
            'encounter_id': 'count'
        }).reset_index()
        grouped.columns = ['Year', 'Month', 'Revenue (KSh)', 'Encounters']
        grouped['Period'] = grouped['Year'].astype(str) + '-' + grouped['Month']
        x_col = 'Period'
        
    elif rollup_level == "Quarterly":
        grouped = data.groupby(['year', 'quarter']).agg({
            'total_bill_ksh': 'sum',
            'encounter_id': 'count'
        }).reset_index()
        grouped.columns = ['Year', 'Quarter', 'Revenue (KSh)', 'Encounters']
        grouped['Period'] = grouped['Year'].astype(str) + '-Q' + grouped['Quarter'].astype(str)
        x_col = 'Period'
        
    else:  # Yearly
        grouped = data.groupby('year').agg({
            'total_bill_ksh': 'sum',
            'encounter_id': 'count'
        }).reset_index()
        grouped.columns = ['Year', 'Revenue (KSh)', 'Encounters']
        x_col = 'Year'
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            grouped,
            x=x_col,
            y='Revenue (KSh)',
            title=f"{rollup_level} Revenue",
            color='Revenue (KSh)',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            grouped,
            x=x_col,
            y='Encounters',
            title=f"{rollup_level} Encounter Count",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(grouped, use_container_width=True)
    
    st.markdown("---")
    
    # Geographic Roll-up
    st.subheader("Geographic Roll-Up")
    
    geo_level = st.radio(
        "Select Level:",
        ["Region + Residence Type", "Region Only", "Country Level"]
    )
    
    if geo_level == "Region + Residence Type":
        geo_data = data.groupby(['region', 'residence_type']).agg({
            'total_bill_ksh': 'sum',
            'encounter_id': 'count'
        }).reset_index()
        geo_data.columns = ['Region', 'Residence Type', 'Revenue (KSh)', 'Encounters']
        
    elif geo_level == "Region Only":
        geo_data = data.groupby('region').agg({
            'total_bill_ksh': 'sum',
            'encounter_id': 'count'
        }).reset_index()
        geo_data.columns = ['Region', 'Revenue (KSh)', 'Encounters']
        
    else:  # Country
        total_revenue = data['total_bill_ksh'].sum()
        total_encounters = len(data)
        st.metric("Kenya - Total Revenue", f"KSh {total_revenue:,.0f}")
        st.metric("Kenya - Total Encounters", f"{total_encounters:,}")
        geo_data = pd.DataFrame({
            'Country': ['Kenya'],
            'Revenue (KSh)': [total_revenue],
            'Encounters': [total_encounters]
        })
    
    st.dataframe(geo_data, use_container_width=True)

# =============================================================================
# DRILL-DOWN
# =============================================================================
elif operation == "🔽 Drill-Down":
    st.header("🔽 Drill-Down (Disaggregation)")
    st.markdown("""
    **Definition:** Break down aggregated data into finer details
    
    **Example:** Wing → Payment Method → Specialty → Individual Encounters
    """)
    
    st.markdown("---")
    
    drill_level = st.selectbox(
        "Select Drill-Down Level:",
        ["Level 1: By Wing", "Level 2: Wing + Payment Method", 
         "Level 3: Wing + Payment + Specialty", "Level 4: Individual Encounters"]
    )
    
    if drill_level == "Level 1: By Wing":
        drill_data = data.groupby('wing').agg({
            'total_bill_ksh': ['sum', 'mean', 'count']
        }).reset_index()
        drill_data.columns = ['Wing', 'Total Revenue', 'Avg Bill', 'Encounters']
        
        fig = px.bar(
            drill_data,
            x='Wing',
            y='Total Revenue',
            color='Wing',
            title="Revenue by Wing"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(drill_data, use_container_width=True)
        
    elif drill_level == "Level 2: Wing + Payment Method":
        drill_data = data.groupby(['wing', 'payment_method']).agg({
            'total_bill_ksh': 'sum',
            'encounter_id': 'count'
        }).reset_index()
        drill_data.columns = ['Wing', 'Payment Method', 'Revenue', 'Encounters']
        
        fig = px.bar(
            drill_data,
            x='Wing',
            y='Revenue',
            color='Payment Method',
            barmode='group',
            title="Revenue by Wing and Payment Method"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(drill_data, use_container_width=True)
        
    elif drill_level == "Level 3: Wing + Payment + Specialty":
        drill_data = data.groupby(['wing', 'payment_method', 'specialty']).agg({
            'total_bill_ksh': 'sum',
            'encounter_id': 'count'
        }).reset_index()
        drill_data.columns = ['Wing', 'Payment Method', 'Specialty', 'Revenue', 'Encounters']
        
        # Filter options
        selected_wing = st.selectbox("Filter by Wing:", ['All'] + list(data['wing'].unique()))
        if selected_wing != 'All':
            drill_data = drill_data[drill_data['Wing'] == selected_wing]
        
        st.dataframe(drill_data.sort_values('Revenue', ascending=False), use_container_width=True)
        
    else:  # Individual Encounters
        st.subheader("Individual Encounter Details")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_wing = st.selectbox("Wing:", ['All'] + list(data['wing'].unique()))
        with col2:
            selected_payment = st.selectbox("Payment Method:", ['All'] + list(data['payment_method'].unique()))
        with col3:
            selected_specialty = st.selectbox("Specialty:", ['All'] + list(data['specialty'].unique()))
        
        filtered_data = data.copy()
        if selected_wing != 'All':
            filtered_data = filtered_data[filtered_data['wing'] == selected_wing]
        if selected_payment != 'All':
            filtered_data = filtered_data[filtered_data['payment_method'] == selected_payment]
        if selected_specialty != 'All':
            filtered_data = filtered_data[filtered_data['specialty'] == selected_specialty]
        
        st.write(f"Showing {len(filtered_data):,} encounters")
        
        display_data = filtered_data[[
            'encounter_id', 'patient_id', 'doctor_name', 'date', 
            'wing', 'payment_method', 'total_bill_ksh', 'stay_duration_days'
        ]].head(100)
        
        st.dataframe(display_data, use_container_width=True)

# =============================================================================
# SLICE
# =============================================================================
elif operation == "✂️ Slice":
    st.header("✂️ Slice")
    st.markdown("""
    **Definition:** Select a single dimension value (creates a sub-cube)
    
    **Example:** Filter data for only 'Maternity' wing or only 'Q1 2023'
    """)
    
    st.markdown("---")
    
    slice_dimension = st.selectbox(
        "Select Dimension to Slice:",
        ["Wing", "Quarter", "Gender", "Region", "Insurance Provider", "Payment Method"]
    )
    
    if slice_dimension == "Wing":
        slice_value = st.selectbox("Select Wing:", data['wing'].unique())
        sliced_data = data[data['wing'] == slice_value]
        group_by = 'payment_method'
        
    elif slice_dimension == "Quarter":
        slice_value = st.selectbox("Select Quarter:", sorted(data['quarter'].unique()))
        sliced_data = data[data['quarter'] == slice_value]
        group_by = 'wing'
        
    elif slice_dimension == "Gender":
        slice_value = st.selectbox("Select Gender:", data['gender'].unique())
        sliced_data = data[data['gender'] == slice_value]
        group_by = 'wing'
        
    elif slice_dimension == "Region":
        slice_value = st.selectbox("Select Region:", data['region'].unique())
        sliced_data = data[data['region'] == slice_value]
        group_by = 'wing'
        
    elif slice_dimension == "Insurance Provider":
        slice_value = st.selectbox("Select Provider:", data['insurance_provider'].unique())
        sliced_data = data[data['insurance_provider'] == slice_value]
        group_by = 'wing'
        
    else:  # Payment Method
        slice_value = st.selectbox("Select Payment Method:", data['payment_method'].unique())
        sliced_data = data[data['payment_method'] == slice_value]
        group_by = 'wing'
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Encounters", f"{len(sliced_data):,}")
    with col2:
        st.metric("Total Revenue", f"KSh {sliced_data['total_bill_ksh'].sum():,.0f}")
    with col3:
        st.metric("Average Bill", f"KSh {sliced_data['total_bill_ksh'].mean():,.0f}")
    with col4:
        st.metric("% of Total", f"{len(sliced_data)/len(data)*100:.1f}%")
    
    st.markdown("---")
    
    # Breakdown
    st.subheader(f"Breakdown by {group_by.replace('_', ' ').title()}")
    
    breakdown = sliced_data.groupby(group_by).agg({
        'total_bill_ksh': ['sum', 'mean'],
        'encounter_id': 'count'
    }).reset_index()
    breakdown.columns = [group_by.title(), 'Total Revenue', 'Avg Bill', 'Encounters']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            breakdown,
            values='Total Revenue',
            names=group_by.title(),
            title=f"Revenue Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            breakdown,
            x=group_by.title(),
            y='Encounters',
            title=f"Encounter Count",
            color='Encounters',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(breakdown, use_container_width=True)

# =============================================================================
# DICE
# =============================================================================
elif operation == "🎲 Dice":
    st.header("🎲 Dice")
    st.markdown("""
    **Definition:** Select multiple dimension values (creates a smaller sub-cube)
    
    **Example:** Filter by multiple conditions simultaneously
    """)
    
    st.markdown("---")
    
    st.subheader("Select Multiple Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        wings = st.multiselect("Wing:", data['wing'].unique(), default=list(data['wing'].unique()))
        payments = st.multiselect("Payment Method:", data['payment_method'].unique(), 
                                  default=list(data['payment_method'].unique()))
    
    with col2:
        regions = st.multiselect("Region:", data['region'].unique(), default=list(data['region'].unique()))
        genders = st.multiselect("Gender:", data['gender'].unique(), default=list(data['gender'].unique()))
    
    with col3:
        quarters = st.multiselect("Quarter:", sorted(data['quarter'].unique()), 
                                  default=list(data['quarter'].unique()))
        age_range = st.slider("Age Range:", 0, 100, (0, 100))
    
    # Apply filters
    diced_data = data[
        (data['wing'].isin(wings)) &
        (data['payment_method'].isin(payments)) &
        (data['region'].isin(regions)) &
        (data['gender'].isin(genders)) &
        (data['quarter'].isin(quarters)) &
        (data['age'] >= age_range[0]) &
        (data['age'] <= age_range[1])
    ]
    
    # Metrics
    st.markdown("---")
    st.subheader("Filtered Results")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Encounters", f"{len(diced_data):,}")
    with col2:
        st.metric("Total Revenue", f"KSh {diced_data['total_bill_ksh'].sum():,.0f}")
    with col3:
        st.metric("Avg Bill", f"KSh {diced_data['total_bill_ksh'].mean():,.0f}")
    with col4:
        if diced_data[diced_data['is_inpatient'] == 1].shape[0] > 0:
            avg_stay = diced_data[diced_data['is_inpatient'] == 1]['stay_duration_days'].mean()
            st.metric("Avg Stay", f"{avg_stay:.1f} days")
        else:
            st.metric("Avg Stay", "N/A")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Wing")
        wing_data = diced_data.groupby('wing')['total_bill_ksh'].sum().reset_index()
        fig = px.bar(wing_data, x='wing', y='total_bill_ksh', color='wing')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Encounters by Specialty")
        specialty_data = diced_data.groupby('specialty')['encounter_id'].count().reset_index()
        specialty_data.columns = ['Specialty', 'Count']
        specialty_data = specialty_data.sort_values('Count', ascending=False)
        fig = px.bar(specialty_data, x='Count', y='Specialty', orientation='h')
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("Sample Data")
    display_cols = ['encounter_id', 'date', 'wing', 'payment_method', 'region', 
                   'gender', 'age', 'specialty', 'total_bill_ksh']
    st.dataframe(diced_data[display_cols].head(50), use_container_width=True)

# =============================================================================
# PIVOT
# =============================================================================
elif operation == "🔄 Pivot":
    st.header("🔄 Pivot (Rotation)")
    st.markdown("""
    **Definition:** Rotate the data cube to view from different perspectives
    
    **Example:** Transform rows into columns to change the view
    """)
    
    st.markdown("---")
    
    pivot_type = st.selectbox(
        "Select Pivot Analysis:",
        ["Wing × Payment Method", "Specialty × Quarter", "Region × Gender", 
         "Month × Wing", "Custom Pivot"]
    )
    
    if pivot_type == "Wing × Payment Method":
        pivot_table = pd.pivot_table(
            data,
            values='total_bill_ksh',
            index='wing',
            columns='payment_method',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        st.subheader("Revenue by Wing (rows) × Payment Method (columns)")
        st.dataframe(pivot_table, use_container_width=True)
        
        # Heatmap
        fig = px.imshow(
            pivot_table.set_index('wing'),
            labels=dict(x="Payment Method", y="Wing", color="Revenue (KSh)"),
            color_continuous_scale='YlOrRd',
            title="Revenue Heatmap"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif pivot_type == "Specialty × Quarter":
        pivot_table = pd.pivot_table(
            data,
            values='encounter_id',
            index='specialty',
            columns='quarter',
            aggfunc='count',
            fill_value=0
        ).reset_index()
        
        st.subheader("Encounters by Specialty (rows) × Quarter (columns)")
        st.dataframe(pivot_table, use_container_width=True)
        
        # Heatmap
        fig = px.imshow(
            pivot_table.set_index('specialty'),
            labels=dict(x="Quarter", y="Specialty", color="Encounters"),
            color_continuous_scale='Blues',
            title="Encounter Count Heatmap"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif pivot_type == "Region × Gender":
        pivot_table = pd.pivot_table(
            data,
            values='total_bill_ksh',
            index='region',
            columns='gender',
            aggfunc='mean',
            fill_value=0
        ).round(0).reset_index()
        
        st.subheader("Average Bill by Region (rows) × Gender (columns)")
        st.dataframe(pivot_table, use_container_width=True)
        
        # Grouped bar chart
        pivot_melted = pivot_table.melt(id_vars='region', var_name='Gender', value_name='Avg Bill')
        fig = px.bar(
            pivot_melted,
            x='region',
            y='Avg Bill',
            color='Gender',
            barmode='group',
            title="Average Bill by Region and Gender"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif pivot_type == "Month × Wing":
        pivot_table = pd.pivot_table(
            data,
            values='total_bill_ksh',
            index='month',
            columns='wing',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        st.subheader("Revenue by Month (rows) × Wing (columns)")
        st.dataframe(pivot_table, use_container_width=True)
        
        # Line chart
        pivot_melted = pivot_table.melt(id_vars='month', var_name='Wing', value_name='Revenue')
        fig = px.line(
            pivot_melted,
            x='month',
            y='Revenue',
            color='Wing',
            markers=True,
            title="Monthly Revenue by Wing"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:  # Custom Pivot
        st.subheader("Custom Pivot Table")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            index_col = st.selectbox("Rows (Index):", 
                ['wing', 'specialty', 'region', 'payment_method', 'quarter', 'month', 'gender'])
        
        with col2:
            columns_col = st.selectbox("Columns:", 
                ['payment_method', 'wing', 'quarter', 'gender', 'region', 'specialty'])
        
        with col3:
            value_col = st.selectbox("Values:", ['total_bill_ksh', 'encounter_id', 'stay_duration_days'])
            agg_func = st.selectbox("Aggregation:", ['sum', 'mean', 'count'])
        
        pivot_table = pd.pivot_table(
            data,
            values=value_col,
            index=index_col,
            columns=columns_col,
            aggfunc=agg_func,
            fill_value=0
        ).reset_index()
        
        st.dataframe(pivot_table, use_container_width=True)
        
        # Heatmap
        try:
            fig = px.imshow(
                pivot_table.set_index(index_col),
                labels=dict(color=f"{value_col} ({agg_func})"),
                color_continuous_scale='Viridis',
                title=f"{value_col.replace('_', ' ').title()} - {agg_func.title()}"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Heatmap not available for this combination")

# Footer
st.markdown("---")
st.markdown("**Group Assignment - Data Analytics** | St. Bonaventure Hospital Data Warehouse")
