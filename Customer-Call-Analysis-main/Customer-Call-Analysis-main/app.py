# app.py
import os
import json
import csv
from pathlib import Path
from flask import Flask, request, render_template_string, jsonify
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # reads env var GROQ_API_KEY

CSV_FILE = Path("call_analysis.csv")

# Ensure CSV header exists
if not CSV_FILE.exists():
    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Transcript", "Summary", "Sentiment"])

# Simple HTML form
HTML = """
<!doctype html>
<title>Call Transcript Analyzer</title>
<h2>Paste a short customer call transcript</h2>
<form action="/analyze" method=post>
  <textarea name="transcript" rows="8" cols="80" placeholder="Enter transcript here..."></textarea><br><br>
  <button type="submit">Analyze</button>
</form>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

def call_groq(transcript: str) -> dict:
    """Call Groq chat completions with a JSON schema (Structured Outputs)."""
    # response_format follows Groq Structured Outputs JSON Schema mode
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "call_analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "neutral", "negative"]
                    }
                },
                "required": ["summary", "sentiment"],
                "additionalProperties": False
            }
        }
    }

    system_msg = {
        "role": "system",
        "content": (
            "You are an assistant that extracts a short (2-3 sentence) summary "
            "and the customer's sentiment (one of: positive, neutral, negative) "
            "from the provided customer call transcript. Output JSON only that "
            "matches the schema: {summary: string, sentiment: 'positive'|'neutral'|'negative'}."
        ),
    }

    user_msg = {"role": "user", "content": f"Transcript:\n{transcript}"}

    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[system_msg, user_msg],
        response_format=response_format,
    )

    # The content is a JSON string per Groq Structured Outputs example
    raw = resp.choices[0].message.content
    if isinstance(raw, str):
        return json.loads(raw)
    elif isinstance(raw, dict):
        return raw
    else:
        raise ValueError("Unexpected response format from Groq")

@app.route("/analyze", methods=["POST"])
def analyze():
    # Accept either form or JSON POST
    transcript = None
    if request.is_json:
        data = request.get_json()
        transcript = data.get("transcript")
    else:
        transcript = request.form.get("transcript")

    if not transcript or not transcript.strip():
        return "No transcript provided", 400

    try:
        result = call_groq(transcript.strip())
        summary = result.get("summary", "").strip()
        sentiment = result.get("sentiment", "").strip()
    except Exception as e:
        return f"Error calling Groq API: {e}", 500

    # Append to CSV
    with CSV_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([transcript, summary, sentiment])

    # Return a simple HTML page showing the original transcript, summary, sentiment
    return render_template_string(
        "<h3>Analysis Result</h3>"
        "<b>Transcript:</b><pre>{{t}}</pre>"
        "<b>Summary:</b><p>{{s}}</p>"
        "<b>Sentiment:</b><p>{{sent}}</p>"
        "<p>Saved to call_analysis.csv</p>",
        t=transcript,
        s=summary,
        sent=sentiment,
    )

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(force=True)
    transcript = data.get("transcript")
    if not transcript:
        return jsonify({"error": "transcript missing"}), 400
    try:
        result = call_groq(transcript)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Append to CSV
    with CSV_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([transcript, result["summary"], result["sentiment"]])

    return jsonify({"transcript": transcript, "summary": result["summary"], "sentiment": result["sentiment"]})

if __name__ == "__main__":
    app.run(debug=True)
