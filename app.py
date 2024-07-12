import time
import streamlit as st
from vanna_calls import (
    generate_questions_cached,
    generate_sql_cached,
    run_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
    generate_followup_cached,
    should_generate_chart_cached,
    is_sql_valid_cached,
    generate_summary_cached
)

avatar_url = "https://vanna.ai/img/vanna.svg"

st.set_page_config(layout="wide")

st.sidebar.title("API Key Settings")
api_key_input = st.sidebar.text_input("Enter Vanna API Key", type="password")

if api_key_input:
    st.session_state["api_key"] = api_key_input
    st.success("API Key saved successfully!")
else:
    st.warning("Please enter your Vanna API Key.")

st.sidebar.title("Output Settings")
st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
st.sidebar.checkbox("Show Table", value=True, key="show_table")
st.sidebar.checkbox("Show Plotly Code", value=True, key="show_plotly_code")
st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
st.sidebar.checkbox("Show Summary", value=True, key="show_summary")
st.sidebar.checkbox("Show Follow-up Questions", value=True, key="show_followup")
st.sidebar.button("Reset", on_click=lambda: set_question(None), use_container_width=True)

st.title("Vanna AI")

def set_question(question):
    st.session_state["my_question"] = question

# Ensure the input box is displayed initially
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.chat_input("Ask me a question about your data", key="user_question_input")
    if user_input:
        st.session_state["my_question"] = user_input
with col2:
    if st.button("Clear and Start New Session", key="clear_button"):
        st.session_state.clear()
        st.experimental_rerun()

if "my_question" not in st.session_state:
    st.session_state["my_question"] = None

if st.session_state["my_question"]:
    my_question = st.session_state["my_question"]

    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = generate_sql_cached(question=my_question)

    if sql:
        if is_sql_valid_cached(sql=sql):
            if st.session_state.get("show_sql", True):
                assistant_message_sql = st.chat_message(
                    "assistant", avatar=avatar_url
                )
                assistant_message_sql.code(sql, language="sql", line_numbers=True)
        else:
            assistant_message = st.chat_message(
                "assistant", avatar=avatar_url
            )
            assistant_message.write(sql)
            st.stop()

        df = run_sql_cached(sql=sql)

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("show_table", True):
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                if len(df) > 10:
                    assistant_message_table.text("First 10 rows of data")
                    assistant_message_table.dataframe(df.head(10))
                else:
                    assistant_message_table.dataframe(df)

            if should_generate_chart_cached(question=my_question, sql=sql, df=df):

                code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)

                if st.session_state.get("show_plotly_code", False):
                    assistant_message_plotly_code = st.chat_message(
                        "assistant",
                        avatar=avatar_url,
                    )
                    assistant_message_plotly_code.code(
                        code, language="python", line_numbers=True
                    )

                if code is not None and code != "":
                    if st.session_state.get("show_chart", True):
                        assistant_message_chart = st.chat_message(
                            "assistant",
                            avatar=avatar_url,
                        )
                        fig = generate_plot_cached(code=code, df=df)
                        if fig is not None:
                            assistant_message_chart.plotly_chart(fig)
                        else:
                            assistant_message_chart.error("I couldn't generate a chart")

            if st.session_state.get("show_summary", True):
                assistant_message_summary = st.chat_message(
                    "assistant", avatar=avatar_url
                )
                summary = generate_summary_cached(question=my_question, df=df)
                if summary is not None:
                    assistant_message_summary.text(summary)

            if st.session_state.get("show_followup", True):
                assistant_message_followup = st.chat_message(
                    "assistant", avatar=avatar_url
                )
                followup_questions = generate_followup_cached(
                    question=my_question, sql=sql, df=df
                )
                st.session_state["df"] = None

                if len(followup_questions) > 0:
                    assistant_message_followup.text(
                        "Here are some possible follow-up questions"
                    )
                    # Print the first 5 follow-up questions
                    for i, question in enumerate(followup_questions[:5]):
                        assistant_message_followup.button(
                            question, 
                            on_click=set_question, 
                            args=(question,),
                            key=f"followup_question_button_{i}"
                        )

    else:
        assistant_message_error = st.chat_message(
            "assistant", avatar=avatar_url
        )
        assistant_message_error.error("I wasn't able to generate SQL for that question")
else:
    assistant_message_suggested = st.chat_message(
        "assistant", avatar=avatar_url
    )
    if assistant_message_suggested.button("Click to show suggested questions"):
        st.session_state["my_question"] = None
        questions = generate_questions_cached()
        if questions:
            for i, question in enumerate(questions):
                time.sleep(0.05)
                button = st.button(
                    question,
                    on_click=set_question,
                    args=(question,),
                    key=f"suggested_question_button_{i}"
                )
        else:
            st.error("No suggested questions available")
