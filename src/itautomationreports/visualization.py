import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd

def plot_sla_compliance(df):
    if "SLA" not in df.columns or df.empty:
        st.warning("SLA column is missing or dataset is empty.")
        return

    # Convert SLA to numeric: Met -> 1, Fail -> 0
    sla_mapping = {"Met": 1, "Fail": 0}
    df["SLA_Numeric"] = df["SLA"].map(sla_mapping)

    # Calculate SLA compliance rate
    sla_rate = df["SLA_Numeric"].mean() * 100 if not df["SLA_Numeric"].isna().all() else 0

    # Custom HTML & CSS for bordered card with inline-block styling
    st.markdown(f"""
        <div style="
            display: inline-block;
            width: 48%;
            border: 2px solid #2196F3; 
            border-radius: 10px; 
            padding: 15px; 
            text-align: center; 
            background-color: #f9f9f9; 
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
            <h3 style="color: #2196F3; margin-bottom: 5px;">SLA Compliance</h3>
            <h2 style="color: black;">{sla_rate:.1f}%</h2>
        </div>
    """, unsafe_allow_html=True)


import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import pandas as pd
import streamlit as st

def plot_ticket_trends(df):
    """Bar Chart: Monthly Ticket Trends with Numbers Inside Bars"""
    
    if "Request time" not in df.columns or df.empty:
        st.warning("⚠️ 'Request time' column is missing or dataset is empty.")
        return

    # Convert to datetime
    df["Request time"] = pd.to_datetime(df["Request time"], errors="coerce")

    # Count tickets per month
    ticket_trends = df["Request time"].dt.to_period("M").value_counts().sort_index()

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(ticket_trends.index.astype(str), ticket_trends.values, color="royalblue")

    # Add numbers inside bars with a black border
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            text = ax.text(
                bar.get_x() + bar.get_width() / 2,  # X position
                bar.get_height() / 2,  # Y position (middle of the bar)
                str(int(height)),  # Convert count to integer
                ha="center", va="center", fontsize=12, color="white", fontweight="bold"
            )
            text.set_path_effects([
                path_effects.withStroke(linewidth=3, foreground="black")  # Black border for better visibility
            ])

    # Set labels and title
    ax.set_title("📈 Ticket Trends Over Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Ticket Count", fontsize=12)
    ax.set_xticklabels(ticket_trends.index.astype(str), rotation=45, ha="right")

    # Display plot in Streamlit
    st.pyplot(fig)


def plot_time_of_day_heatmap(df):
    if "Request time" not in df.columns or "Ticket" not in df.columns or df.empty:
        st.warning("Request time or Ticket column is missing or dataset is empty.")
        return

    df["Request time"] = pd.to_datetime(df["Request time"], errors="coerce")
    df["Hour"] = df["Request time"].dt.hour

    pivot = df.pivot_table(
        values="Ticket",
        index=df["Request time"].dt.day_name(),
        columns="Hour",
        aggfunc="count",
        fill_value=0,
    )

    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(pivot, cmap="YlGnBu", annot=True, fmt="g", ax=ax)
    ax.set_title("Tickets Raised by Time of Day and Day of Week")
    st.pyplot(fig)

