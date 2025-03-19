import streamlit as st
import pandas as pd
import plotly.express as px

def detect_header_row(df):
    """
    Detect the header row dynamically by finding the row 
    where column 1 (Index 0) contains '#' or 'Ticket'.
    """
    for index, row in df.iterrows():
        if str(row.iloc[0]).strip().lower() in ["#", "ticket"]:
            return index
    return None  # Return None if no valid header is found

def load_and_clean_data(uploaded_files):
    """Load and clean data from valid sheets ('Data' or 'Report') in multiple Excel files."""
    reports = {}

    for file in uploaded_files:
        try:
            xls = pd.ExcelFile(file, engine="openpyxl")

            # Check if 'Data' or 'Report' sheet exists
            valid_sheets = [sheet for sheet in xls.sheet_names if sheet.lower() in ["data", "report"]]

            if not valid_sheets:
                st.warning(f"⚠️ Skipping {file.name}: No valid sheet ('Data' or 'Report') found.")
                continue

            # Read the first valid sheet
            df_raw = pd.read_excel(xls, sheet_name=valid_sheets[0], header=None)

            # Detect the correct header row dynamically
            header_row = detect_header_row(df_raw)
            if header_row is None:
                st.warning(f"⚠️ Skipping {file.name}: Could not detect a valid header row.")
                continue

            # Read the data again with the correct header row
            df = pd.read_excel(xls, sheet_name=valid_sheets[0], header=header_row)

            # Normalize column names (strip spaces, lowercase)
            df.columns = df.columns.str.strip().str.lower()

            # Rename columns if necessary
            rename_map = {
                "#": "ticket",
                "ticket": "ticket",
                "request user": "request_user",
                "close time": "close_time",
                "request time": "request_time"
            }
            df.rename(columns=rename_map, inplace=True)

            # Ensure required columns exist
            required_columns = {"request_user", "close_time", "request_time"}
            if not required_columns.issubset(df.columns):
                st.warning(f"⚠️ Skipping {file.name}: Missing required columns {required_columns}.")
                continue

            # Convert datetime columns
            df["request_time"] = pd.to_datetime(df["request_time"], errors="coerce")
            df["close_time"] = pd.to_datetime(df["close_time"], errors="coerce")

            # Calculate Resolution Time in minutes
            df["resolution_time"] = (df["close_time"] - df["request_time"]).dt.total_seconds() / 60

            reports[file.name] = df

        except Exception as e:
            st.error(f"🚨 Error loading {file.name}: {str(e)}")

    return reports


def plot_total_requests(reports):
    """Interactive bar chart comparing total requests across multiple reports."""
    total_counts = {name: len(df) for name, df in reports.items()}
    
    if not total_counts:
        st.warning("⚠️ No valid data for Total Requests comparison.")
        return

    df_total = pd.DataFrame(list(total_counts.items()), columns=["Report", "Total Requests"])

    fig = px.bar(df_total, x="Report", y="Total Requests", text="Total Requests",
                 title="📊 Total Requests Comparison", color="Total Requests",
                 color_continuous_scale="Blues")

    fig.update_traces(texttemplate='%{text}', textposition='outside',
                      marker=dict(line=dict(color='black', width=1)))  # Add border

    fig.update_layout(xaxis_title="", yaxis_title="Total Requests")
    
    st.plotly_chart(fig, use_container_width=True)

def plot_response_time(reports):
    """Interactive box plot for response time distribution in minutes."""
    all_data = []

    for name, df in reports.items():
        if "resolution_time" in df.columns and not df["resolution_time"].isna().all():
            df_filtered = df[["resolution_time"]].dropna()
            df_filtered["Report"] = name
            all_data.append(df_filtered)

    if not all_data:
        st.warning("⚠️ No valid response time data available.")
        return

    df_combined = pd.concat(all_data)

    fig = px.box(df_combined, x="Report", y="resolution_time", 
                 title="⏳ Response Time & Ticket Aging", 
                 color="Report", points="all")

    fig.update_traces(marker=dict(line=dict(color='black', width=1)))  # Add border
    fig.update_layout(xaxis_title="", yaxis_title="Resolution Time (Minutes)")
    
    st.plotly_chart(fig, use_container_width=True)

import plotly.express as px
import streamlit as st
import pandas as pd

import plotly.express as px
import streamlit as st
import pandas as pd

def plot_aging_report(reports):
    """Interactive scatter plot for aging report (resolution time per ticket)."""
    all_data = []

    for name, df in reports.items():
        if "resolution_time" in df.columns and not df["resolution_time"].isna().all():
            df_filtered = df[["ticket", "resolution_time"]].dropna()
            df_filtered["Report"] = name
            all_data.append(df_filtered)

    if not all_data:
        st.warning("⚠️ No valid aging data available.")
        return

    df_combined = pd.concat(all_data)

    # High-contrast color palette
    contrast_colors = ["#FF0000", "#0000FF", "#00FF00", "#FFA500", "#800080", "#FFC0CB", "#8B0000"]

    fig = px.scatter(df_combined, 
                     x="ticket", 
                     y="resolution_time", 
                     color="Report",
                     title="📋 Aging Report (Minutes)",
                     labels={"ticket": "Ticket ID", "resolution_time": "Resolution Time (Minutes)"},
                     color_discrete_sequence=contrast_colors)  # Apply high-contrast colors

    # Add a border to points for visibility
    fig.update_traces(marker=dict(line=dict(color='black', width=1)))  

    # Improve layout
    fig.update_layout(xaxis_title="Ticket ID", yaxis_title="Resolution Time (Minutes)")

    st.plotly_chart(fig, use_container_width=True)


def compare_reports(uploaded_files):
    """Main function to compare multiple reports."""
    reports = load_and_clean_data(uploaded_files)

    if not reports:
        st.error("🚨 No valid data found in the uploaded reports.")
        return

    st.subheader("📊 Total Requests")
    plot_total_requests(reports)

    st.subheader("⏳ Response Time & Ticket Aging")
    plot_response_time(reports)

    st.subheader("📋 Aging Report (Minutes)")
    plot_aging_report(reports)
