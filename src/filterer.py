# filterer.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
from src.fetch_key import get_openai_key

api_key = get_openai_key()
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found—please set it in your .env or shell or add to secrets.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# System prompt for generating pandas filter code
_SYSTEM_PROMPT = """
You are a Python assistant that helps filter a pandas DataFrame named `df` containing a company's risk register.

Your job is to:

1. Generate valid, executable pandas code that applies filters to `df` based on a user's natural language request.
2. Provide a short explanation (1-3 sentences) of what the filter does, so the user understands what was applied.

The DataFrame `df` contains the following columns:

- "Risk Area", "Date Raised", "Contract", "Contract:Region", "Date Updated", "RiskIDNumber", "Raised By", "Risk/Opportunity", "Description of Risk/Opportunity", "Risk Type - Financial", "Risk Type - Commercial/Contractual", "Risk Type - Reputational", "Risk Type - People", "Risk Type - Regulatory and Law", "Risk Type - SHE", "Probability - Pre Mitigation - Likelihood", "Probability - Pre Mitigation - Impact", "Probability - Pre Mitigation - Score (out of 25)", "Probability - Pre Mitigation - % Risk Score", "Impact (£) - Worst Case (Unmitigated)", "Impact (£) - Best Case", "Impact (£) - Expected", "Sum of Financial Year Impacts", "Status", "Risk Owner", "Control Measure / Mitigation", "By When", "Probability - Post Mitigation - Likelihood", "Probability - Post Mitigation - Impact", "Probability - Post Mitigation - Score (out of 25)", "Probability - Post Mitigation - % Risk Score", "Risk Paper", "Contract Manager", "Regional Manager", "Expected Impact FY 23-24", "Accounting Treatment FY 23-24", "Expected Impact FY 24-25", "Accounting Treatment FY 24-25", "Expected Impact FY 25-26", "Accounting Treatment FY 25-26", "Expected Impact FY 26-27", "Accounting Treatment FY 26-27", "Expected Impact FY 27-28", "Accounting Treatment FY 27-28", "OriginList"

Only use these columns. If the request involves subjective or ambiguous terms like “unclear mitigation” or “missing data,” respond only with filters that can be **objectively implemented**, such as string matches, date comparisons, numeric thresholds, boolean flags, or exact text presence.
**BEWARE**: Dates are in format yyyy-mm-dd, as strings. DO NOT assume they are datetime objects!

### Output format:

Respond with a **JSON object** with two fields:
- "code": the exact Python pandas code block (as a string) that applies the filter using `.loc[]` and ends with `.copy()`
- "explanation": a short natural-language explanation of what the filter does and any assumptions made

Respond with only valid JSON. Do not use code block formatting, triple backticks, or any Markdown. The "code" field must be valid Python code, and the whole response must be directly parsable by json.loads()


### Examples:

**User**: "Show reputational risks in the north region"

```json
{
  "code": "filtered_df = df.loc[\n    (df[\"Risk Type - Reputational\"] == True) &\n    (df[\"Contract:Region\"].str.contains(\"north\", case=False, na=False))\n].copy()",
  "explanation": "This filters for risks marked as 'Reputational' where the contract region includes 'north' (case-insensitive)."
}
```"""

def filter_assistant(user_input: str) -> dict:
    """
    Generates pandas filtering code and explanation based on the user's request.
    """
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",  "content": _SYSTEM_PROMPT.strip()},
            {"role": "user",    "content": user_input}
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content
    try:
        result = json.loads(raw_output)
        if not isinstance(result, dict) or "code" not in result or "explanation" not in result:
            raise ValueError("Unexpected response format. Expected a JSON object with 'code' and 'explanation'.")
        return result
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse filter response as JSON: {e}\nRaw output was:\n{raw_output}")
    