def plot_response_time(df, source_filter=None):
    if df.empty or "Response Time" not in df.columns:
        st.warning("No data available for response time analysis.")
        return

    # Filter data if a specific source report is selected
    if source_filter:
        df = df[df["Source"] == source_filter]

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(x=df["Response Time"], ax=ax, color="lightcoral")

    ax.set_title("📊 Response Time Distribution", fontsize=14)
    ax.set_xlabel("Response Time (Minutes)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.6)

    st.pyplot(fig)


def plot_ticket_aging(df, source_filter=None):
    if df.empty or "Ticket Aging" not in df.columns:
        st.warning("No data available for ticket aging analysis.")
        return

    # Filter data if a specific source report is selected
    if source_filter:
        df = df[df["Source"] == source_filter]

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.violinplot(x=df["Ticket Aging"], ax=ax, color="orange", inner="quartile")

    ax.set_title("Ticket Aging Distribution", fontsize=14)
    ax.set_xlabel("Ticket Age (Days)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.6)

    st.pyplot(fig)



def plot_total_requests(df):
    """Displays the total number of requests as a bordered metric card."""
    if df.empty:
        st.warning("⚠️ No data available to display total requests.")
        return
    
    total_requests = df.shape[0]  # Count total rows

    # Custom HTML & CSS for bordered card with inline-block styling
    st.markdown(f"""
        <div style="
            display: inline-block;
            width: 48%;
            border: 2px solid #4CAF50; 
            border-radius: 10px; 
            padding: 15px; 
            text-align: center; 
            background-color: #f9f9f9; 
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-right: 2%;">
            <h3 style="color: #4CAF50; margin-bottom: 5px;">Total Requests</h3>
            <h2 style="color: black;">{total_requests:,}</h2>
        </div>
    """, unsafe_allow_html=True)


import plotly.express as px
import streamlit as st
import pandas as pd

def plot_requests_by_category(df):
    """Displays a Bubble Chart showing the number of requests by Category & Sub-Category."""
    
    df.columns = df.columns.str.strip()  # Remove extra spaces from column names

    if "Category" not in df.columns or "Sub-Category" not in df.columns or df.empty:
        st.warning("⚠️ 'Category' or 'Sub-Category' column is missing.")
        return

    df = df.dropna(subset=["Category", "Sub-Category"])
    
    # Count requests per Category & Sub-Category
    category_counts = df.groupby(["Category", "Sub-Category"]).size().reset_index(name="Request Count")

    # Bubble chart visualization
    fig = px.scatter(category_counts, 
                     x="Category", 
                     y="Sub-Category", 
                     size="Request Count", 
                     color="Category",
                     hover_name="Sub-Category",
                     color_discrete_sequence=px.colors.qualitative.Pastel)

    fig.update_layout(title_text="🔵 Requests by Category & Sub-Category (Bubble Chart)", title_x=0.4)

    # Display in Streamlit
    st.plotly_chart(fig)

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import streamlit as st

def plot_sla_performance(df):
    """Stacked Column Chart: Requests Meeting SLA vs. SLA Breached with Labeled Counts Inside Bars (Black Border)"""

    if "SLA" not in df.columns or df.empty:
        st.warning("⚠️ 'SLA' column is missing or dataset is empty.")
        return

    # Count occurrences of SLA Met vs SLA Breached
    sla_counts = df["SLA"].value_counts()

    # Create bar chart
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = sla_counts.plot(kind="bar", stacked=True, color=["green", "red"], ax=ax)

    # Add data labels inside bars with black-bordered text
    for bar in bars.patches:
        height = bar.get_height()
        if height > 0:
            text = ax.text(
                bar.get_x() + bar.get_width() / 2,  # X position
                bar.get_height() / 2,  # Y position (middle of the bar)
                str(int(height)),  # Convert count to integer
                ha="center", va="center", fontsize=12, color="white", fontweight="bold"
            )
            text.set_path_effects([
                path_effects.withStroke(linewidth=3, foreground="black")  # Black border for better visibility
            ])

    # Labels and title
    ax.set_title("Requests Meeting SLA vs. SLA Breached", fontsize=14, fontweight="bold")
    ax.set_xlabel("SLA Status", fontsize=12)
    ax.set_ylabel("Number of Requests", fontsize=12)
    ax.set_xticklabels(sla_counts.index, rotation=0)  # Keep labels horizontal

    # Show plot in Streamlit
    st.pyplot(fig)




def plot_avg_closure_time(df):
    """Displays the Average Time to Close Requests as a styled metric card with centered value."""
    
    if df.empty or "Close time" not in df.columns or "Request time" not in df.columns:
        st.warning("⚠️ Required columns missing or dataset is empty.")
        return

    # Convert columns to datetime
    df["Close time"] = pd.to_datetime(df["Close time"], errors="coerce")
    df["Request time"] = pd.to_datetime(df["Request time"], errors="coerce")

    # Calculate resolution time (in days)
    df["Resolution Time"] = (df["Close time"] - df["Request time"]).dt.total_seconds() / 86400  # Convert seconds to days

    # Compute average resolution time
    avg_resolution_time = df["Resolution Time"].mean()

    # Custom HTML & CSS for a bordered card with centered value
    st.markdown(f"""
        <div style="
            border: 2px solid #2196F3; 
            border-radius: 10px; 
            padding: 15px; 
            text-align: center; 
            background-color: #f9f9f9; 
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            width: 100%; 
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;">
            <h3 style="color: #2196F3; margin-bottom: 10px;">Avg Time to Close Requests</h3>
            <h2 style="color: black; font-size: 28px; font-weight: bold; margin: 0;">{avg_resolution_time:.1f} Days</h2>
        </div>
    """, unsafe_allow_html=True)


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def plot_due_date_analysis(df):
    """Bar Chart: Requests Closed Before, On, or After the Due Date with Labeled Counts Inside Bars (Black Border)"""
    
    if "Close time" not in df.columns or "Due Date" not in df.columns or df.empty:
        st.warning("⚠️ 'Close time' or 'Due Date' column is missing.")
        return

    # Convert columns to datetime
    df["Close time"] = pd.to_datetime(df["Close time"], errors="coerce")
    df["Due Date"] = pd.to_datetime(df["Due Date"], errors="coerce")

    # Classify closure status
    df["Closure Status"] = df.apply(
        lambda row: "Before Due Date" if row["Close time"] < row["Due Date"]
        else "On Due Date" if row["Close time"] == row["Due Date"]
        else "After Due Date", axis=1
    )

    # Count occurrences
    closure_counts = df["Closure Status"].value_counts()

    # Create bar chart
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = sns.barplot(x=closure_counts.index, y=closure_counts.values, palette=["green", "blue", "red"], ax=ax)

    # Add data labels inside bars with black-bordered text
    for bar in bars.patches:
        height = bar.get_height()
        if height > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # X position
                bar.get_height() / 2,  # Y position (middle of the bar)
                str(int(height)),  # Convert count to integer
                ha="center", va="center", fontsize=12, 
                color="white", fontweight="bold", path_effects=[
                    plt.matplotlib.patheffects.withStroke(linewidth=3, foreground="black")  # Black border
                ]
            )

    # Labels and title
    ax.set_title("Requests Closed Before, On, or After the Due Date", fontsize=14, fontweight="bold")
    ax.set_xlabel("Closure Status", fontsize=12)
    ax.set_ylabel("Number of Requests", fontsize=12)
    ax.set_xticklabels(closure_counts.index, rotation=0)  # Keep labels horizontal

    # Show plot in Streamlit
    st.pyplot(fig)


def plot_request_completion_status(df):
    """Displays a donut chart for Pending vs. Completed Requests."""
    
    if "Status" not in df.columns or df.empty:
        st.warning("⚠️ 'Status' column is missing or dataset is empty.")
        return

    # Define status categories
    completed_statuses = ["Closed", "Resolved", "Completed"]
    pending_statuses = ["Open", "In Progress", "Pending"]

    # Count requests in each category
    completed_count = df[df["Status"].isin(completed_statuses)].shape[0]
    pending_count = df[df["Status"].isin(pending_statuses)].shape[0]

    # Data for the pie chart
    labels = ["Completed", "Pending"]
    sizes = [completed_count, pending_count]
    colors = ["#4CAF50", "#FFC107"]  # Green for completed, Yellow for pending

    # Create the figure with smaller size (reduced to half)
    fig, ax = plt.subplots(figsize=(3, 3))  # Shrinking the figure

    ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, 
           startangle=140, wedgeprops={"edgecolor": "black"})
    ax.set_title("Pending vs. Completed Requests", fontsize=10)  # Reduce title size

    # Add a circle at the center to make it a donut chart
    center_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig.gca().add_artist(center_circle)

    # Display the plot
    st.pyplot(fig)

