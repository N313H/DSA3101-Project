#main attempt in constructing API
# libraries
from flask import Flask, jsonify, request
import mysql.connector
import pandas as pd
import json
import re
from h2ogpte import H2OGPTE
from flask_cors import CORS # type: ignore
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Initialize Flask app
app = Flask(__name__)

# Function to connect to MySQL
def connect_to_mysql():
    return mysql.connector.connect(
        host="db",
        user="root",
        password="pikapikachu",
        database="dsa3101",
        port=3306
    )

# Function to read JSON file
def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

# Establish MySQL connection and read data
db = connect_to_mysql()
my_data = pd.read_sql("SELECT * FROM dsa3101", db)
#returned data consist of 9 columns
#index,	dataFrom, date,	review, rating, extracted_devresp, devresp_time, Topic Number, Topic

#############################################################################################################################
## Configure H2OGPTE
API_KEY = "sk-ms7SU43E34tS9UJks5RD2KM3m1JumOR2pM73Dk95VzKjM6TZ"
REMOTE_ADDRESS = "https://h2ogpte.genai.h2o.ai"
client = H2OGPTE(address=REMOTE_ADDRESS, api_key=API_KEY)

#############################################################################################################################
#summary
# API endpoint for getting summary

# Function to convert DataFrame to string
def convert_str(topic_review):
    return ''.join(topic_review['review'].astype(str))


@app.route('/api/summary', methods=['GET'])
def get_summary():
    topic = request.args.get('topic') #front end request the topic, and we send the summary for thhat specific topic
    if topic is None:
        return jsonify({"error": "Please provide a topic parameter"}), 400

    # Assuming `tor` DataFrame is defined somewhere
    issue1 = my_data.loc[my_data['Topic'] == topic]
    review = convert_str(issue1)
    extract = client.extract_data(
        text_context_list=[review],
        prompt_extract="Recommend improvements based on the reviews. Ignore grammatical errors and awkward languages. Do not return the review numbers"
    )

    summaries = [re.sub('\W+',' ', s) for extract_list_item in extract.content for s in extract_list_item.split("\n")]
    
    return jsonify({"summaries": summaries})


#############################################################################################################################
#issue analysis, seperate reviews in each topics into issues

# Function to extract common issues from reviews using a string of reviews
def common_issues(review):
    extract = client.extract_data(
        text_context_list= [review],
        prompt_extract="Extract all the common issues faced by the application according to the reviews, as well as their corresponding index after the identified issues. Do not return positive. Strictly return in the following format, issues : indexes without additional information. Do not explain your output"
    )
    return [re.sub('\W+',' ', s) for extract_list_item in extract.content for s in extract_list_item.split("\n")]

# extract review and append numbers
def extract_review(issue_ind):
    result_dict = {}
    for item in issue_ind:
        string = re.sub(r'\d+', '', item).strip()  
        numbers = [int(num) for num in item.split() if num.isdigit()]  
        result_dict[string].extend(numbers)
    return dict(result_dict)

# Function to get DataFrame of issues for a given topic #specified by the front end
def issue_df(topic):
    issue1 = my_data.loc[my_data['Topic'] == topic]
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

    df = issue_df(topic) #return the df
    json_data = df.to_json(orient='records') #send the df to front end
    return json_data


#############################################################################################################################
#Vader score #dependent on the topic and issues? In which case, we should rerun the above and run through nps

def analyze_sentiment(topic_df):
    # Initialize the SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()

    # Initialize lists to store data
    review_texts = []
    positive_scores = []
    negative_scores = []
    neutral_scores = []
    compound_scores = []
    nps_indiv = []
    nps_category = []  # New column for NPS categories

    # Perform sentiment analysis and store scores in lists
    for review in topic_df['review']:
        vs = analyzer.polarity_scores(review)

        review_texts.append(review)
        positive_scores.append(vs['pos'])
        negative_scores.append(vs['neg'])
        neutral_scores.append(vs['neu'])
        compound_scores.append(vs['compound'])

        # Map compound scores to nps_indiv based on specified intervals
        if -1 <= vs['compound'] <= -9/11:
            nps_indiv.append(0)
        elif -9/11 < vs['compound'] <= -7/11:
            nps_indiv.append(1)
        elif -7/11 < vs['compound'] <= -5/11:
            nps_indiv.append(2)
        elif -5/11 < vs['compound'] <= -3/11:
            nps_indiv.append(3)
        elif -3/11 < vs['compound'] <= -1/11:
            nps_indiv.append(4)
        elif -1/11 < vs['compound'] <= 1/11:
            nps_indiv.append(5)
        elif 1/11 < vs['compound'] <= 3/11:
            nps_indiv.append(6)
        elif 3/11 < vs['compound'] <= 5/11:
            nps_indiv.append(7)
        elif 5/11 < vs['compound'] <= 7/11:
            nps_indiv.append(8)
        elif 7/11 < vs['compound'] <= 9/11:
            nps_indiv.append(9)
        else:
            nps_indiv.append(10)

        # Map nps_indiv scores to NPS categories
        if nps_indiv[-1] >= 9:  # Promoters
            nps_category.append('Promoter')
        elif nps_indiv[-1] >= 7:  # Passives
            nps_category.append('Passive')
        else:  # Detractors
            nps_category.append('Detractor')

    # Add sentiment scores and NPS categories to the DataFrame
    topic_df['positive_scores'] = positive_scores
    topic_df['negative_scores'] = negative_scores
    topic_df['neutral_scores'] = neutral_scores
    topic_df['compound_scores'] = compound_scores
    topic_df['nps_indiv'] = nps_indiv
    topic_df['nps_category'] = nps_category

    # Calculate Net Promoter Score (NPS) for each issue
    unique_keys = topic_df['key'].unique()
    issues_nps_scores = {}

    for key in unique_keys:
        key_df = topic_df[topic_df['key'] == key]
        label_counts = key_df['nps_category'].value_counts()

        promoter_count = label_counts.get('Promoter', 0)
        detractor_count = label_counts.get('Detractor', 0)
        passive_count = label_counts.get('Passive', 0)
        total_count = promoter_count + detractor_count + passive_count

        if total_count == 0:
            issues_nps_scores[key] = None
        else:
            nps = ((promoter_count - detractor_count) / total_count) * 100
            issues_nps_scores[key] = round(nps, 2)

    issuesNPS = pd.DataFrame(list(issues_nps_scores.items()), columns=['Issue', 'NPS'])
    
    # Calculate topic NPS
    label_counts = topic_df['nps_category'].value_counts()
    promoter_count = label_counts.get('Promoter', 0)
    detractor_count = label_counts.get('Detractor', 0)
    passive_count = label_counts.get('Passive', 0)
    total_count = promoter_count + detractor_count + passive_count

    # Calculate NPS
    if total_count == 0:
        topic_nps = None
    else:
        topic_nps = ((promoter_count - detractor_count) / total_count) * 100
    
    return topic_nps, issuesNPS


@app.route('/analyze', methods=['POST'])
def analyze():
    # Get the topic from the request
    topic = request.json.get('topic') #front end identify the topic nps they want
    #run topic through h20 to get the df for issues
    issue_df = issue_df(topic)

    # Perform sentiment analysis
    topic_nps, issuesNPS = analyze_sentiment(issue_df)
    
    # Convert DataFrame to dictionary
    issuesNPS_dict = issuesNPS.to_dict(orient='records')
    
    # Create JSON response
    response = {
        'topic_nps': topic_nps,
        'issuesNPS': issuesNPS_dict
    }
    
    return jsonify(response)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)