"""Turns question into a SQL query using the Gemini API."""
import json

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY
from app.database import get_schema

GEMINI_MODEL = "gemini-2.5-flash"

# One client is created at startup and reused for every request.
client = genai.Client(api_key=GEMINI_API_KEY)


def build_prompt(question: str) -> str:
    """Combine the table structure, SQL rules, and the user's question into one prompt."""
    schema = get_schema()
    columns = "\n".join(
        f"- {column['name']} ({column['type']})" for column in schema["columns"]
    )
    return f"""You convert questions about a vehicle-offers dataset into a single SQLite SELECT query.

Table: {schema['table']}
Columns:
{columns}

Important data note:
- Every column is stored as TEXT, including numeric-looking values like prices,
  APRs, mileage, terms, and payments.
- Before doing arithmetic, comparison, sorting, AVG, SUM, MIN, or MAX on a numeric
  column, clean and cast it.
- For money/number fields: CAST(REPLACE(REPLACE(column, '$', ''), ',', '') AS REAL)
- For percent fields: CAST(REPLACE(column, '%', '') AS REAL)
- Exclude NULL and empty-string values when aggregating numeric fields.

Rules:
- Generate SQLite-compatible SQL only.
- Use only the table and columns listed above; do not invent tables or columns.
- Return exactly one SELECT statement.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, or multiple statements.
- Do not use SELECT * for analytical answers unless the user explicitly asks to see rows.
- For list-style questions, include LIMIT 10 unless the user asks for a different number.
- Use LOWER(column) for text comparisons when helpful.

Respond only with JSON in the form {{"sql": "<query>"}}.

Question: {question}"""


def generate_sql(question: str) -> str:
    """Ask Gemini for a SQL query that answers the question and return it as a string."""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=build_prompt(question),
        # Force the reply to be JSON so it can be parsed reliably.
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(response.text)["sql"]