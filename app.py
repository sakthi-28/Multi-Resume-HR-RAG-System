# 🏢 Enterprise Multi-Resume HR RAG System (Optimized Production Version)

import streamlit as st
import pandas as pd
import os
import re
from openai import OpenAI

st.set_page_config(page_title="Enterprise HR AI System", layout="wide")
st.title("🏢 Enterprise Multi-Resume HR RAG System")

# -----------------------------
# CACHE HEAVY RESOURCES
# -----------------------------
@st.cache_resource
def load_openai_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

client = load_openai_client()

if client is None:
    st.error("🚨 OpenRouter API key not found.")
    st.stop()

# -----------------------------
# FILE UPLOAD
# -----------------------------
excel_file = st.file_uploader("Upload Candidate Dataset (Excel)", type="xlsx")

if excel_file:

    df = pd.read_excel(excel_file)

    st.subheader("📊 Full Candidate Dataset")
    st.dataframe(df)

    # -----------------------------
    # FILTERING
    # -----------------------------
    st.subheader("🔎 Structured Filtering")

    dept = st.multiselect("Department", df["Department"].unique())
    degree = st.multiselect("Degree", df["Degree"].unique())
    min_exp = st.slider("Minimum Experience", 0, 20, 0)
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
    # HR QUESTION SYSTEM
    # -----------------------------
    st.subheader("🤖 Ask Enterprise HR Question")

    if not filtered_df.empty:

        query = st.text_input("Ask HR Question")

        if st.button("Analyze"):

            if not query.strip():
                st.warning("Please enter a question.")

            else:

                query_lower = query.lower()
                result_df = filtered_df.copy()

                # AGE HANDLING
                age_exact = re.search(r'\bage\s*(\d+)', query_lower)
                age_below = re.search(r'below\s*(\d+)', query_lower)
                age_above = re.search(r'above\s*(\d+)', query_lower)

                if age_exact:
                    result_df = result_df[result_df["Age"] == int(age_exact.group(1))]

                elif age_below:
                    result_df = result_df[result_df["Age"] < int(age_below.group(1))]

                elif age_above:
                    result_df = result_df[result_df["Age"] > int(age_above.group(1))]

                if result_df.empty:
                    st.warning("No candidates found.")
                else:

                    st.success(f"{len(result_df)} candidates found")
                    st.dataframe(result_df)

                    # 🔥 FULL RESUME DETAILS
                    structured_text = ""
                    for _, row in result_df.iterrows():
                        structured_text += "\n".join(
                            [f"{col}: {row[col]}" for col in result_df.columns]
                        )
                        structured_text += "\n----------------------\n"

                    prompt = f"""
You are an enterprise HR analytics AI.

Use ONLY the candidate dataset below.
Do NOT invent new data.

Dataset:
{structured_text}

Question:
{query}

Provide:
1. Detailed candidate analysis
2. Strength summary
3. Hiring recommendation
4. Professional HR insights
"""

                    response = client.chat.completions.create(
                        model="z-ai/glm-4.5-air:free",
                        messages=[{"role": "user", "content": prompt}]
                    )

                    st.markdown("### 📊 HR AI Response")
                    st.info(response.choices[0].message.content)

    else:
        st.warning("No candidates match selected filters.")

else:
    st.info("📂 Please upload an Excel dataset to begin.")

    st.markdown("""
<style>
.footer {
    position: fixed;
    bottom: 12px;
    right: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 500;
    color: white;
    text-shadow: 0 0 10px #4fc3f7, 0 0 20px #4fc3f7;
    z-index: 1000;
}

.footer img {
    filter: drop-shadow(0 0 6px #4fc3f7);
    transition: transform 0.2s ease-in-out;
}

.footer img:hover {
    transform: scale(1.15);
}
</style>

<div class="footer">
    Powered by Shakthi
    <a href="https://github.com/sakthi-28" target="_blank">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" 
        width="18" height="18"/>
    </a>
</div>
""", unsafe_allow_html=True)