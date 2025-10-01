import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Incident Analyzer", layout="wide")
st.title("🚨 Incident Analyzer Dashboard")

# Upload or load file
uploaded_file = st.file_uploader("Upload incident.xlsx", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['Opened'] = pd.to_datetime(df['Opened'], errors='coerce')
    st.success(f"Loaded {len(df)} incidents from {df['Opened'].min()} to {df['Opened'].max()}.")

    # Filters
    st.sidebar.header("Filters")
    priorities = st.sidebar.multiselect("Priority", df['Priority'].unique(), default=df['Priority'].unique())
    states = st.sidebar.multiselect("State", df['State'].unique(), default=df['State'].unique())
    date_range = st.sidebar.date_input("Date Range", [df['Opened'].min().date(), df['Opened'].max().date()])

    filtered_df = df[(df['Priority'].isin(priorities)) & (df['State'].isin(states)) & 
                     (df['Opened'].dt.date.between(date_range[0], date_range[1]))]

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidents", len(filtered_df))
    col2.metric("Avg Duration (hours)", round(filtered_df['Business duration'].mean() / 3600, 2))
    col3.metric("Medium Priority %", f"{(len(filtered_df[filtered_df['Priority']=='3 - Medium']) / len(filtered_df) * 100):.1f}%" if len(filtered_df) > 0 else 0)

    # Breakdowns
    st.header("Breakdowns")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("By Priority")
        pri_df = filtered_df['Priority'].value_counts().reset_index()
        st.dataframe(pri_df)
        fig_pri = px.pie(pri_df, values='count', names='Priority', title="Priority Distribution")
        st.plotly_chart(fig_pri)

    with col2:
        st.subheader("Top Issue Types")
        top_issues = filtered_df['Short description'].value_counts().head(10).reset_index()
        st.dataframe(top_issues)
        fig_issues = px.bar(top_issues, x='count', y='Short description', orientation='h', title="Top 10 Issues")
        st.plotly_chart(fig_issues)

    # Trends
    st.header("Trends")
    if 'Opened' in df.columns:
        daily = filtered_df.resample('D', on='Opened').size().reset_index(name='Count')
        fig_trend = px.line(daily, x='Opened', y='Count', title="Daily Incident Trend")
        st.plotly_chart(fig_trend)

    # Raw Data
    st.header("Raw Data")
    st.dataframe(filtered_df)
else:
    st.info("Upload incident.xlsx to start.")
