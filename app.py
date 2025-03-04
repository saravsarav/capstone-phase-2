from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import joblib
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Load the trained ML model
try:
    model = joblib.load("vulnerability_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
except FileNotFoundError:
    model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url.startswith("http"):
        return jsonify({"error": "⚠️ Please enter a valid URL starting with http or https."})

    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        vulnerabilities = []

        # ✅ **1. SQL Injection Check (Enhanced)**
        sql_patterns = [r"SELECT.*FROM", r"INSERT.*INTO", r"UPDATE.*SET", r"DELETE.*FROM", r"DROP\s+TABLE"]
        if any(re.search(pattern, response.text, re.IGNORECASE) for pattern in sql_patterns):
            vulnerabilities.append("⚠️ Possible SQL Injection Detected!")

        # ✅ **2. XSS Vulnerability Check (Enhanced)**
        script_tags = soup.find_all("script")
        for script in script_tags:
            if re.search(r"alert\(|document\.write\(", str(script), re.IGNORECASE):
                vulnerabilities.append("⚠️ Possible XSS Found in JavaScript!")

        # ✅ **3. Checking for Suspicious Inputs (Form Injection)**
        form_tags = soup.find_all("form")
        for form in form_tags:
            inputs = form.find_all("input")
            for inp in inputs:
                if inp.get("type") == "text" and inp.get("name") and re.search(r"password|user|email", inp.get("name"), re.IGNORECASE):
                    vulnerabilities.append("⚠️ Potential User Input Vulnerability!")

        # ✅ **4. Machine Learning Model Check**
        if model:
            text_data = [soup.get_text()]
            text_vector = vectorizer.transform(text_data)
            prediction = model.predict(text_vector)
            if prediction[0] == 1:
                vulnerabilities.append("⚠️ ML Model Detected Potential Risk!")

        # ✅ **Final Output Formatting**
        return jsonify({"result": "<br>".join(vulnerabilities) if vulnerabilities else "✅ No Major Vulnerabilities Found"})

    except requests.RequestException as e:
        return jsonify({"error": f"❌ Error Scanning Website: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