def plot_requests_by_status(df):
    """Displays a stacked bar chart of Requests by Status."""
    
    if "Status" not in df.columns or "Category" not in df.columns or df.empty:
        st.warning("⚠️ 'Status' or 'Category' column is missing or dataset is empty.")
        return

    # Group by Category & Status
    status_counts = df.groupby(["Category", "Status"]).size().reset_index(name="Request Count")

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=status_counts, x="Category", y="Request Count", hue="Status", ax=ax)

    # Rotate x-axis labels if too many categories exist
    if status_counts["Category"].nunique() > 8:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

    ax.set_title("Requests by Status")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of Requests")

    st.pyplot(fig)

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np
import streamlit as st

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import streamlit as st

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects  # For text outline effect

def plot_aging_report_table(df):
    """Displays a table summarizing requests open for different aging brackets in minutes and a candlestick-style chart."""
    
    if "Ticket Aging" not in df.columns or df.empty:
        st.warning("⚠️ 'Ticket Aging' column is missing or dataset is empty.")
        return

    # Convert Ticket Aging from days to minutes (assuming 1 day = 1440 minutes)
    df["Ticket Aging (Minutes)"] = df["Ticket Aging"] * 1440

    # Define aging brackets (in minutes)
    conditions = [
        (df["Ticket Aging (Minutes)"] <= 30),
        (df["Ticket Aging (Minutes)"] > 30) & (df["Ticket Aging (Minutes)"] <= 60),
        (df["Ticket Aging (Minutes)"] > 60) & (df["Ticket Aging (Minutes)"] <= 120),
        (df["Ticket Aging (Minutes)"] > 120)
    ]
    labels = ["0-30 Minutes", "30-60 Minutes", "60-120 Minutes", "120+ Minutes"]

    df["Age Category"] = np.select(conditions, labels, default="Unknown")

    # Ensure all aging categories appear (even if they have 0 requests)
    aging_brackets = ["0-30 Minutes", "30-60 Minutes", "60-120 Minutes", "120+ Minutes"]
    aging_summary = df["Age Category"].value_counts().reindex(aging_brackets, fill_value=0).reset_index()
    aging_summary.columns = ["Aging Bracket", "Request Count"]

    # Display table
    st.subheader("📋 Aging Report (Minutes)")
    st.table(aging_summary)

    # Prepare Candlestick Chart Data (OHLC Format)
    aging_summary["Open"] = aging_summary["Request Count"].shift(1, fill_value=aging_summary["Request Count"].iloc[0])
    aging_summary["High"] = aging_summary["Request Count"]
    aging_summary["Low"] = aging_summary["Request Count"].rolling(2).min().fillna(aging_summary["Request Count"])
    aging_summary["Close"] = aging_summary["Request Count"]

    # Plot Custom Candlestick Chart using Matplotlib
    fig, ax = plt.subplots(figsize=(6, 4))

    for i, row in aging_summary.iterrows():
        x = i  # X-axis index (0,1,2,3 for categories)
        open_ = row["Open"]
        high = row["High"]
        low = row["Low"]
        close = row["Close"]

        # Draw candlestick wick (vertical line)
        ax.vlines(x, low, high, color="black", linewidth=2)

        # Determine candle color (green if Close > Open, red otherwise)
        color = "green" if close >= open_ else "red"

        # Draw candlestick body (rectangle)
        body = patches.Rectangle(
            (x - 0.2, min(open_, close)),  # X position & bottom Y
            0.4,  # Width
            abs(close - open_),  # Height (absolute difference)
            color=color,
            alpha=0.8
        )
        ax.add_patch(body)

        # Add text inside the candle with a black border
        text = ax.text(
            x, (open_ + close) / 2, str(int(row["Request Count"])), 
            ha="center", va="center", fontsize=12, color="white", fontweight="bold"
        )

        # Apply black outline effect to text
        text.set_path_effects([
            path_effects.Stroke(linewidth=2, foreground="black"),  # Black border
            path_effects.Normal()  # Normal text rendering
        ])

    # Set labels
    ax.set_xticks(range(len(aging_brackets)))
    ax.set_xticklabels(aging_brackets, rotation=0)
    ax.set_ylabel("Number of Requests", fontsize=12)
    ax.set_title("Request Aging Distribution (Minutes)", fontsize=14, fontweight="bold")

    # Display in Streamlit
    st.pyplot(fig)


