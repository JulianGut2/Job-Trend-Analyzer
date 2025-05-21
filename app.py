# Streamlit imports
import streamlit as st
import pandas as pd
from PIL import Image


# Load the data
df = pd.read_csv("data/clean_remoteok_jobs.csv")

# Let us set up the app

st.set_page_config(page_title = "Job Trends Analyzer", layout = "wide")
st.title("Job Trends Analyzer Using RemoteOK")
st.markdown("""
            This Streamlit app analyzes **real remote job listings** pulled directly from RemoteOK.
            It highlights skill demand, top hiring companies, and job trends over a period of time.
            """)

# Next let users be able to preview the dataset

with st.expander("Click to preview raw job data"):
    st.dataframe(df.head(10))

# Now lets add a section for charts 

st.header("Insights & Visualizations")

# Load and display the images

st.subheader("Top In-Demand Skills")
st.image("visuals/top_skills.png", use_column_width = True, caption = "The top 5 most in demand skills are: support, software, management, growth, digital nomad")

st.subheader("Top Hiring Companies")
st.image("visuals/top_companies.png", use_column_width = True, caption = "Contra and Anchorage Digital lead remote hiring")

st.subheader("Job Postings Over Time")
st.image("visuals/postings_over_time.png", use_column_width = True, caption = "Job postings spiked around May 6th, 2025.")

# Credit myself with a footer!
st.markdown("---")
st.markdown("Created by **Julian Gutierrez** | Built with `Python`, `Pandas`, and `Streamlit`")


