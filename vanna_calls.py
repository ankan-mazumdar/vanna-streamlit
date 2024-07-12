import streamlit as st
from vanna.remote import VannaDefault
import logging

logging.basicConfig(level=logging.DEBUG)

@st.cache_resource(ttl=3600)
def setup_vanna():
    logging.debug("Retrieving API keys from secrets")
    api_keys = st.secrets.get("api_keys")
    logging.debug(f"API Keys: {api_keys}")
    if api_keys is None:
        raise ValueError("API keys not found in secrets.toml")

    api_key = api_keys["vanna_key"]
    vn = VannaDefault(api_key=api_key, model='chinook')
    if vn is None:
        raise Exception("Failed to initialize VannaDefault")

    vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")
    return vn

@st.cache_data(show_spinner="Generating sample questions ...")
def generate_questions_cached():
    vn = setup_vanna()
    if vn is None:
        st.error("Failed to set up Vanna")
        return []
    questions = vn.generate_questions()
    if questions is None:
        st.error("Failed to generate questions")
        return []
    return questions

@st.cache_data(show_spinner="Generating SQL query ...")
def generate_sql_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="Checking for valid SQL ...")
def is_sql_valid_cached(sql: str):
    vn = setup_vanna()
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Checking if we should generate a chart ...")
def should_generate_chart_cached(question, sql, df):
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Generating Plotly code ...")
def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code

@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)

@st.cache_data(show_spinner="Generating followup questions ...")
def generate_followup_cached(question, sql, df):
    vn = setup_vanna()
    return vn.generate_followup_questions(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="Generating summary ...")
def generate_summary_cached(question, df):
    vn = setup_vanna()
    return vn.generate_summary(question=question, df=df)
