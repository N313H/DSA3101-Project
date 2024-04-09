from flask import Flask, jsonify, request, render_template, redirect, send_file
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
from collections import defaultdict

from flask import Flask, jsonify, request
import pandas as pd
import os
import re
from h2ogpte import H2OGPTE

app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": ["http://localhost:3002", "http://localhost:3000"]}})


def connect_to_mysql():
    return mysql.connector.connect(
        host="db",
        user="root",
        password="pikapikachu!",
        database="connect",
        port=3306
    )

# Read JSON file
def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

app = Flask(__name__)

API_KEY = "sk-ms7SU43E34tS9UJks5RD2KM3m1JumOR2pM73Dk95VzKjM6TZ"
REMOTE_ADDRESS = "https://h2ogpte.genai.h2o.ai"

if not API_KEY:
    raise ValueError("Please configure h2ogpte API key")

client = H2OGPTE(address=REMOTE_ADDRESS, api_key=API_KEY)

# Load the CSV file containing reviews
tor = pd.read_csv('/Users/blabbyduck/Desktop/Y3S2/DSA3101/DSA3101-Project/csv_output/TopicsofReviews.csv')

# Function to convert DataFrame to string
def convert_str(topic_review):
    compiled_review = topic_review['review'].to_string()

    comp_rev = ""
    for row in compiled_review:
        comp_rev += row
    return comp_rev

##Summary
@app.route('/api/summary', methods=['GET'])
def get_summary():
    topic = request.args.get('topic')

    if topic is None:
        return jsonify({"error": "Please provide a topic parameter"}), 400

    issue1 = tor.loc[tor['Topic_Name'] == topic]
    review = convert_str(issue1)
    extract = client.extract_data(
        text_context_list=[review],
        prompt_extract="Recommend improvements based on the reviews. Ignore grammatical errors and awkward languages. Do not return the review numbers"
    )
    
    # Extracted summaries
    summaries = []
    for extract_list_item in extract.content:
        for s in extract_list_item.split("\n"):
            s = re.sub('\W+',' ', s)
            summaries.append(s)
    
    return jsonify({"summaries": summaries})





##Topic_issue code
# Function to convert DataFrame to string
def convert_str(topic_review):
    compiled_review = topic_review['review'].to_string()

    comp_rev = ""
    for row in compiled_review:
        comp_rev += row
    return comp_rev

# Function to extract common issues
def common_issues(review):
    extract = client.extract_data(
        text_context_list= [review],
        #pre_prompt_extract="Pay attention and look at all people. Your job is to collect their names.\n",
        prompt_extract="Extract all the common issues faced by the application according to the reviews, as well as their corresponding index after the identified issues. Do not return positive. Strictly return in the following format, issues : indexes without additional information"
    )
    # List of LLM answers per text input
    sol = []
    for extract_list_item in extract.content:
        for s in extract_list_item.split("\n"):
            s = re.sub('\W+',' ', s)
            sol.append(s)
    return sol
# Function to extract review
#format it so that they are in dic form, for better df manipulation
def extract_review(issue_ind):
    result_dict = {}
    for item in issue_ind:
        # Use regex to extract the string part without numbers
        string = re.sub(r'\d+', '', item)  # Replace all digits with an empty string
        string = string.strip()  # Remove leading and trailing whitespaces
        
        numbers = [int(num) for num in item.split() if num.isdigit()]  # Extract all numbers in the string
        if string in result_dict:
            result_dict[string].extend(numbers)
        else:
            result_dict[string] = numbers
    
    return result_dict

# Function to get DataFrame of issues for a given topic
def issue_df(topic):
    issue1 = tor.loc[tor['Topic_Name'] == topic]
    review_str = convert_str(issue1)
    review_lst = common_issues(review_str)
    dic = extract_review(review_lst)

    # Get all indices covered by the dictionary values
    covered_indices = set(index for indices in dic.values() for index in indices)

    # Get all indices in the tor dataset
    all_indices = set(issue1['index'])

    # Get the remaining indices
    remaining_indices = all_indices - covered_indices

    # Create an empty list to hold individual DataFrames
    dfs = []

    # Iterate over the dictionary items
    for key, indices in dic.items():
        # Create a DataFrame for each key-value pair
        indices_with_reviews = [index for index in indices if index in issue1.index]
        df = pd.DataFrame({'key': [key] * len(indices_with_reviews),
                           'review': [issue1.loc[i, 'review'] for i in indices_with_reviews]})
        dfs.append(df)

    # Add remaining indices under "Others"
    if remaining_indices:
        others_indices_with_reviews = [index for index in remaining_indices if index in issue1.index]
        others_df = pd.DataFrame({'key': ['Others'] * len(others_indices_with_reviews),
                                  'review': [issue1.loc[i, 'review'] for i in others_indices_with_reviews]})
        dfs.append(others_df)

    # Concatenate all DataFrames together
    result_df = pd.concat(dfs, ignore_index=True)

    return result_df

# API endpoint to get DataFrame of issues for a given topic
@app.route('/api/issues', methods=['GET'])
def get_issues():
    topic = request.args.get('topic')

    if topic is None:
        return jsonify({"error": "Please provide a topic parameter"}), 400

    # Get DataFrame of issues for the given topic
    df = issue_df(topic)

    # Convert DataFrame to JSON
    json_data = df.to_json(orient='records')

    return json_data

if __name__ == '__main__':
    app.run(debug=True)


