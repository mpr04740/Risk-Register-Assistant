# summariser.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
from typing import Optional

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found—please set it in your .env or shell.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# System prompt for generating high quality summaries
_SYSTEM_PROMPT = """
You are a risk summarisation assistant.

Your task is to read a set of risks from the company risk register and generate a concise written report based on the user's question.

You will be given:
- A user prompt (natural language query, e.g. “What are the biggest risk areas in the next month?”)
- A table of filtered risks, as rows from a pandas DataFrame in JSON format (each row is a dictionary)

You should:
- Understand the user's intent from the question
- Analyse the filtered data to detect meaningful trends or findings
- Mention key fields such as risk area, type, financial impact, dates, status, or owners — depending on what's relevant
- Focus on summarising the **most important insights** clearly and briefly
- If the filtered data is empty, return a simple message like: “No risks match the criteria.”
- Do not attempt to answer questions which are unrelated to the data. 

### Output format:
Respond only with a short natural-language paragraph (3-5 sentences). Do not output code or tables.
Make it look pretty! Use paragraphs, bullet points and other formatting tools like bold when appropriate.
**Use bold** as much as is appropriate to help fast reading and understanding.

### Examples:

**User Prompt**:  
"What are the most important risks this quarter?"  
**Filtered Data**: 7 risk rows, mostly reputational and commercial, impact values ranging from £500k to £2M, most marked “Open”

**Response**:  
"During this quarter, the company is facing several high-impact risks primarily in reputational and commercial areas. A majority of these risks are still open and unresolved. Financial exposure ranges up to £2 million, with a concentration in regional contracts. The data suggests a need for urgent review of reputational controls and stakeholder management strategies."

---

Always write in plain, business-friendly English. Focus on actionable insight.
"""

def summary_assistant(
    user_input: str,
    filtered_df: Optional[pd.DataFrame] = None,
    filter_explanation: Optional[str] = None,
    intent: Optional[list] = None
) -> str:
    """
    Generate a summary report for `user_input` using:
    - filtered_df: the DataFrame after filtering (or None)
    - filter_explanation: explanation of that filter (or None)

    Returns the assistant's summary as a string.
    """

    payload = {"user_prompt": user_input}

    if filtered_df is not None:
        records = filtered_df.to_dict(orient="records")
        
        if 'filter_data' in intent:
            payload["filtered_data"] = records
        else:
            payload['complete_unfiltered_data'] = records

    if filter_explanation is not None:
        payload["filter_explanation"] = filter_explanation

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",  "content": _SYSTEM_PROMPT.strip()},
            {"role": "user",    "content": json.dumps(payload)}
        ],
        temperature=0.2
    )

    summary = response.choices[0].message.content.strip()
    if not summary:
        raise ValueError("Empty summary returned")
    return summary