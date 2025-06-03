# General imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter

# Load and prepare our data
df = pd.read_csv("data/clean_remoteok_jobs.csv")
df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
df["tags"] = df["tags"].apply(lambda x: eval(x) if isinstance(x, str) else x) # We need to convert the tags into a real list

# Set up the Streamlit page
st.set_page_config(page_title = "Job Trends Analyzer", layout = "wide")
st.title("Job Trends Analyzer Using RemoteOK")

st.markdown("""
            Use the filters below to explore job trends in the remote tech market.
            """)
# Adds a date selection slider to filter through results, better for error management as the tuple will always return
# a clean tuple.

min_date = df['date'].min().date()
max_date = df['date'].max().date()

start_date, end_date = st.slider(
    "Select Date Range",
    min_value = min_date,
    max_value = max_date,
    value = (min_date, max_date),
    format = "YYYY-MM-DD"
)

df_filtered = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

# Group the date based on jobs posted on that date
jobs_per_day = df_filtered.groupby(df_filtered["date"].dt.date).size()

# Create our graph and returns no job postings if the date range is empty
if not jobs_per_day.empty:
    st.line_chart(jobs_per_day)

else:
    st.warning("No job postings in the selected date range.")

# Remove all the duplicates tags and list em!

all_tags = sorted(set(tag for tag_list in df["tags"] for tag in tag_list if isinstance(tag_list, list)))

df_exploded = df_filtered.explode("tags")

tab1, tab2, tab3, tab4 = st.tabs(["Skill Trends", "Company Insights", "Raw Listings", "Job Title Trends"])

# Creates our first tab to be able to compare in demand skills
with tab1:

    selected_skills = st.multiselect("Compare Skill Trends", all_tags)

    st.subheader("Skill Trends Comparison")

    if selected_skills:
        # Filter our frame to include only selected skills
        skill_data = df_exploded[df_exploded["tags"].isin(selected_skills)]

        # We count the frequency of each skill
        skill_counts = skill_data["tags"].value_counts()

        # Create the bar chart
        fig, ax = plt.subplots()
        fig.tight_layout()
        skill_counts.plot(kind = 'bar', ax = ax, color = 'mediumseagreen')
        ax.set_title("Selected Skill Demand")
        ax.set_xlabel("Skill")
        ax.set_ylabel("Number of Listings")
        plt.xticks(rotation = 45)
        st.pyplot(fig)
    
    # Create a label to direct user engagement
    else: 
        st.info("Select one or more skills from the list to compare trends")

with tab2:
    st.subheader("Top Hiring Companies")

    # Document the top value counts of the top 10 companies
    top_companies = df_filtered['company'].value_counts().head(10)

    st.markdown("### Pie Chart of Job Share by Top Companies")

    company_list = top_companies.index.tolist()
    company_filtered = df_filtered[df_filtered["company"].isin(company_list)]

    # Group by date and company
    company_trends = company_filtered.groupby([df_filtered["date"].dt.to_period('M'), "company"]).size().unstack().fillna(0)

    # Time to plot :]
    fig, ax = plt.subplots(figsize = (15,11))
    ax.tick_params(labelsize = 8)
    ax.pie(top_companies.values, labels = top_companies.index, autopct = '%1.1f%%', startangle = 90)
    ax.axis("equal")
    ax.set_ylabel('')
    ax.set_title("Share of Job Postings by Top Companies")
    st.pyplot(fig)

    selected_comapny = st.selectbox("Select a company for more details", company_list)

    company_data = df_filtered[df_filtered["company"] == selected_comapny]
    st.metric("Job Postings", len(company_data))
    top_skill = df_exploded[df_exploded["company"] == selected_comapny]["tags"].mode().iloc[0]
    st.metric("Top Tag", top_skill)

    # Fix the out of bounds error using is not statement
    top_location = (
        company_data["location"].mode().iloc[0]
        if not company_data['location'].mode().empty
        else "N/A"
    )

    st.metric("Top Location", top_location)

with tab3:
    st.subheader("Job Listings & Download")
    
    # How many rows do we wanna show?
    num_rows = st.slider("How many jobs to show?", 5, 50, 10)

    columns_to_show = ["date", "company", "position", "location", "tags"]
    df_display = df_filtered[columns_to_show].sort_values("date", ascending = False).reset_index(drop = True)

    # Now we get to show the filtered list in a table, not too overwhelming
    st.dataframe(df_display.head(num_rows), use_container_width = True)

    csv_data = df_display.to_csv(index = False)

    # Add a download button incase people want to download their filtered results
    st.download_button(
    label = "Download Filtered Job Listings as CSV",
    data = csv_data,
    file_name = "filtered_jobs.csv",
    mime = "text/csv"
    )

with tab4:
    st.subheader("Job Title Trends")

    keyword = st.text_input("Filter job titles by keyword (optional):", "")

    # We finna get da keywords ofn nga
    title_series = df_filtered["position"].dropna()
    if keyword:
        title_series = title_series[title_series.str.contains(keyword, case = False)]

    # Get top 10 job titles
    top_titles = title_series.value_counts().head(10)

    if not top_titles.empty:
        fig, ax = plt.subplots(figsize = (6,3))
        top_titles.plot(kind = 'barh', ax = ax, color = "orchid")
        ax.set_title("Top Job Titles")
        ax.set_xlabel("Count")
        ax.set_ylabel("Job Title")
        ax.invert_yaxis()
        fig.tight_layout()
        st.pyplot(fig)
    
    else:
        st.info("No job titles found for that keyword.")

