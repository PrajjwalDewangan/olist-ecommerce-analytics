import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()


ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
PAT = os.getenv("SNOWFLAKE_PAT")

API_URL = (
    f"https://{ACCOUNT}.snowflakecomputing.com"
    "/api/v2/cortex/analyst/message"
)


def load_semantic_model():
    yaml_path = Path(__file__).parent.parent / "semantic_model.yaml"

    with open(yaml_path, "r", encoding="utf-8") as f:
        return f.read()


def ask_analyst(question):

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question,
                    }
                ],
            }
        ],
        "semantic_model": load_semantic_model(),
    }

    headers = {
        "Authorization": f"Bearer {PAT}",
        "Content-Type": "application/json",
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
    }

    response = requests.post(
        API_URL,
        json=payload,
        headers=headers,
        timeout=120,
    )

    return response

def extract_sql(response_json):

    for block in response_json["message"]["content"]:

        if block["type"] == "sql":
            return block["statement"]

    return None

def extract_text(response_json):

    for block in response_json["message"]["content"]:

        if block["type"] == "text":
            return block["text"]

    return ""