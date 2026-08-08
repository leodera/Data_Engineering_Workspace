import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Streamlit in Jupyter", layout="wide")

st.title("Interactive Streamlit Dashboard")
st.write("Running directly inside a Jupyter Notebook cell.")


@st.cache_data
def load_data():
    return px.data.gapminder()

df = load_data()


st.sidebar.header("Filter Controls")
continent = st.sidebar.selectbox("Select Continent", df["continent"].unique())
metric = st.sidebar.selectbox("Select Metric", ["lifeExp", "gdpPercap", "pop"])


filtered_df = df[df["continent"] == continent]


fig = px.line(
    filtered_df, 
    x="year", 
    y=metric, 
    color="country", 
    title=f"{metric} over time in {continent}",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)