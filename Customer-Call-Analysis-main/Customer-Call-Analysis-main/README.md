# Customer Call Transcript Analysis

## Overview
This is a **Python Flask application** that analyzes customer call transcripts using the **Groq API**.  
It summarizes the conversation in 2–3 sentences, extracts the customer’s sentiment (positive, neutral, or negative), and saves the results into a CSV file for easy review.  

This project demonstrates a simple workflow for **customer support analytics** and can be extended for large-scale transcript analysis.  

---

## Features
- Accepts customer call transcripts via a **web interface** or **API endpoint**.  
- Uses Groq API to:
  - Generate a short **summary** of the transcript.
  - Identify **sentiment** (`positive`, `neutral`, `negative`).  
- Displays the transcript, summary, and sentiment in real-time.  
- Saves results into **`call_analysis.csv`** with columns: `Transcript | Summary | Sentiment`.  

---

## Requirements
- Python 3.x  
- Packages (install via `pip install -r requirements.txt`):
flask
groq
python-dotenv


---

## Setup Instructions
1. **Clone the repository** or download the project folder.  
2. **Set your Groq API key** as an environment variable:
 ```bash
 export GROQ_API_KEY="your_groq_api_key_here"
 # On Windows PowerShell:
 # $env:GROQ_API_KEY="your_groq_api_key_here"
pip install -r requirements.txt
python app.py