def plot_requests_by_priority(df):
    """Bar Chart: Requests by Priority (High, Medium, Low) with numbers inside bars."""
    
    if "Priority" not in df.columns or df.empty:
        st.warning("⚠️ 'Priority' column is missing or dataset is empty.")
        return

    # Count requests by priority
    priority_counts = df["Priority"].value_counts()

    # Plot bar chart
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = sns.barplot(x=priority_counts.index, y=priority_counts.values, palette=["red", "orange", "green"], ax=ax)

    # Add numbers inside bars
    for bar in bars.patches:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # X position
            height / 2,  # Y position (middle of the bar)
            str(int(height)),  # Convert count to integer
            ha="center", va="center", fontsize=12, color="black", fontweight="bold",
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3")
        )

    ax.set_title("Requests by Priority", fontsize=14, fontweight="bold")
    ax.set_xlabel("Priority", fontsize=12)
    ax.set_ylabel("Number of Requests", fontsize=12)

    st.pyplot(fig)

def plot_urgent_requests(df):
    """Pie Chart: Urgent vs. Non-Urgent Requests"""
    
    if "Urgency" not in df.columns or df.empty:
        st.warning("⚠️ 'Urgency' column is missing or dataset is empty.")
        return

    # Count urgent vs. non-urgent requests
    urgency_counts = df["Urgency"].value_counts()

    # Plot pie chart
    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(
        urgency_counts.values, labels=urgency_counts.index, autopct="%1.1f%%",
        colors=["red", "gray"], startangle=90, textprops={"fontsize": 12, "fontweight": "bold"}
    )

    # Add black border to text
    for text in autotexts:
        text.set_bbox(dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))

    ax.set_title("Urgent Requests Breakdown", fontsize=14, fontweight="bold")
    
    st.pyplot(fig)

