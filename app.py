# 🏢 Enterprise Multi-Resume HR RAG System (Final Stable Version)

import streamlit as st
import pandas as pd
from openai import OpenAI

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Enterprise HR AI System", layout="wide")
st.title("🏢 Enterprise Multi-Resume HR RAG System")

# -----------------------------
# API KEY
# -----------------------------
import os

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("🚨 OpenRouter API key not found in environment variables.")
    st.stop()

client = OpenAI(
api_key=api_key,
base_url="https://openrouter.ai/api/v1"
)

# -----------------------------
# LOAD EXCEL DATASET
# -----------------------------
excel_file = st.file_uploader("Upload Candidate Dataset (Excel)", type="xlsx")

if excel_file:

    df = pd.read_excel(excel_file)

    st.subheader("📊 Full Candidate Dataset")
    st.dataframe(df)

    # -----------------------------
    # STRUCTURED FILTERING
    # -----------------------------
    st.subheader("🔎 Structured Filtering")

    dept = st.multiselect("Department", df["Department"].unique())
    degree = st.multiselect("Degree (UG/PG)", df["Degree"].unique())
    min_exp = st.slider("Minimum Experience (Years)", 0, 20, 0)
    max_age = st.slider("Maximum Age", 18, 60, 60)

    filtered_df = df.copy()

    if dept:
        filtered_df = filtered_df[filtered_df["Department"].isin(dept)]

    if degree:
        filtered_df = filtered_df[filtered_df["Degree"].isin(degree)]

    filtered_df = filtered_df[
        (filtered_df["Experience"] >= min_exp) &
        (filtered_df["Age"] <= max_age)
    ]

    st.write("### 🎯 Filtered Candidates")
    st.dataframe(filtered_df)

    # -----------------------------
    # ENTERPRISE MULTI-RESUME RAG
    # -----------------------------
    # -----------------------------
# ENTERPRISE HR QUERY SYSTEM (Fixed Version)
# -----------------------------
import re

st.subheader("🤖 Ask Enterprise HR Question")

if filtered_df.empty:
    st.warning("No candidates match selected filters.")

else:

    query = st.text_input(
        "Ask HR Question (e.g., age 22, below 25, how many candidates?)"
    )

    if st.button("Analyze"):

        if not query.strip():
            st.warning("Please enter a question.")

        else:

            query_lower = query.lower()

            # -----------------------------
            # 🔹 STRUCTURED QUERY HANDLER
            # -----------------------------

            age_exact = re.search(r'\bage\s*(\d+)', query_lower)
            age_below = re.search(r'below\s*(\d+)', query_lower)
            age_above = re.search(r'above\s*(\d+)', query_lower)

            result_df = filtered_df.copy()

            if age_exact:
                age_value = int(age_exact.group(1))
                result_df = result_df[result_df["Age"] == age_value]

            elif age_below:
                age_value = int(age_below.group(1))
                result_df = result_df[result_df["Age"] < age_value]

            elif age_above:
                age_value = int(age_above.group(1))
                result_df = result_df[result_df["Age"] > age_value]

            # -----------------------------
            # 🔹 COUNT QUERY
            # -----------------------------
            if "how many" in query_lower:
                st.success(f"Total Candidates: {len(result_df)}")
                st.dataframe(result_df)

            # -----------------------------
            # 🔹 IF STRUCTURED FILTER APPLIED
            # -----------------------------
            elif age_exact or age_below or age_above:

                if result_df.empty:
                    st.warning("No candidates found.")
                else:
                    st.success(f"{len(result_df)} candidates found")
                    st.dataframe(result_df)

                    # Convert to structured text for LLM summary
                    structured_text = ""
                    for _, row in result_df.iterrows():
                        structured_text += f"""
Name: {row['Name']}
Department: {row['Department']}
Age: {row['Age']}
Experience: {row['Experience']} years
Degree: {row['Degree']}
Skills: {row['Skills']}
-----------------------
"""

                    prompt = f"""
You are an enterprise HR analytics AI system.

Use ONLY the data provided below.
Do NOT invent new candidates.
Do NOT modify values.

Candidate Data:
{structured_text}

Provide professional HR insights strictly based on this dataset.
"""

                    response = client.chat.completions.create(
                        model="z-ai/glm-4.5-air:free",
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )

                    st.markdown("### 📊 HR AI Response")
                    st.info(response.choices[0].message.content)

            # -----------------------------
            # 🔹 GENERAL HR QUESTION (Use LLM)
            # -----------------------------
            else:

                # Convert entire filtered_df into context
                structured_text = ""
                for _, row in filtered_df.iterrows():
                    structured_text += f"""
Name: {row['Name']}
Department: {row['Department']}
Age: {row['Age']}
Experience: {row['Experience']} years
Degree: {row['Degree']}
Skills: {row['Skills']}
-----------------------
"""

                prompt = f"""
You are an enterprise HR analytics AI system.

Use ONLY the following filtered candidate dataset.
Do NOT invent information.

Dataset:
{structured_text}

Question:
{query}

Answer professionally.
"""

                response = client.chat.completions.create(
                    model="z-ai/glm-4.5-air:free",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                st.markdown("### 📊 HR AI Response")
                st.info(response.choices[0].message.content)