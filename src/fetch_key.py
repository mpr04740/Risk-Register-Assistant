import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

def get_openai_key() -> str | None:
    # Load .env for local dev
    load_dotenv()  # looks for .env up the tree

    # 1) Try environment first (local dev / Docker / CI)
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    # 2) Try Streamlit secrets (deployed)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None