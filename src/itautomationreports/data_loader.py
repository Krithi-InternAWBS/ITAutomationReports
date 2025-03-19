import pandas as pd
import numpy as np
from datetime import datetime

def find_header_row(df):
    """Finds the row number that contains '#' or 'Ticket' to set as the header."""
    for i, row in df.iterrows():
        if any(row.astype(str).str.contains(r"^(#|Ticket)$", na=False, case=False, regex=True)):
            return i  # Return the row index where the header is found
    return None

def load_data(uploaded_files):
    """
    Loads and processes multiple Excel files, ensuring:
    - The correct sheet ("Data" or "Report") is used.
    - The correct header row is identified dynamically.
    - Additional derived columns ("Response Time", "Ticket Aging") are calculated.
    """
    all_data = []
    file_names = []

    for file in uploaded_files:
        print(f"\n📂 Loading file: {file.name}")

        try:
            # Open the Excel file and check for available sheets
            xl = pd.ExcelFile(file)
            available_sheets = xl.sheet_names

            # Try loading "Data" or "Report" sheet (whichever is found first)
            sheet_name = next((s for s in ["Data", "Report"] if s in available_sheets), None)
            if not sheet_name:
                print(f"🚨 No 'Data' or 'Report' sheet found in {file.name}! Available sheets: {available_sheets}")
                continue  # Skip this file

            df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
            print(f"✅ Loaded sheet: {sheet_name}")

        except Exception as e:
            print(f"🚨 Error loading {file.name}: {e}")
            continue  # Skip this file if an error occurs

        print("📊 First 10 rows before processing:\n", df.head(10))  # Debugging output

        # Identify the row where "#" or "Ticket" is present as the header row
        header_row = find_header_row(df)
        if header_row is not None:
            print(f"✅ Using row {header_row} as header in {file.name}.")
            df.columns = df.iloc[header_row]  # Set the correct header
            df = df.iloc[header_row + 1:].reset_index(drop=True)  # Remove extra rows
        else:
            print(f"🚨 No '#' or 'Ticket' found in {file.name}! Skipping file.")
            continue  # Skip file if no header found

        # Normalize column names (strip spaces and replace multiple spaces)
        df.columns = df.columns.astype(str).str.strip().str.replace(r"\s+", " ", regex=True)

        # Debugging: Verify cleaned column names
        print(f"📂 Available columns AFTER cleaning: {list(df.columns)}")

        # Add a "Source" column to track file origin
        df["Source"] = file.name  

        # Store processed data
        all_data.append(df)
        file_names.append(file.name)

    if not all_data:
        print("🚨 No valid data loaded!")
        return None, file_names  # Return None if no files processed

    combined_df = pd.concat(all_data, ignore_index=True)

    # Pass the combined data to cleaning function
    cleaned_df = clean_data(combined_df)

    return cleaned_df, file_names


import pandas as pd
import numpy as np

def clean_data(df):
    """
    Cleans and processes the dataset by:
    - Standardizing column names
    - Fixing 'SLA' column values
    - Renaming columns based on known variations
    - Converting date columns to datetime format
    - Calculating "Response Time" and "Ticket Aging" (corrected)
    - Dropping completely empty rows
    """

    # Standardize column names (strip spaces and normalize)
    df.columns = df.columns.astype(str).str.strip()

    # Debugging: Print available columns before renaming
    print("📂 Available columns BEFORE renaming:", df.columns)

    # Expected column name mappings (normalize variations)
    column_mapping = {
        "Request time": ["Request time", "Request Date", "Created Time", "Timestamp"],
        "Ticket": ["#", "Ticket", "Request ID", "Incident ID", "Case Number"],  
        "SLA": ["SLA", "SLA Compliance", "Met SLA"],  
        "Close time": ["Close time", "Resolved Time", "Completion Date"],
        "Due Date": ["Due Date", "SLA Due Date", "Deadline"],
        "Category": ["Category", "Request Category"],
        "Sub-Category": ["Sub-Category", "Request Sub-Category"],
        "Process Manager": ["Process Manager", "Assigned Manager"]
    }

    # Rename columns to standard format
    new_columns = {}
    for standard_name, variations in column_mapping.items():
        for variant in variations:
            if variant in df.columns:
                new_columns[variant] = standard_name
    df.rename(columns=new_columns, inplace=True)

    # Debugging: Show final column names after renaming
    print("✅ Available columns AFTER renaming:", list(df.columns))

    # Convert date columns
    date_columns = ["Request time", "Close time", "Due Date"]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # ✅ Fix SLA column reference
    if "SLA" in df.columns:
        df["SLA"] = df["SLA"].astype(str).str.extract(r"(Met|Fail)", expand=False)  # Extract only 'Met' or 'Fail'
        print(f"📊 Unique Values in 'SLA': {df['SLA'].unique()}")  # Debugging output
        df["SLA Met Count"] = (df["SLA"].str.strip() == "Met").sum()  # Count occurrences of "Met"
    else:
        print("🚨 Warning: 'SLA' column not found in dataset!")

    # ✅ Add "Response Time" (Only if both 'Request time' & 'Close time' exist)
    if "Request time" in df.columns and "Close time" in df.columns:
        df["Response Time"] = (df["Close time"] - df["Request time"]).dt.total_seconds() / 60  # Convert to minutes
        df["Response Time"] = df["Response Time"].fillna(0)  # Replace NaN with 0
        print("✅ 'Response Time' calculated successfully.")
    else:
        print("🚨 'Response Time' column could not be calculated. Required columns missing!")

    # ✅ Correct "Ticket Aging" Calculation  
    if "Request time" in df.columns:
        df["Ticket Aging"] = (df["Close time"] - df["Request time"]).dt.days

        # If ticket is still open, calculate aging based on today’s date
        df.loc[df["Close time"].isna(), "Ticket Aging"] = (pd.to_datetime("today") - df["Request time"]).dt.days

        df["Ticket Aging"] = df["Ticket Aging"].fillna(0).astype(int)  # Replace NaN with 0
        print("✅ 'Ticket Aging' calculated successfully.")

        # ✅ Assign Aging Brackets
        conditions = [
            (df["Ticket Aging"] > 90),
            (df["Ticket Aging"] > 60) & (df["Ticket Aging"] <= 90),
            (df["Ticket Aging"] > 30) & (df["Ticket Aging"] <= 60),
            (df["Ticket Aging"] <= 30)
        ]
        labels = ["90+ Days", "60-90 Days", "30-60 Days", "0-30 Days"]
        df["Aging Bracket"] = np.select(conditions, labels, default="Unknown")

    else:
        print("🚨 'Ticket Aging' column could not be calculated. Required column missing!")

    # Drop completely empty rows
    df.dropna(how="all", inplace=True)

    # Debugging: Final check of available columns
    print("📊 Final Processed Columns (After Adding Derived Columns):", list(df.columns))

    return df
