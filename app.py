import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sklearn.preprocessing import LabelEncoder

# Set Streamlit page config 
st.set_page_config(page_title="Diamond Price Analysis", layout="wide")

# ✅ Google Sheets API Setup
SHEET_URL = "https://docs.google.com/spreadsheets/d/1_thakBki8I4SlzIHPM_pDm4jV0ZtLWL323-9GMl3J-w"

# ✅ Define the scope and credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

# ✅ Authenticate with Google Sheets
client = gspread.authorize(credentials)

try:
    # ✅ Open Google Sheet and get data
    spreadsheet = client.open_by_url(SHEET_URL)
    sheet = spreadsheet.sheet1
    data = sheet.get_all_records()

    # ✅ Convert to DataFrame
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()

    # ✅ Drop any rows with missing values to prevent errors
    df = df.dropna()

    # ✅ Convert categorical columns into numerical values
    categorical_cols = ['cut', 'color', 'clarity']
    label_encoders = {}

    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

    # ✅ Define label mappings for better readability
    factor_labels = {
        "carat": "Carat",
        "x": "Length (mm)",
        "y": "Width (mm)",
        "z": "Depth (mm)",
        "color": "Color",
        "table": "Table",
        "cut": "Cut",
        "depth": "Total Depth",
        "clarity": "Clarity"
    }

    # ✅ Streamlit UI
    st.title("Diamond Price Analysis: A/B Testing")

    # ✅ Display dataset preview
    st.write("### Preview of the Diamonds Dataset:")
    st.dataframe(df.head())

    # ✅ Visualization Selection
    st.write("## What Factor Influences Diamond Price the Most?")

    # ✅ Store session state for interaction
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "selected_chart" not in st.session_state:
        st.session_state.selected_chart = None
    if "show_answer_button" not in st.session_state:
        st.session_state.show_answer_button = False
    if "show_conclusion" not in st.session_state:
        st.session_state.show_conclusion = False

    # ✅ Function to randomly pick a chart
    def pick_random_chart():
        st.session_state.selected_chart = random.choice(["Correlation Heatmap", "Factor Importance Bar Chart"])
        st.session_state.start_time = time.time()
        st.session_state.show_answer_button = True
        st.session_state.show_conclusion = False  # Reset conclusion visibility

    # ✅ Button to display a random chart
    if st.button("Show me a random visualization"):
        pick_random_chart()

    # ✅ Display the randomly selected chart
    if st.session_state.selected_chart:
        st.write(f"### {st.session_state.selected_chart}")

        if st.session_state.selected_chart == "Correlation Heatmap":
            # The correlation with price
            price_corr = df.corr()["price"].drop("price").sort_values(ascending=False)

            plt.figure(figsize=(8, 5))
            heatmap_data = price_corr.to_frame().rename(columns={"price": "Correlation"})
            sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
            plt.title("Correlation of Factors with Price")
            plt.xlabel("")
            plt.ylabel("Factors")
            st.pyplot(plt)

        elif st.session_state.selected_chart == "Factor Importance Bar Chart":
            correlation_values = df.corr()["price"].drop("price").sort_values(ascending=False)

            # Rename factors using the dictionary above
            correlation_values.index = [factor_labels.get(col, col) for col in correlation_values.index]

            plt.figure(figsize=(8, 5))
            sns.barplot(x=correlation_values.values, y=correlation_values.index, palette="Blues_r")
            plt.xlabel("Correlation with Price")
            plt.ylabel("Factors")
            plt.title("Which Factor Influences Price the Most?")
            st.pyplot(plt)

    # ✅ Button to confirm that the user answered the question
    if st.session_state.show_answer_button:
        if st.button("I have the answer"):
            time_taken = time.time() - st.session_state.start_time
            st.session_state.show_conclusion = True  # Show conclusion 
            st.write(f"You took **{time_taken:.2f} seconds** to answer the question.")

    # ✅ Conclusion Section (Only Appears After Clicking "I have the answer")
    if st.session_state.show_conclusion:
        st.write("## Conclusion:")
        st.write("""
        - **Bar Chart:**  
          The most important factor influencing diamond price is **carat size**. Larger diamonds have significantly higher prices.
          
        - **Correlation Heatmap:**  
          The strongest correlation with price is seen with **carat size**, followed by dimensions (length, width, depth). Other factors like clarity, cut, and color have lower correlations.
        """)

except PermissionError:
    st.error("🚨 **Permission Denied:** The service account does not have access to this Google Sheet.")
    st.write("🔹 **Fix:** Ensure the service account email is added as an **Editor** in the Google Sheets sharing settings.")

except Exception as e:
    st.error(f"⚠️ An error occurred: {e}")
