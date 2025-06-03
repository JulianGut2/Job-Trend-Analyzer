# General imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

tab1, tab2, tab3 = st.tabs(["Skill Trends", "Company Insights", "Raw Listings"])

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

    # Charts the companies AS LONG AS top_companies is not empty
    if not top_companies.empty:
        fig, ax = plt.subplots()
        top_companies.plot(kind = 'barh', ax = ax, color = 'skyblue')
        ax.set_title('Top Hiring Companies')
        ax.set_xlabel("Number of Job Listings")
        ax.set_ylabel("Company")
        ax.invert_yaxis()
        st.pyplot(fig)

    # Print this if top companies is empty
    else:
        st.info("No companu data available in the selected date range.")

    st.markdown("---")

    # Create a list of company options with no dupes and dropping empty values 



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
