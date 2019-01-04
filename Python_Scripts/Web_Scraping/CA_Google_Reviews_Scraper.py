from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pymongo
import xlrd
import random
import time

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)

def convert(s):
    try:
        return round(float(s),2)
    except ValueError:
        try:
            num, denom = s.split('/')
            return float(num)
        except:
            return 0.0

def get_google_reviews(url):
    json_doc = {}
    driver.get(url)
    time.sleep(random.randint(1, 5))
    try:
        review_link = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/div/div/span[1]")
        print(review_link.text)
        json_doc['restaurant_google_rating'] = float(review_link.text)

        reviews_count = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/div/div/span[2]/span/a/span")
        json_doc['restaurant_google_review_count'] = float(reviews_count.text.replace('Google reviews','').strip())
    except:
        return json_doc
    try:
        peer_review_1_name = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[7]/div[2]/div/a[1]/span[1]")
        peer_review_1_rating = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[7]/div[2]/div/a[1]/span[2]")
        #peer_review_1_vote = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[7]/div[2]/div/a[1]/span[3]")
        if peer_review_1_name and peer_review_1_rating:
            print(peer_review_1_name.text)
            print(peer_review_1_rating.text)
            if peer_review_1_rating.text == 'Facebook':
                json_doc['restaurant_facebook_rating'] = convert(peer_review_1_name.text)
            elif peer_review_1_rating.text == 'HungryGoWhere':
                json_doc['restaurant_hungrygowear_rating'] = convert(peer_review_1_name.text)
            else:
                json_doc['other_website_rating'] = convert(peer_review_1_name.text)

    except:
        print("could not obtain rating..ignoring.")

    try:
        peer_review_2_name = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[7]/div[2]/div/a[2]/span[1]")
        peer_review_2_rating = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[7]/div[2]/div/a[2]/span[2]")
        #peer_review_2_vote = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[7]/div[2]/div/a[2]/span[3]")
        if peer_review_2_name and peer_review_2_rating:
            print(peer_review_2_name.text)
            print(peer_review_2_rating.text)
            if peer_review_2_rating.text == 'Facebook':
                json_doc['restaurant_facebook_rating'] = convert(peer_review_2_name.text)
            elif peer_review_2_rating.text == 'HungryGoWhere':
                json_doc['restaurant_hungrygowear_rating'] = convert(peer_review_2_name.text)
            else:
                json_doc['other_website_rating'] = convert(peer_review_2_name.text)
    except:
        print("could not obtain rating..ignoring.")

    try:
        peer_review_3_name = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[7]/div[2]/div/a[3]/span[2]")
        peer_review_3_rating = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[7]/div[2]/div/a[3]/span[2]")
        #peer_review_3_vote = driver.find_element_by_xpath("//*[@id=\"rhs_block\"]/div/div[1]/div/div[1]/div[2]/div[7]/div[2]/div/a[3]/span[3]")
        if peer_review_3_name and peer_review_3_rating:
            print(peer_review_3_name.text)
            print(peer_review_3_rating.text)
            if peer_review_3_rating.text == 'Facebook':
                json_doc['restaurant_facebook_rating'] = convert(peer_review_3_name.text)
            elif peer_review_3_rating.text == 'HungryGoWhere':
                json_doc['restaurant_hungrygowear_rating'] = convert(peer_review_3_name.text)
            else:
                json_doc['other_website_rating'] = convert(peer_review_3_name.text)
    except:
        print("could not obtain rating..ignoring.")

    return json_doc

def generate_url(restaurant_name, address):
    url = main_path + restaurant_name + address
    print("scraping: " + url)
    return url


# Read local restaurant from mongo collection

main_path = 'https://www.google.com.sg/search?q='

connection = pymongo.MongoClient('localhost', 27017)
db = connection.cadb_raw
rest_record = db.restaurants
google_record = db.google_ratings


for restaurant in rest_record.find({"reviews_number_en": {"$gte": 100, "$lte": 500}, 'TimeStamp': {'$gte': 1534600800}}):
    print(restaurant)
    restaurant_ranks = restaurant['ranking']
    rest_id = restaurant['_id']
    name = restaurant['restaurant_name']

    address = restaurant['address']
    address = address.rsplit(',', 3)[1]  # to get 'singapore' + zipcode

    url = generate_url(name, address)
    json_doc = get_google_reviews(url)
    json_doc['address'] = address
    json_doc['restaurant_rank'] = restaurant_ranks
    json_doc['restaurant_name'] = name
    json_doc['restaurant_id'] = rest_id

    google_record.insert(json_doc)

driver.close()
