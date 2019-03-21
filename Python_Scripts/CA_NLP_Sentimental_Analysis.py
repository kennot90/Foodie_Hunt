##This code is a simple implementation of the sentiment analysis using Vader



from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer


#initialize the MongoDB
from pymongo import MongoClient
client = MongoClient()
db = client['charles_ca']


restaurants_collection = db.restaurants
events_collection = db.events
customers_collection = db.customers
reviews = db.reviews

#Obtain the Sentiment Analysis
sid = SentimentIntensityAnalyzer()
for post in reviews.find().limit(4):
    text = (post['Text'])
    print(text)
    testimonial = TextBlob(text)
    print(testimonial.sentiment)
    print("#############################")
    ss = sid.polarity_scores(text)
    print(ss)
