#VADER

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

#nps_scoring
#vader function
#2. Output should be: nps_indiv, nps_category, topic (?) from the score_df ?

def nps_score(review) :
    vs = analyzer.polarity_scores(review)
    pos_score = vs['pos']
    neg_score = vs['neg']
    neu_score = vs['neu']
    comp_score = vs['compound']
    nps_indv = -1
    #mapping
    if -1 <= vs['compound'] <= -9/11:
        nps_indiv = 0
    elif -9/11 < vs['compound'] <= -7/11:
        nps_indiv = 1
    elif -7/11 < vs['compound'] <= -5/11:
        nps_indiv = 2
    elif -5/11 < vs['compound'] <= -3/11:
        nps_indiv = 3
    elif -3/11 < vs['compound'] <= -1/11:
        nps_indiv = 4
    elif -1/11 < vs['compound'] <= 1/11:
        nps_indiv = 5
    elif 1/11 < vs['compound'] <= 3/11:
        nps_indiv = 6
    elif 3/11 < vs['compound'] <= 5/11:
        nps_indiv = 7
    elif 5/11 < vs['compound'] <= 7/11:
        nps_indiv = 8
    elif 7/11 < vs['compound'] <= 9/11:
        nps_indiv = 9
    else:
        nps_indiv = 10
    return nps_indiv


#nps category
def nps_cat(review) :
    nps_indiv = nps_score(review)
    cat = ""
    if nps_indiv >= 9:  # Promoters
        cat = 'Promoter'
    elif nps_indiv >= 7:  # Passives
        cat = 'Passive'
    else:  # Detractors
        cat = 'Detractor'
    return cat

