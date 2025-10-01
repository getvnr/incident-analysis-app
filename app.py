import pandas as pd
import streamlit as st
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.title('Incident Analysis Web App')

# Upload file
uploaded_file = st.file_uploader('Upload incident.xlsx', type='xlsx')
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Ensure 'Opened' is datetime
    df['Opened'] = pd.to_datetime(df['Opened'], errors='coerce')
    df['Month'] = df['Opened'].dt.to_period('M').astype(str)  # Convert to string for display
    
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
    
    # Create pivot table
    pivot = pd.pivot_table(df, index='Month', columns='Incident Type', aggfunc='size', fill_value=0)
    
    # Download pivot table as Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Pivot Table')
        return output.getvalue()
    
    pivot_excel = to_excel(pivot)
    st.download_button(
        label="Download Pivot Table as Excel",
        data=pivot_excel,
        file_name=f"pivot_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Display pivot table
    st.subheader('Pivot Table: Incidents by Month and Type')
    st.dataframe(pivot)
    
    # Interactive selection for filtering incidents
    st.subheader('Filter Incidents by Month and Type')
    selected_month = st.selectbox('Select Month', sorted(pivot.index))
    selected_type = st.selectbox('Select Incident Type', sorted(pivot.columns))
    
    # Filter incidents based on selection
    if selected_month and selected_type:
        filtered_df = df[(df['Month'] == selected_month) & (df['Incident Type'] == selected_type)]
        st.write(f"Showing {len(filtered_df)} incidents for {selected_type} in {selected_month}")
        st.dataframe(filtered_df[['Number', 'Opened', 'Short description', 'Assigned to', 'State']])
        
        # Download filtered incidents as Excel
        filtered_excel = to_excel(filtered_df)
        st.download_button(
            label=f"Download Filtered Incidents ({selected_month}, {selected_type})",
            data=filtered_excel,
            file_name=f"filtered_incidents_{selected_month}_{selected_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Bar chart for most frequent types
    type_counts = df['Incident Type'].value_counts().reset_index()
    type_counts.columns = ['Incident Type', 'Count']
    fig_types = px.bar(type_counts, x='Incident Type', y='Count', title='Most Frequent Incident Types',
                       color_discrete_sequence=['#1f77b4'])  # Blue for visibility
    st.plotly_chart(fig_types)
    
    # Line chart for month-wise totals
    month_counts = df.groupby('Month').size().reset_index()
    month_counts.columns = ['Month', 'Count']
    fig_month = px.line(month_counts, x='Month', y='Count', title='Month-wise Total Incidents',
                        color_discrete_sequence=['#ff7f0e'])  # Orange for visibility
    st.plotly_chart(fig_month)
else:
    st.write('Please upload the incident Excel file.')
