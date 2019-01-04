import requests
import re
import time
from pymongo import MongoClient


def update_tags(ref, new_tag):
    print(ref)
    print(new_tag)
    events_test.update_one({'_id': ref}, {'$push': {'rest_ids': new_tag}})
    print("updated!")


def eventbrite_scrap(url, events, search, headerapi_key, location, latitude_term, lat, longtitude_term, long, end_date, start_date):
    data = {}
    data['event'] = []

    target = (url + events + search + headerapi_key + location
              + latitude_term + lat
              + longtitude_term + long + end_date + start_date)
    response = requests.get(target)
    z = response.json()
    page_count = z['pagination']['page_count']
    for page in range(0, int(page_count)):
        page_2 = page + 1
        target = (url + events + search + headerapi_key + location
                  + latitude_term + lat
                  + longtitude_term + long
                  + end_date + start_date +
                  "&page=" + str(page_2))

        response = requests.get(target)
        z = response.json()

        page_size = len(z["events"])

        for count in range(0, page_size):
            # print(count)
            if (z["events"][count]['online_event'] == False) and \
                    (z["events"][count]['category_id'] != str(120)) and \
                    (z["events"][count]['category_id'] != str(199)) and \
                    (z["events"][count]['category_id'] != str(114)) and \
                    (z["events"][count]['category_id'] != str(111)):

                if z["events"][count]["description"]["text"] is not None:
                    temp_dsc = re.sub(r'\r\n', '', z["events"][count]["description"]["text"])
                    temp_dsc = re.sub(r'\n', '', temp_dsc)
                    temp_dsc = re.sub(r'\r', '', temp_dsc)
                    temp_dsc = (temp_dsc.encode('ascii', 'ignore')).decode("utf-8")
                else:
                    temp_dsc = " "
                if z["events"][count]["name"]["text"] is not None:
                    temp_event = re.sub(r'\r\n', '', z["events"][count]["name"]["text"])
                    temp_event = re.sub(r'\n', '', temp_event)
                    temp_event = re.sub(r'\r', '', temp_event)
                    temp_event = (temp_event.encode('ascii', 'ignore')).decode("utf-8")
                else:
                    temp_event = " "

                cat = get_category_event(z["events"][count]["category_id"])

                data['event'].append({
                    "event_name": temp_event,
                    "_id": z["events"][count]["id"],
                    "start_date": z["events"][count]["start"]["utc"],
                    "end_date": z["events"][count]["end"]["utc"],
                    "time_zone": z["events"][count]["start"]["timezone"],
                    "is_free": z["events"][count]["is_free"],
                    "organizer_id": z["events"][count]["organizer_id"],
                    "venue_id": z["events"][count]["venue_id"],
                    "category_id": cat,
                    "url": z["events"][count]["url"],
                    "online_event": z["events"][count]["online_event"]
                })

    return data


def get_category_event(category_id):
    if (category_id == str(103)):
        result = "Music"
    elif (category_id == str(101)):
        result = "Business & Professional"
    elif (category_id == str(110)):
        result = "Food & Drink"
    elif (category_id == str(113)):
        result = "Community & Culture"
    elif (category_id == str(105)):
        result = "Performing & Visual Arts"
    elif (category_id == str(104)):
        result = "Film, Media & Entertainment"
    elif (category_id == str(108)):
        result = "Sports & Fitness"
    elif (category_id == str(107)):
        result = "Health & Wellness"
    elif (category_id == str(102)):
        result = "Science & Technology"
    elif (category_id == str(109)):
        result = "Travel & Outdoor"
    elif (category_id == str(111)):
        result = "Charity & Causes"
    elif (category_id == str(114)):
        result = "Religion & Spirituality"
    elif (category_id == str(115)):
        result = "Family & Education"
    elif (category_id == str(116)):
        result = "Seasonal & Holiday"
    elif (category_id == str(112)):
        result = "Government & Politics"
    elif (category_id == str(106)):
        result = "Fashion & Beauty"
    elif (category_id == str(117)):
        result = "Home & Lifestyle"
    elif (category_id == str(118)):
        result = "Auto, Boat & Air"
    elif (category_id == str(119)):
        result = "Hobbies & Special Interest"
    elif (category_id == str(120)):
        result = "School Activities"
    else:
        result = " "
    return result


headerapi_key = '/?token=W7IWZN265WQ23DVF5KM6'
events = '/events'
search = '/search'
url = 'https://www.eventbriteapi.com/v3'
singapore = '&location.address=Singapore&'
location = '&location.within=1km&'
latitude_term = 'location.latitude='
longtitude_term = '&location.longitude='
end_date = '&start_date.range_end=2018-12-31T23%3A59%3A59&'
start_date = '&start_date.range_start=2013-01-01T07%3A00%3A00'

client = MongoClient()
db = client['charles_ca']
restaurant_collection = db.restaurants
events_test =  db.events_test

rank = 0
name = ''
lat = 0.0
long = 0.0


for post in restaurant_collection.find({"$and": [{"Review_Count": {"$gte": 100, "$lte": 500}},
                                                 {'Address.Latitude': {'$ne': '#N/A'}}]}):
    rest_id = post['_id']
    name = post['Name']
    long = post['Address']['Longitude']
    lat = post['Address']['Latitude']

    data = eventbrite_scrap(url, events, search, headerapi_key, location, latitude_term, str(lat), longtitude_term, str(long), end_date, start_date)
    data_eventname = data['event']
    for event in data_eventname:
        event_id = event['_id']
        event['TimeStamp'] = int(time.time())

        # query for event
        mongo_event = events_test.find_one({"_id": event_id})
        if mongo_event is not None:
            # update
            update_tags(event_id, rest_id)
        else:
            event['rest_ids'] = []
            event['rest_ids'].append(rest_id)
            events_test.insert_one(event)

for post in restaurant_collection.find({"reviews_number_en": {"$gte": 100, "$lte": 500}}):
    rest_id = post['_id'] # change to "_id"
    name = post['restaurant_name']
    long = post['Longitude']
    lat = post['Latitude']
    
    data = eventbrite_scrap(url, events, search, headerapi_key,location,latitude_term,str(lat), longtitude_term, str(long), end_date, start_date)
    data_eventname = data['event']
    for event in data_eventname:
        event_id = event['event_id']
        event['_id'] = event_id
        event['TimeStamp'] = int(time.time())
        
        # query for event
        mongo_event = events_test.find_one({"_id": event_id})
        if mongo_event is not None:
            # update
            update_tags(event_id, rest_id)
        else:
            event['rest_ids'] = []
            event['rest_ids'].append(rest_id)
            events_test.insert_one(event)