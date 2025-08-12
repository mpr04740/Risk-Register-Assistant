import time
import streamlit as st
import pandas as pd
from src.main import process_query
from src.intent_detector import detect_intent

st.markdown("""
    <style>
    /* Global font and main text color */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', 'Arial', sans-serif !important;
        color: #0075BF !important;       /* Professional Blue */
    }
    /* DataFrame/table cells */
    .stDataFrame th, .stDataFrame td {
        color: #0075BF !important;
    }
    /* Headings (st.title, st.header, etc.) */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #0075BF !important;
    }
    /* Sidebar text */
    .css-1d391kg, .css-1v0mbdj, .css-1cpxqw2 { 
        color: #0075BF !important;
    }
    /* BUTTONS: Magenta background, white text always */
    .stButton button {
        font-family: 'Segoe UI', 'Arial', sans-serif !important;
        background-color: rgb(213, 47, 137) !important;   /* Magenta */
        color: #FFFFFF !important;                        /* Force white text */
        border-radius: 7px !important;
        font-size: 16px !important;
        border: none !important;
        padding: 0.5em 1.2em !important;
        transition: background 0.2s;
        font-weight: 500;
    }
    .stButton button:hover {
        background-color: rgb(170, 37, 110) !important;
        color: #FFFFFF !important;
    }
    /* Fixes for possible button text selectors */
    .stButton > button, .stButton button div, .stButton button span {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)


# load DataFrame
df = pd.read_csv('data/Risk_Register__100_Rows.csv')
df.index = df.index + 1

# Set up app formatting
st.set_page_config(page_title="ROBO Risk", layout="centered")
try:
    st.image("data/logo.svg", width=100)
except Exception as e:
    st.warning("Logo could not be loaded.")

# Utility for DataFrame display dynamic height
def show_dataframe_with_index(df_to_show, caption=None):
    display_df = df_to_show.copy()
    n_rows = len(display_df)
    ROW_HEIGHT = 38
    HEADER_HEIGHT = 38
    display_height = HEADER_HEIGHT + (min(n_rows, 5) * ROW_HEIGHT)

    st.dataframe(
        display_df,
        use_container_width=True,
        height=display_height
    )
    st.caption(f"Rows displayed: {n_rows}")
    if caption:
        st.caption(caption)


# Generator to stream out your filtered data + summaries
def stream_results(filtered_df, filter_explanation, summary, final_summary, intent):
    # Filtered-data section
    if 'filter_data' in intent:
        yield "**Filtered Data**\n\n"
        time.sleep(0.09)

        if filter_explanation:
            yield f"*Filter applied:* {filter_explanation}\n\n"
            time.sleep(0.09)

        if filtered_df is not None and not filtered_df.empty:
            # Streamlit will render the DataFrame for you
            yield filtered_df
        else:
            yield "There are no risks matching this criteria.\n\n"

        time.sleep(0.)  # pause before next section

    # Summary section
    if 'other' in intent or 'summarise_risks' in intent:
        yield "\n**Summary**\n\n"
        time.sleep(0.05)

        text = final_summary if 'other' in intent else summary
        # Stream word-by-word
        for w in text.split(" "):
            yield w + " "
            time.sleep(0.02)

        yield "\n"


# Behaviour pre query submission
if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False

# Show full risk register before first query
if not st.session_state['submitted']:
    st.subheader("Risk Register")
    show_dataframe_with_index(df)

# Query input
user_query = st.text_input("Hi, I'm ROBO. \n How can help? Ask me anything about the risk register:", "")

# When user clicks Submit
if st.button("Submit") and user_query.strip():
    st.session_state['submitted'] = True

    # Detect intent and build action message
    intent = detect_intent(user_query)
    intent_map = {
        'filter_data': 'filtering the data',
        'summarise_risks': 'generating a data summary',
        'other': 'generating a final answer'
    }
    intent_list = [desc for key, desc in intent_map.items() if key in intent]
    action_msg = ', then '.join(intent_list) if intent_list else 'processing your request'
    st.info(f"This query involves {action_msg}.")

    # Run the query
    with st.spinner(f"Thinking..."):
        filtered_df, filter_explanation, summary, final_summary = process_query(
            user_query, df, intent
        )
        st.markdown("---")

    # Stream out the results
    gen = stream_results(
        filtered_df,
        filter_explanation,
        summary,
        final_summary,
        intent
    )
    st.write_stream(gen)

else:
    if not st.session_state['submitted']:
        st.info("Enter your query and press Submit to see results.")
