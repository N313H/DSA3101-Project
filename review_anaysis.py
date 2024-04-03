from flask import Flask, request, jsonify
from h2ogpte import H2OGPTE
import numpy as np
import pandas as pd
import os


app = Flask(__name__)

API_KEY = "sk-ms7SU43E34tS9UJks5RD2KM3m1JumOR2pM73Dk95VzKjM6TZ"
REMOTE_ADDRESS = "https://h2ogpte.genai.h2o.ai"

# Initialize H2OGPTE client
client = H2OGPTE(address=REMOTE_ADDRESS, api_key=API_KEY)

@app.route('/analyze_review', methods=['POST'])
#data extraction
def analyze_review():
    # Get review text from request data
    review = request.json.get('review')
    # Perform review analysis
    extract = client.extract_data(
        text_context_list= [review],
        #pre_prompt_extract="Pay attention and look at all people. Your job is to collect their names.\n",
        prompt_extract="List the good thing and suggestions for improvement. Ignore grammatical errors and awkward languages"
    )
    # List of LLM answers per text input
    extracted_data = []
    for extract_list_item in extract.content:
        for s in extract_list_item.split("\n"):
            extracted_data.append(s)

    # Return the extracted data as JSON
    return jsonify(extracted_data)

#get output of analysis
if __name__ == '__main__':
    app.run(debug=True)