import os
import pandas as pd
import plotly.express as px
import streamlit as st

CLEAN_PATH = os.path.join("data", "clean", "reviews_clean.csv")
WC_PATH = os.path.join("data", "clean", "wordcloud_negative.png")

st.set_page_config(page_title="Food Delivery Pain Points", layout="wide")
st.title("📦 Food Delivery Customer Pain Points – Enhanced Dashboard")

# Check if clean dataset exists
if not os.path.exists(CLEAN_PATH):
    st.warning("No clean dataset found. Run the scrapers and `analyze.py` first.")
    st.stop()

# Load dataset with caching
@st.cache_data
def load_data(path):
    if "at" in pd.read_csv(path, nrows=0).columns:
        return pd.read_csv(path, parse_dates=["at"], infer_datetime_format=True)
    return pd.read_csv(path)

df = load_data(CLEAN_PATH)

# Display dataset summary
st.subheader("Dataset Overview")
st.write(f"Total reviews: {len(df)}")
st.dataframe(df.head(10))

# Display WordCloud
if os.path.exists(WC_PATH):
    st.subheader("Negative Reviews WordCloud")
    st.image(WC_PATH, use_column_width=True)

# Sentiment distribution plot
st.subheader("Sentiment Distribution")
sent_counts = df["sent_label"].value_counts()
fig = px.bar(
    x=sent_counts.index,
    y=sent_counts.values,
    labels={"x": "Sentiment", "y": "Count"},
    text=sent_counts.values,
    color=sent_counts.index,
    color_discrete_map={"positive": "green", "negative": "red", "neutral": "gray"}
)
st.plotly_chart(fig, use_container_width=True)

# Sentiment Trend Over Time
if "at" in df.columns:
    st.subheader("Sentiment Trend Over Time")
    trend = df.groupby([pd.Grouper(key="at", freq="W"), "sent_label"]).size().reset_index(name="count")
    fig3 = px.line(
        trend, x="at", y="count", color="sent_label",
        labels={"at": "Date", "count": "Review Count", "sent_label": "Sentiment"},
        color_discrete_map={"positive": "green", "negative": "red", "neutral": "gray"}
    )
    st.plotly_chart(fig3, use_container_width=True)

# Top reported issues
st.subheader("Top Reported Issues")
top_issues = df["issues"].str.split("|").explode().value_counts().head(10)
fig2 = px.bar(
    x=top_issues.index,
    y=top_issues.values,
    labels={"x": "Issue", "y": "Count"},
    text=top_issues.values,
    color=top_issues.values,
    color_continuous_scale="OrRd"
)
st.plotly_chart(fig2, use_container_width=True)

# Negative issue breakdown
st.subheader("Negative Issue Breakdown")
if "sent_label" in df.columns and "issues" in df.columns:
    negative_issues = df[df["sent_label"] == "negative"]["issues"].str.split("|").explode().value_counts().head(10)
    fig4 = px.pie(
        values=negative_issues.values,
        names=negative_issues.index,
        title="Top Issues in Negative Reviews",
        color=negative_issues.index,
        color_discrete_sequence=px.colors.sequential.Reds
    )
    st.plotly_chart(fig4, use_container_width=True)
