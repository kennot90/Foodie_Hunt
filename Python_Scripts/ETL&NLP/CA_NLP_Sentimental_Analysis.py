from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from pymongo import MongoClient
client = MongoClient()
db = client['charles_ca']
restaurants_collection = db.restaurants
events_collection = db.events
customers_collection = db.customers
reviews = db.reviews

sid = SentimentIntensityAnalyzer()
for post in reviews.find().limit(4):
    text = (post['Text'])
    print(text)
    testimonial = TextBlob(text)
    print(testimonial.sentiment)
    print("#############################")
    ss = sid.polarity_scores(text)
    print(ss)
