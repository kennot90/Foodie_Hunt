import pymongo
import datetime
import time


def etl_restaurants():
    # Restaurants
    dif = []
    rest = {}
    rating_details = {}
    add = {}
    meal = {}
    for restaurant in db_raw.restaurants.find({"reviews_number_en": {"$gte": 100, "$lte": 500}, 'TimeStamp': {'$gte': 1534600800}}):
        rest['subzone'] = ''
        rest['operating_hours'] = ''
        rest['establishment_type'] = ''
        rest['zomato_url'] = ''
        rest['zomato_cost'] = ''
        rest['zomato_votes'] = ''
        for zomato in db_raw.zomatos.find({"restaurant_id": restaurant["_id"]}):
            if (zomato["restaurant_subzone"].find(',') != -1):
                temp2 = []
                temp2 = zomato["restaurant_subzone"].split(",")
                rest['subzone'] = str(temp2[1]).strip()
            rest['operating_hours'] = zomato["hours"]
            rest['zomato_ratings'] = zomato["rating"]
            rest['establishment_type'] = zomato["establishment_type"]
            rest['zomato_url'] = zomato["restaurant_link"]
            rest['zomato_cost'] = zomato["cost"]
            rest['zomato_votes'] = zomato["votes"]

        for google_rating in db_raw.google_ratings.find({'restaurant_id': restaurant['_id']}):
            try:
                restaurant_google_rating = google_rating['restaurant_google_rating']
            except:
                restaurant_google_rating = 0
            try:
                restaurant_google_review_count = google_rating['restaurant_google_review_count']
            except:
                restaurant_google_review_count = 0
            try:
                restaurant_facebook_rating = google_rating['restaurant_facebook_rating']
            except:
                restaurant_facebook_rating = 0
            try:
                restaurant_hungrygowear_rating = google_rating['restaurant_hungrygowear_rating']
            except:
                restaurant_hungrygowear_rating = 0
            try:
                other_website_rating = google_rating['other_website_rating']
            except:
                other_website_rating = 0

            rest['restaurant_google_rating'] = restaurant_google_rating
            rest['restaurant_google_review_count'] = restaurant_google_review_count
            rest['restaurant_facebook_rating'] = restaurant_facebook_rating
            rest['restaurant_hungrygowear_rating'] = restaurant_hungrygowear_rating
            rest['other_website_rating'] = other_website_rating

        temp = []
        rest['_id'] = restaurant["_id"]
        rest['name'] = restaurant["restaurant_name"]
        rest['rank'] = restaurant["ranking"]
        rest['cuisine'] = restaurant["cuisine"]
        rest['ta_url'] = restaurant["url"]
        rest['ta_rating'] = restaurant["rating"]
        rest['review_count'] = restaurant["reviews_number"]
        rest['timestamp'] = restaurant["TimeStamp"]

        temp = restaurant["address"].split(",")
        add['street'] = temp[0]
        add['extended_add'] = temp[1]
        add['country'] = temp[2]
        add['postal_code'] = restaurant["Postal Code"]
        add['latitude'] = restaurant["Latitude"]
        add['longitude'] = restaurant["Longitude"]
        rest['address'] = add

        rating_details['atmosphere'] = restaurant["rating_atmosphere"]
        rating_details['food'] = restaurant["rating_food"]
        rating_details['service'] = restaurant["rating_service"]
        rating_details['value'] = restaurant["rating_value"]
        rest['rating_details'] = rating_details

        if str(restaurant['meal']).strip().find('Breakfast'):
            meal['breakfast'] = 'Y'
        else:
            meal['breakfast'] = ''
        if str(restaurant['meal']).strip().find('Lunch'):
            meal['lunch'] = 'Y'
        else:
            meal['lunch'] = ''
        if str(restaurant['meal']).strip().find('Dinner'):
            meal['dinner'] = 'Y'
        else:
            meal['dinner'] = ''
        if str(restaurant['meal']).strip().find('After-hours'):
            meal['after-hours'] = 'Y'
        else:
            meal['after-hours'] = ''
        if str(restaurant['meal']).strip().find('Drinks'):
            meal['drinks'] = 'Y'
        else:
            meal['drinks'] = ''
        if str(restaurant['meal']).strip().find('Brunch'):
            meal['brunch'] = 'Y'
        else:
            meal['brunch'] = ''
        rest['meal'] = meal
        rest['item'] = 1

        db_new.restaurants.insert_one(rest)


