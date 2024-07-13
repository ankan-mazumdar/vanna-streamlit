import streamlit as st
from vanna.remote import VannaDefault, ChromaDB_VectorStore, Mistral
from vanna.chromadb import ChromaDB_VectorStore
from vanna.mistral import Mistral
from google.cloud import bigquery
import logging

logging.basicConfig(level=logging.DEBUG)

class MyVanna(ChromaDB_VectorStore, Mistral):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Mistral.__init__(self, config={'api_key': 'OD24ZZunStRDKv2R5HjAVZTABjTJOhf7', 'model': 'mistral-tiny'})

@st.cache_resource(ttl=3600)
def setup_vanna(database_choice):
    logging.debug("Retrieving API key from session state")
    api_key = st.session_state.get("api_key")
    if not api_key:
        raise ValueError("API key not provided")

    if database_choice == "Chinook":
        vn = VannaDefault(api_key=api_key, model='chinook')
        vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")
    elif database_choice == "BigQuery":
        vn = MyVanna()
        vn.connect_to_bigquery(project_id='nodal-plexus-423300-e9')
    else:
        raise ValueError("Invalid database choice")

    if vn is None:
        raise Exception("Failed to initialize VannaDefault")

    return vn

@st.cache_data(show_spinner="Generating sample questions ...")
def generate_questions_cached(database_choice):
    vn = setup_vanna(database_choice)
    if vn is None:
        st.error("Failed to set up Vanna")
        return []
    questions = vn.generate_questions()
    if questions is None:
        st.error("Failed to generate questions")
        return []
    return questions

@st.cache_data(show_spinner="Generating SQL query ...")
def generate_sql_cached(question: str, database_choice):
    vn = setup_vanna(database_choice)
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="Checking for valid SQL ...")
def is_sql_valid_cached(sql: str, database_choice):
    vn = setup_vanna(database_choice)
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str, database_choice):
    vn = setup_vanna(database_choice)
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Checking if we should generate a chart ...")
def should_generate_chart_cached(question, sql, df, database_choice):
    vn = setup_vanna(database_choice)
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Generating Plotly code ...")
def generate_plotly_code_cached(question, sql, df, database_choice):
    vn = setup_vanna(database_choice)
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code

@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df, database_choice):
    vn = setup_vanna(database_choice)
    return vn.get_plotly_figure(plotly_code=code, df=df)

@st.cache_data(show_spinner="Generating followup questions ...")
def generate_followup_cached(question, sql, df, database_choice):
    vn = setup_vanna(database_choice)
    return vn.generate_followup_questions(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="Generating summary ...")
def generate_summary_cached(question, df, database_choice):
    vn = setup_vanna(database_choice)
    return vn.generate_summary(question=question, df=df)
