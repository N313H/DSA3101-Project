from flask import Flask, jsonify, request
import mysql.connector
import pandas as pd
import json
import re
from h2ogpte import H2OGPTE
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3002", "http://localhost:3000"]}})

# Function to connect to MySQL
def connect_to_mysql():
    return mysql.connector.connect(
        host="db",
        user="root",
        password="pikapikachu!",
        database="connect",
        port=3306
    )

# Function to read JSON file
def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data



# Establish MySQL connection and read data
db = connect_to_mysql()
my_data = pd.read_sql("SELECT * FROM review", db)

# prepare database
tor = my_data

# Configure H2OGPTE
API_KEY = "sk-ms7SU43E34tS9UJks5RD2KM3m1JumOR2pM73Dk95VzKjM6TZ"
REMOTE_ADDRESS = "https://h2ogpte.genai.h2o.ai"
client = H2OGPTE(address=REMOTE_ADDRESS, api_key=API_KEY)

# Function to convert DataFrame to string
def convert_str(topic_review):
    return ''.join(topic_review['review'].astype(str))

# API endpoint for getting summary
@app.route('/api/summary', methods=['GET'])
def get_summary():
    topic = request.args.get('topic')
    if topic is None:
        return jsonify({"error": "Please provide a topic parameter"}), 400

    # Assuming `tor` DataFrame is defined somewhere
    issue1 = tor.loc[tor['Topic_Name'] == topic]
    review = convert_str(issue1)
    extract = client.extract_data(
        text_context_list=[review],
        prompt_extract="Recommend improvements based on the reviews. Ignore grammatical errors and awkward languages. Do not return the review numbers"
    )

    summaries = [re.sub('\W+',' ', s) for extract_list_item in extract.content for s in extract_list_item.split("\n")]
    
    return jsonify({"summaries": summaries})

# Function to extract common issues from reviews
def common_issues(review):
    extract = client.extract_data(
        text_context_list= [review],
        prompt_extract="Extract all the common issues faced by the application according to the reviews, as well as their corresponding index after the identified issues. Do not return positive. Strictly return in the following format, issues : indexes without additional information"
    )
    return [re.sub('\W+',' ', s) for extract_list_item in extract.content for s in extract_list_item.split("\n")]

# Function to extract review
def extract_review(issue_ind):
    result_dict = defaultdict(list)
    for item in issue_ind:
        string = re.sub(r'\d+', '', item).strip()  
        numbers = [int(num) for num in item.split() if num.isdigit()]  
        result_dict[string].extend(numbers)
    return dict(result_dict)

# Function to get DataFrame of issues for a given topic
def issue_df(topic):
    issue1 = tor.loc[tor['Topic_Name'] == topic]
    review_str = convert_str(issue1)
    review_lst = common_issues(review_str)
    dic = extract_review(review_lst)

    covered_indices = set(index for indices in dic.values() for index in indices)
    all_indices = set(issue1['index'])
    remaining_indices = all_indices - covered_indices

    dfs = []
    for key, indices in dic.items():
        indices_with_reviews = [index for index in indices if index in issue1.index]
        df = pd.DataFrame({'key': [key] * len(indices_with_reviews),
                           'review': [issue1.loc[i, 'review'] for i in indices_with_reviews]})
        dfs.append(df)

    if remaining_indices:
        others_indices_with_reviews = [index for index in remaining_indices if index in issue1.index]
        others_df = pd.DataFrame({'key': ['Others'] * len(others_indices_with_reviews),
                                  'review': [issue1.loc[i, 'review'] for i in others_indices_with_reviews]})
        dfs.append(others_df)

    result_df = pd.concat(dfs, ignore_index=True)
    return result_df

# API endpoint for getting issues
@app.route('/api/issues', methods=['GET'])
def get_issues():
    topic = request.args.get('topic')
    if topic is None:
        return jsonify({"error": "Please provide a topic parameter"}), 400

    df = issue_df(topic)
    json_data = df.to_json(orient='records')
    return json_data

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
