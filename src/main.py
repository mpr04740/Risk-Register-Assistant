# main.py
from dotenv import load_dotenv
import pandas as pd
from src.filterer import filter_assistant 
from src.summariser import summary_assistant
from src.other import other_assistant


def process_query(user_query, df, intent):
    """
    Handles full pipeline given a user_query and a DataFrame.
    Returns: (filtered_df, filter_explanation, summary, final_summary)
    """
    filtered_df = None
    filter_explanation = ""
    summary = ""
    final_summary = ""

    if "filter_data" in intent:
        filter_json = filter_assistant(user_query)
        pandas_code = filter_json['code']
        filter_explanation = filter_json['explanation']
        ns = {"df": df, "pd": pd}
        exec(pandas_code, ns)
        filtered_df = ns['filtered_df']

    if "summarise_risks" in intent:
        summary = summary_assistant(user_query, filtered_df, filter_explanation, intent)

    if "other" in intent:
        if "summarise_risks" not in intent:
            final_summary = other_assistant(user_query, summary, filter_explanation, filtered_df)

        else:
           final_summary = other_assistant(user_query, summary, filter_explanation)

    return filtered_df, filter_explanation, summary, final_summary