def etl_reviews_customers():
    # Reviews & Customers
    custs = []
    for review in db_raw.reviews.find({'TimeStamp': {'$gte': 1534600800}}):
        # Reviews
        json_reviews = {}
        json_reviews['restaurant_id'] = review['restaurant_id']
        customer_id = str(review['reviewer_level']).strip() if str(review['reviewer_level']).strip() != 'nan' else '0.0'
        json_reviews['customer_id'] = str(review['reviewer_name']).strip() + customer_id
        json_reviews['title'] = review['review_title']
        json_reviews['text'] = review['review_text']
        json_reviews['rating'] = review['review_rating']
        json_reviews['likes'] = review['likes_of_review']
        date = review['review_date']
        if date is not None and date != '':
            date = date.replace('-', ' ')
            date_time = datetime.datetime.strptime(date, '%d %b %y')
        json_reviews['date'] = date_time

        # Insert directly
        db_new.reviews.insert_one(json_reviews)

        # Customer
        json_cust = {}

        if str(review['reviewer_name']).strip() not in custs:
            if str(review['reviewer_name']).strip() == 'nan' or str(review['reviewer_name']).strip() == '':
                continue
            custs.append(str(review['reviewer_name']).strip())
            customer_id = str(review['reviewer_level']).strip() if str(review['reviewer_level']).strip() != 'nan' else '0.0'
            json_cust['_id'] = str(review['reviewer_name']).strip() + customer_id
            json_cust['name'] = review['reviewer_name']
            json_cust['country'] = review['reviewer_country'] if review['reviewer_country'] != 'nan' else ''
            json_cust['level'] = review['reviewer_level'] if review['reviewer_level'] != 'nan' else ''
            json_cust['number_of_reviews'] = review['number_of_reviews'] if review['number_of_reviews'] != 'nan' else ''
            json_cust['traval_type'] = review['reviewer_travel_type'] if review['reviewer_travel_type'] != 'nan' else ''
            join_date = review['reviewer_join_date'] if review['reviewer_join_date'] != 'nan' else ''
            json_cust['join_date'] = join_date.split('Since')[1].strip() if len(join_date.split('Since')) >= 2 else ''
            json_cust['age_group'] = review['reviewer_age_group'] if review['reviewer_age_group'] != 'nan' else ''
            json_cust['timestamp'] = review["TimeStamp"]

            # Update or Insert
            cursor_new = db_new.customers.find({'_id': json_cust['_id']})
            if len(list(cursor_new)) > 0:
                db_new.customers.update({'_id': json_cust['_id']}, {'$set': {'name': json_cust['name'], 'country': json_cust['country'], 'level': json_cust['level'], 'number_of_reviews': json_cust['number_of_reviews'], 'traval_type': json_cust['traval_type'], 'join_date': json_cust['Join_Date'], 'age_group': json_cust['age_group']}})
            else:
                db_new.customers.insert_one(json_cust)


def etl_events():
    # Events
    for event in db_raw.events.find({'TimeStamp': {'$gte': 1534600800}}):
        # Events
        json_events = {}
        json_events['_id'] = event['_id']
        json_events['event_name'] = event['event_name']
        json_events['start_date'] = datetime.datetime.strptime(event['start_date'], '%Y-%m-%dT%H:%M:%SZ')
        json_events['end_date'] = datetime.datetime.strptime(event['end_date'], '%Y-%m-%dT%H:%M:%SZ')
        json_events['time_zone'] = event['time_zone']
        json_events['is_free'] = event['is_free']
        json_events['organizer_id'] = event['organizer_id']
        json_events['venue_id'] = event['venue_id']
        json_events['category_id'] = event['category_id']
        json_events['url'] = event['url']
        json_events['online_event'] = event['online_event']
        json_events['TimeStamp'] = event['TimeStamp']
        json_events['rest_ids'] = event['rest_ids']
        json_events['timestamp'] = event["TimeStamp"]

        # Insert directly
        db_new.events.insert_one(json_events)


if __name__ == '__main__':
    # Read data from Raw MongoDB
    client_raw = pymongo.MongoClient('localhost', 27016)
    client_new = pymongo.MongoClient('localhost', 27017)
    db_raw = client_raw.FoodieHunt
    # Input data into new MongoDB
    db_new = client_new.FoodieHunt
    # Restaurants
    etl_restaurants()
    # Reviews & Customers
    etl_reviews_customers()
    # Events
    etl_events()

    # db_new.restaurants.create_index([("rank", pymongo.DESCENDING)], unique=True)

    # db_new.reviews.create_index([("restaurant_id", pymongo.DESCENDING), ("customer_id", pymongo.DESCENDING)], unique=True)

    # db_new.events.create_index([("_id", pymongo.DESCENDING), ("rest_ids", pymongo.ASCENDING)], unique=True)
