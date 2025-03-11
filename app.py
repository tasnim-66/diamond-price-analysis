import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import random
import gspread
from google.oauth2.service_account import Credentials
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="Diamond Price Analysis", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1_thakBki8I4SlzIHPM_pDm4jV0ZtLWL323-9GMl3J-w"

try:
    credentials_dict = dict(st.secrets["google_service_account"])
    credentials = Credentials.from_service_account_info(credentials_dict)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_url(SHEET_URL)
    sheet = spreadsheet.sheet1
    data = sheet.get_all_records()

    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()
    df = df.dropna()

    categorical_cols = ['cut', 'color', 'clarity']
    label_encoders = {}

    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

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

    st.title("Diamond Price Analysis: A/B Testing")

    st.write("### Preview of the Diamonds Dataset:")
    st.dataframe(df.head())

    st.write("## What Factor Influences Diamond Price the Most?")

    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "selected_chart" not in st.session_state:
        st.session_state.selected_chart = None
    if "show_answer_button" not in st.session_state:
        st.session_state.show_answer_button = False
    if "show_conclusion" not in st.session_state:
        st.session_state.show_conclusion = False

    def pick_random_chart():
        st.session_state.selected_chart = random.choice(["Correlation Heatmap", "Factor Importance Bar Chart"])
        st.session_state.start_time = time.time()
        st.session_state.show_answer_button = True
        st.session_state.show_conclusion = False

    if st.button("Show me a random visualization"):
        pick_random_chart()

    if st.session_state.selected_chart:
        st.write(f"### {st.session_state.selected_chart}")

        if st.session_state.selected_chart == "Correlation Heatmap":
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
            correlation_values.index = [factor_labels.get(col, col) for col in correlation_values.index]

            plt.figure(figsize=(8, 5))
            sns.barplot(x=correlation_values.values, y=correlation_values.index, palette="Blues_r")
            plt.xlabel("Correlation with Price")
            plt.ylabel("Factors")
            plt.title("Which Factor Influences Price the Most?")
            st.pyplot(plt)

    if st.session_state.show_answer_button:
        if st.button("I have the answer"):
            time_taken = time.time() - st.session_state.start_time
            st.session_state.show_conclusion = True
            st.write(f"You took **{time_taken:.2f} seconds** to answer the question.")

    if st.session_state.show_conclusion:
        st.write("## Conclusion:")
        st.write("""
        - **Bar Chart:**  
          The most important factor influencing diamond price is **carat size**. Larger diamonds have significantly higher prices.
          
        - **Correlation Heatmap:**  
          The strongest correlation with price is seen with **carat size**, followed by dimensions (length, width, depth). Other factors like clarity, cut, and color have lower correlations.
        """)

except KeyError:
    st.error("Secrets Not Configured: Please add your Google Sheets credentials to Streamlit Secrets.")
    st.write("Fix: Go to Streamlit Cloud → Manage App → Settings → Secrets and add your Google Service Account details.")

except PermissionError:
    st.error("Permission Denied: The service account does not have access to this Google Sheet.")
    st.write("Fix: Ensure the service account email is added as an Editor in the Google Sheets sharing settings.")

except Exception as e:
    st.error(f"An error occurred: {e}")