def plot_priority_vs_resolution_time(df):
    """Line Chart: Average Resolution Time by Priority"""

    if "Priority" not in df.columns or "Response Time" not in df.columns or df.empty:
        st.warning("⚠️ Required columns ('Priority', 'Response Time') are missing or dataset is empty.")
        return

    # Compute average response time for each priority
    avg_resolution_time = df.groupby("Priority")["Response Time"].mean().sort_index()

    # Plot line chart
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(avg_resolution_time.index, avg_resolution_time.values, marker="o", linestyle="-", color="blue")

    # Add data labels
    for i, value in enumerate(avg_resolution_time.values):
        ax.text(i, value, f"{int(value)} min", ha="center", va="bottom", fontsize=12,
                bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))

    ax.set_title("Impact of Priority on Resolution Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("Priority", fontsize=12)
    ax.set_ylabel("Avg. Resolution Time (minutes)", fontsize=12)

    st.pyplot(fig)

def plot_requests_by_process_manager(df):
    """Column Chart: Number of Requests Handled by Each Process Manager"""
    
    if "Process manager" not in df.columns or df.empty:
        st.warning("⚠️ 'Process manager' column is missing or dataset is empty.")
        return
    
    manager_counts = df["Process manager"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(manager_counts.index, manager_counts.values, color="royalblue")

    # Add data labels with black borders
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height, str(int(height)), 
                ha='center', va='bottom', fontsize=12, color='black', 
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    ax.set_title("Requests Handled by Each Process Manager", fontsize=14, fontweight="bold")
    ax.set_xlabel("Process Manager", fontsize=12)
    ax.set_ylabel("Number of Requests", fontsize=12)
    ax.set_xticklabels(manager_counts.index, rotation=45, ha="right")

    st.pyplot(fig)
    
def plot_request_volume_trend(df):
    if "Request time" not in df.columns or df.empty:
        st.warning("⚠️ 'Request time' column is missing or dataset is empty.")
        return

    df["Request time"] = pd.to_datetime(df["Request time"], errors="coerce")

    # Aggregate data by month
    request_trend = df["Request time"].dt.to_period("M").value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    request_trend.plot(kind="line", marker="o", color="blue", ax=ax)
    ax.set_title("📈 Request Volume Trend Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Requests")
    ax.grid(True)
    
    st.pyplot(fig)

def plot_peak_request_times(df):
    """Plots a bar chart showing peak request times (most active days/months)."""
    if "Request time" not in df.columns or df.empty:
        st.warning("⚠️ 'Request time' column is missing or dataset is empty.")
        return

    df["Request time"] = pd.to_datetime(df["Request time"], errors="coerce")

    # Group by month and get the highest request counts
    peak_times = df["Request time"].dt.strftime("%B").value_counts()

    fig, ax = plt.subplots(figsize=(10, 5))
    peak_times.sort_values(ascending=True).plot(kind="barh", color="orange", ax=ax)
    ax.set_title("📊 Peak Request Times (Most Active Months)")
    ax.set_xlabel("Number of Requests")
    ax.set_ylabel("Month")
    
    st.pyplot(fig)

def plot_most_common_request_categories(df):
    """Plots a pie chart showing the most common request categories and subcategories."""
    if "Category" not in df.columns or "Sub-Category" not in df.columns or df.empty:
        st.warning("⚠️ 'Category' or 'Sub-Category' column is missing or dataset is empty.")
        return

    category_counts = df["Category"].value_counts().head(5)  # Top 5 categories
    subcategory_counts = df["Sub-Category"].value_counts().head(5)  # Top 5 subcategories

    fig, ax = plt.subplots(figsize=(6, 6))
    category_counts.plot(kind="pie", autopct="%1.1f%%", colors=plt.cm.Paired.colors, ax=ax)
    ax.set_title("📊 Most Common Request Categories")
    ax.set_ylabel("")  # Hide y-axis label
    
    st.pyplot(fig)

def plot_recurring_issues(df, top_n=10):
    """Plots a heatmap showing the most common recurring issues based on Title and Category."""
    if "Category" not in df.columns or "Title" not in df.columns or df.empty:
        st.warning("⚠️ 'Category' or 'Title' column is missing or dataset is empty.")
        return

    # Count occurrences of each (Category, Title) pair
    issue_counts = df.groupby(["Category", "Title"]).size().reset_index(name="Count")

    # Select top N most frequent issues
    top_issues = issue_counts.nlargest(top_n, "Count")

    # Pivot for heatmap format
    heatmap_data = top_issues.pivot(index="Category", columns="Title", values="Count").fillna(0)

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(heatmap_data, annot=True, fmt="g", cmap="Blues", linewidths=0.5, ax=ax)

    ax.set_title("🔥 Top Recurring Issues (Category vs. Title)")
    ax.set_xlabel("Issue Title")
    ax.set_ylabel("Category")

    st.pyplot(fig)



def plot_time_taken_box_plot(df):
    """Displays a Box Plot for Process Managers and their time taken."""
    
    df.columns = df.columns.str.strip()  

    if "Process manager" not in df.columns or "Request time" not in df.columns or "Close time" not in df.columns or df.empty:
        st.warning("⚠️ 'Process manager', 'Request time', or 'Close time' column is missing.")
        return

    df = df.dropna(subset=["Process manager", "Request time", "Close time"])

    df["Request time"] = pd.to_datetime(df["Request time"], errors="coerce")
    df["Close time"] = pd.to_datetime(df["Close time"], errors="coerce")

    df["Time Taken (Minutes)"] = (df["Close time"] - df["Request time"]).dt.total_seconds() / 60
    df = df[df["Time Taken (Minutes)"] >= 0].dropna(subset=["Time Taken (Minutes)"])

    # Box Plot
    fig = px.box(df, 
                 x="Process manager", 
                 y="Time Taken (Minutes)", 
                 color="Process manager", 
                 points="all", 
                 color_discrete_sequence=px.colors.qualitative.Pastel)

    fig.update_layout(title_text="📊 Time Taken Distribution by Process Manager (Box Plot)", title_x=0.4,
                      xaxis_title="Process Manager", yaxis_title="Time Taken (Minutes)")

    st.plotly_chart(fig)

import pandas as pd
import streamlit as st

# ✅ Detect Reopened Requests
def detect_reopened_requests(df):
    """Identify reopened requests based on duplicate (Request user, Category, Sub-Category, Title)."""
    required_columns = {"Request user", "Category", "Sub-Category", "Title"}

    # Ensure all required columns exist
    if not required_columns.issubset(df.columns):
        st.error(f"🚨 Missing columns: {required_columns - set(df.columns)}")
        return df

    # ✅ Identify duplicates that indicate a reopened request
    df["Reopened"] = df.duplicated(subset=["Request user", "Category", "Sub-Category", "Title"], keep=False)
    
    return df

# File: src/itautomationreports/visualization.py
# File: src/itautomationreports/visualization.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_user_request_analysis(df):
    """Visualize the top 10 users with the most requests and their average resolution time."""
    
    if "Request user" not in df.columns or "Close time" not in df.columns or "Request time" not in df.columns:
        st.warning("⚠️ Required columns ('Request user', 'Request time', 'Close time') are missing.")
        return
    
    # Convert to datetime
    df["Request time"] = pd.to_datetime(df["Request time"], errors="coerce")
    df["Close time"] = pd.to_datetime(df["Close time"], errors="coerce")

    # Calculate Resolution Time (in hours)
    df["Resolution Time"] = (df["Close time"] - df["Request time"]).dt.total_seconds() / 3600

    # Group by user
    user_stats = df.groupby("Request user").agg(
        Total_Requests=("Request user", "count"),
        Avg_Resolution_Time=("Resolution Time", "mean")
    ).reset_index()

    # Sort by total requests & select top 10 users
    top_users = user_stats.sort_values(by="Total_Requests", ascending=False).head(10)

    # ✅ Visualization
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Bar chart for Total Requests (Primary Y-Axis)
    sns.barplot(x="Request user", y="Total_Requests", data=top_users, palette="Blues_r", ax=ax1)
    ax1.set_xlabel("User")
    ax1.set_ylabel("Total Requests", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")

    # Scatter plot for Avg Resolution Time (Secondary Y-Axis, Dots Only)
    ax2 = ax1.twinx()
    ax2.scatter(top_users["Request user"], top_users["Avg_Resolution_Time"], color="red", label="Avg Resolution Time")
    ax2.set_ylabel("Avg Resolution Time (hrs)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # Display Plot
    st.pyplot(fig)




