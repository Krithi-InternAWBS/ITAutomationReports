from gc import get_stats
import streamlit as st
import pandas as pd
from src.itautomationreports.data_loader import load_data, clean_data
from src.itautomationreports.filters import filter_by_time
from src.itautomationreports.visualization import (
    plot_priority_vs_resolution_time, plot_requests_by_priority, plot_sla_compliance, plot_ticket_trends, plot_time_of_day_heatmap,
    plot_response_time, plot_ticket_aging, plot_total_requests,
    plot_requests_by_category, plot_requests_by_process_manager,plot_user_request_analysis,
    plot_sla_performance, plot_avg_closure_time, plot_due_date_analysis,plot_time_taken_box_plot,
    plot_request_completion_status, plot_requests_by_status, plot_aging_report_table,
    plot_urgent_requests,plot_request_volume_trend,plot_peak_request_times,plot_most_common_request_categories,plot_recurring_issues)


from src.itautomationreports.comparision import compare_reports   

def main():
    st.set_page_config(page_title="IT Automation Reports", layout="wide")
    st.title('📊 Multi-Report Ticket Analysis Dashboard')

    # Sidebar - File Upload
    uploaded_files = st.sidebar.file_uploader("Upload Excel files", type=["xlsx", "xls"], accept_multiple_files=True)

    if uploaded_files:
        try:
            df, file_names = load_data(uploaded_files)
            if df is not None and not df.empty:
                df = clean_data(df)  # Clean and process the data

                # Sidebar - Filters
                st.sidebar.header("Filters")
                source_filter = st.sidebar.selectbox("Select Report Source", ["All Reports"] + file_names)
                time_filter = st.sidebar.selectbox("Time Period", ["All Time", "Last 90 Days", "Last 30 Days", "Last 7 Days"])

                # Apply filters
                filtered_df = filter_by_time(df, time_filter)
                if source_filter != "All Reports":
                    filtered_df = filtered_df[filtered_df['Source'] == source_filter]

                # Display summary of applied filters
                st.sidebar.markdown(f"✅ **Total Tickets After Filtering:** `{len(filtered_df)}`")
                st.sidebar.markdown(f"📅 **Selected Time Period:** `{time_filter}`")
                st.sidebar.markdown(f"📂 **Selected Report Source:** `{source_filter}`")

                # Ensure data exists after filtering
                if filtered_df.empty:
                    st.warning("⚠️ No data available after applying filters.")
                    return

                            # Tabs for different analyses
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overall Insights", 
    "📉 Response Time & Ticket Aging", 
    "📌 Request Status Report", 
    "👤 User Request Analysis",  # ✅ New Tab for User Analysis
    "🔄 Comparisons"  # ✅ Moved to last
])


                with tab1:
                    st.subheader("📊 Overall Ticket Insights")

                    # Display Total Requests & SLA Compliance side by side with better spacing
                    col1, col2 = st.columns([1, 1])  # Equal width to minimize gap

                    with col1:
                        plot_total_requests(filtered_df)  # ✅ Total request count

                    with col2:
                        plot_sla_compliance(filtered_df)  # ✅ SLA Compliance

                    # Reduce vertical spacing before the next visualizations
                    st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)

                    # Keep other visualizations below
                    plot_ticket_trends(filtered_df)
                    plot_time_of_day_heatmap(filtered_df)

                    # ==================== 🗓️ NEW: Monthly/Quarterly Trends ====================
                    st.subheader("🗓️ Monthly & Quarterly Trends")

                    col3, col4 = st.columns([1, 1])  # Equal width layout
                    with col3:
                        plot_request_volume_trend(filtered_df)  # 📈 Line Chart: Request Volume Trend

                    with col4:
                        plot_peak_request_times(filtered_df)  # 📊 Bar Chart: Peak Request Times

                    st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
                      # **📑 SLA Performance Report**
                    st.subheader("📑 SLA Performance Report")

                    # Side-by-side layout for SLA Performance charts
                    col3, col4 = st.columns([1, 1])
                    with col3:
                        plot_sla_performance(filtered_df)  # ✅ Stacked Column Chart: SLA Met vs. SLA Breached

                    with col4:
                        plot_avg_closure_time(filtered_df)  # ✅ Card Visual: Average Time to Close Requests
                        plot_due_date_analysis(filtered_df)  # ✅ Bar Chart: Closed Before, On, or After Due Date

                    st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)

                with tab2:
                    st.subheader("📉 Response Time & Ticket Aging")

                    # Side-by-side layout for Response Time & Ticket Aging
                    col1, col2 = st.columns(2)
                    with col1:
                        plot_response_time(filtered_df)
                    with col2:
                        plot_ticket_aging(filtered_df)

                    # Debugging: Show available columns
                    st.sidebar.write("📋 **Final Processed Columns:**", list(filtered_df.columns))

                    # Ensure column names have no leading/trailing spaces
                    filtered_df.columns = filtered_df.columns.str.strip()

                    # Debugging: Show unique Categories & Sub-Categories
                    if "Category" in filtered_df.columns and "Sub-Category" in filtered_df.columns:
                        unique_categories = filtered_df["Category"].dropna().unique()
                        unique_subcategories = filtered_df["Sub-Category"].dropna().unique()
                        st.sidebar.write("📌 **Unique Categories:**", unique_categories)
                        st.sidebar.write("📌 **Unique Sub-Categories:**", unique_subcategories)

                    # Ensure 'Category' and 'Sub-Category' columns exist before plotting
                    if "Category" in filtered_df.columns and "Sub-Category" in filtered_df.columns and not filtered_df["Category"].dropna().empty:
                        plot_requests_by_category(filtered_df)
                    else:
                        st.warning("⚠️ 'Category' or 'Sub-Category' column is missing or contains no data.")

                    # Ensure 'Process manager' column exists before plotting
                    if "Process manager" in filtered_df.columns and filtered_df["Process manager"].dropna().any():
                        plot_requests_by_process_manager(filtered_df)

                        # ✅ Added: Box Plot for Time Taken by Process Managers
                        st.subheader("📦 Time Taken Distribution by Process Manager")
                        plot_time_taken_box_plot(filtered_df)

                    else:
                        st.warning("⚠️ 'Process manager' column is missing or contains no data.")

                    st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)

                                            
                   
                with tab3:
                    st.subheader("📌 Request Status Report")

                    # Donut Chart: Pending vs. Completed Requests
                    if "Status" in filtered_df.columns:
                        plot_request_completion_status(filtered_df)  # ✅ Donut Chart
                    else:
                        st.warning("⚠️ 'Status' column is missing from the dataset.")

                    # Stacked Bar Chart: Requests by Status (Open, In Progress, Closed, etc.)
                    if "Status" in filtered_df.columns:
                        plot_requests_by_status(filtered_df)  # ✅ Stacked Bar Chart
                    else:
                        st.warning("⚠️ 'Status' column is missing from the dataset.")

                    # Table: Aging Report (Requests Open for 30+, 60+, 90+ Days)
                    if "Ticket Aging" in filtered_df.columns:
                        plot_aging_report_table(filtered_df)  # ✅ Aging Table
                    else:
                        st.warning("⚠️ 'Ticket Aging' column is missing from the dataset.")

                                        # ==================== 🔥 Priority & Urgency Report ====================
                    st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
                    st.subheader("🔥 Priority & Urgency Report")

                    col1, col2 = st.columns(2)

                    with col1:
                        if "Priority" in filtered_df.columns:
                            plot_requests_by_priority(filtered_df)  # ✅ Bar Chart: High, Medium, Low
                        else:
                            st.warning("⚠️ 'Priority' column is missing from the dataset.")

                    with col2:
                        if "Urgency" in filtered_df.columns:
                            plot_urgent_requests(filtered_df)  # ✅ Pie Chart: Urgent Requests Breakdown
                        else:
                            st.warning("⚠️ 'Urgency' column is missing from the dataset.")

                    # Line Chart: Impact of Priority on Resolution Time
                    if "Priority" in filtered_df.columns and "Resolution Time" in filtered_df.columns:
                        plot_priority_vs_resolution_time(filtered_df)  # ✅ Line Chart
                    else:
                        st.warning("⚠️ 'Priority' or 'Resolution Time' column is missing from the dataset.")

                    # ==================== 🛠️ NEW: Root Cause Analysis ====================
                    st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
                    st.subheader("🛠️ Root Cause Analysis")

                    col3, col4 = st.columns([1, 1])  # Equal width layout
                    with col3:
                        if "Category" in filtered_df.columns:
                            plot_most_common_request_categories(filtered_df)  # 📊 Pie Chart: Most Common Categories
                        else:
                            st.warning("⚠️ 'Category' column is missing from the dataset.")

                    with col4:
                        if "Category" in filtered_df.columns and "Title" in filtered_df.columns:
                            plot_recurring_issues(filtered_df)  # 📊 Stacked Bar Chart: Recurring Issues
                        else:
                            st.warning("⚠️ 'Category' or 'Title' column is missing from the dataset.")
                
                with tab4:
                        st.header("👤 User Request & Resolution Analysis")
                        plot_user_request_analysis(df)  # ✅ Uses the already loaded dataframe
                     
                with tab5:
                    st.header("📈 Compare Multiple Reports")

                    # Allow user to upload multiple reports
                    allow_multiple = st.checkbox("Enable Multiple Report Comparison", value=True)

                    uploaded_files = st.file_uploader(
                        "Upload Excel Reports",
                        type=["xlsx"],
                        accept_multiple_files=allow_multiple
                    )

                    if uploaded_files:
                        st.write("📂 **Uploaded Files:**", [file.name for file in uploaded_files])

                        valid_files = []

                        for file in uploaded_files:
                            try:
                                # Load Excel file and check for valid sheets
                                xls = pd.ExcelFile(file, engine="openpyxl")
                                valid_sheets = [sheet for sheet in xls.sheet_names if sheet.lower() in ["data", "report"]]

                                if valid_sheets:
                                    valid_files.append(file)
                                else:
                                    st.warning(f"⚠️ Skipping {file.name}: No valid sheets found (Data/Report).")

                            except Exception as e:
                                st.error(f"🚨 Error reading {file.name}: {e}")

                        # Call function to process and compare reports if valid files exist
                        if valid_files:
                            compare_reports(valid_files)
                        else:
                            st.error("🚨 No valid reports found. Please upload correct Excel files.")


        except Exception as e:
            st.error(f"🚨 Error: {e}")
            return

    else:
        st.info("📤 Please upload one or more Excel files to proceed.")

if __name__ == "__main__":
    main()
