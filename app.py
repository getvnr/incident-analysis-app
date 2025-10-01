import pandas as pd
import streamlit as st
import plotly.express as px

st.title('Incident Analysis Web App')

# Upload file
uploaded_file = st.file_uploader('Upload incident.xlsx', type='xlsx')
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Ensure 'Opened' is datetime
    df['Opened'] = pd.to_datetime(df['Opened'], errors='coerce')
    df['Month'] = df['Opened'].dt.to_period('M')
    
    # Categorize incidents
    def categorize_incident(desc):
        if pd.isna(desc):
            return 'Unknown'
        desc = str(desc).lower()
        if 'log monitoring - websphere - instance may be hung' in desc:
            return 'WebSphere Hung Error'
        elif 'f5 ltm - pool member is unavailable' in desc:
            return 'F5 Pool Member Unavailable'
        elif 'failure rate increase' in desc:
            return 'Failure Rate Increase'
        elif 'group of alerts' in desc:
            return 'Group of Alerts'
        elif 'long garbage-collection time' in desc:
            return 'Long GC Time'
        elif 'connectivity problem' in desc:
            return 'Connectivity Problem'
        elif 'multiple infrastructure problems' in desc:
            return 'Multiple Infrastructure Problems'
        elif 'multiple service problems' in desc:
            return 'Multiple Service Problems'
        elif 'control-m' in desc:
            return 'Control-M Alert'
        else:
            return 'Other'
    
    df['Incident Type'] = df['Short description'].apply(categorize_incident)
    
    # Pivot table
    pivot = pd.pivot_table(df, index='Month', columns='Incident Type', aggfunc='size', fill_value=0)
    st.subheader('Pivot Table: Incidents by Month and Type')
    st.dataframe(pivot)
    
    # Bar chart for most frequent types
    type_counts = df['Incident Type'].value_counts().reset_index()
    type_counts.columns = ['Incident Type', 'Count']
    fig_types = px.bar(type_counts, x='Incident Type', y='Count', title='Most Frequent Incident Types')
    st.plotly_chart(fig_types)
    
    # Line chart for month-wise totals
    month_counts = df.groupby('Month').size().reset_index()
    month_counts.columns = ['Month', 'Count']
    month_counts['Month'] = month_counts['Month'].astype(str)
    fig_month = px.line(month_counts, x='Month', y='Count', title='Month-wise Total Incidents')
    st.plotly_chart(fig_month)
else:
    st.write('Please upload the incident Excel file.')
