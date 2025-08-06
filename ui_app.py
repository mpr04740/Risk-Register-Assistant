import time
import streamlit as st
import pandas as pd
from src.main import process_query
from src.intent_detector import detect_intent


# load DataFrame
df = pd.read_csv('data/Risk_Register__100_Rows.csv')

# Set up app formatting
st.set_page_config(page_title="Risk Register Assistant", layout="centered")
st.title("Risk Register Assistant")


# Utility for DataFrame display with 1-based index and dynamic height
def show_dataframe_with_index(df_to_show, caption=None):
    display_df = df_to_show.copy()
    display_df.index = display_df.index + 1
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
user_query = st.text_input("Enter your risk query:", "")

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
    with st.spinner(f"Loading... {action_msg.capitalize()}..."):
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
