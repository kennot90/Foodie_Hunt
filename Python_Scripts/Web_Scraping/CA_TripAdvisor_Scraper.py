import requests
from bs4 import BeautifulSoup
import re
import time
import json
import pymongo


def get_parser(url):
    # BS4 to get the html structure
    try:
        print(url)
        html_page = requests.get(url, timeout=3)
        while html_page.status_code != 200 and html_page.status_code != 404:
            time.sleep(1)
            html_page = requests.get(url, timeout=3)
        soup_page = BeautifulSoup(html_page.content, 'html.parser')
        return soup_page
    except:
        return None


def scrap_restaurant_details(url):
    # Get reviews of the first page
    soup_page = get_parser(url)
    time.sleep(1)

    # Restaurant Name & url
    heading_title = soup_page.find('h1', {'class': 'heading_title'})
    name = heading_title.text if heading_title is not None else ''

    # Ranking
    header_popularity = soup_page.find('span', {'class': 'header_popularity popIndexValidation'})
    ranking = header_popularity.find('span').text if header_popularity is not None and header_popularity.find('span') is not None else ''

    # Address
    address = ''
    street_adress = soup_page.find('span', {'class': 'street-address'})
    address = address + street_adress.text + ', ' if street_adress is not None else address
    extended_adress = soup_page.find('span', {'class': 'extended-address'})
    address = address + extended_adress.text + ', ' if extended_adress is not None else address
    locality = soup_page.find('span', {'class': 'locality'})
    address = address + locality.text + ', ' if locality is not None else address
    country_name = soup_page.find('span', {'class': 'country-name'})
    address = address + country_name.text if country_name is not None else address

    # Postal Code
    postal_code = address.split('Singapore ')[1] if len(address.split('Singapore ')) > 1 else ''
    if postal_code != '':
        postal_code = postal_code.split(',')[0]

    # Rating
    rating = ''
    if soup_page.find('span', {'class': 'ui_bubble_rating bubble_50'}) is not None:
        rating = '5'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_40'}) is not None:
        rating = '4'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_30'}) is not None:
        rating = '3'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_20'}) is not None:
        rating = '2'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_10'}) is not None:
        rating = '1'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_45'}) is not None:
        rating = '4.5'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_35'}) is not None:
        rating = '3.5'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_25'}) is not None:
        rating = '2.5'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_15'}) is not None:
        rating = '1.5'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_05'}) is not None:
        rating = '0.5'
    elif soup_page.find('span', {'class': 'ui_bubble_rating bubble_00'}) is not None:
        rating = '0'

    # Rating summary
    rating_food = ''
    rating_service = ''
    rating_value = ''
    rating_atmosphere = ''
    rating_summary = soup_page.find('div', {'class': 'ratingSummary wrap'})
    rating_row = rating_summary.findAll('div', {'class': 'ratingRow wrap'}) if rating_summary is not None else None

    if rating_row is not None:
        for row in rating_row:
            label_part = row.find('div', {'class': 'label part '})
            rating = row.find('div', {'class': 'wrap row part '})
            if label_part is not None and rating is not None:
                if label_part.text.strip() == 'Food':
                    rating_food = str(rating.find('span')['alt']).split(' ')[0] if rating.find('span') is not None else ''
                elif label_part.text.strip() == 'Service':
                    rating_service = str(rating.find('span')['alt']).split(' ')[0] if rating.find('span') is not None else ''
                elif label_part.text.strip() == 'Value':
                    rating_value = str(rating.find('span')['alt']).split(' ')[0] if rating.find('span') is not None else ''
                elif label_part.text.strip() == 'Atmosphere':
                    rating_atmosphere = str(rating.find('span')['alt']).split(' ')[0] if rating.find('span') is not None else None

    # Cuisine
    cuisines_title = soup_page.find('div', {'class': 'ui_column is-6 cuisines'})
    cuisines_text = cuisines_title.find('div', {'class': 'text'}) if cuisines_title is not None else None
    cuisine = cuisines_text.text.strip() if cuisines_text is not None else ''

    # Prices
    price_title = soup_page.find('span', {'class': 'ui_column is-6 price'})
    prices_text = price_title.find('span', {'class': 'text'}) if price_title is not None else None
    price = prices_text.text if prices_text is not None else None

    # Meals
    meal = ''
    table_section = soup_page.find('div', {'class': 'table_section'})
    titles = table_section.findAll('div', {'class': 'title'}) if table_section is not None else None
    contents = table_section.findAll('div', {'class': 'content'}) if table_section is not None else None
    for i in range(len(titles)):
        if titles[i] is not None and contents[i] is not None and titles[i].text.strip() == 'Meals':
            meal = contents[i].text

    # Reviews number
    all_reviews = soup_page.find('a', {'class': 'seeAllReviews'})
    reviews = all_reviews.text if all_reviews is not None else None
    review_num = int(reviews.split(' ')[0]) if reviews is not None else ''

    pagination = soup_page.find('p', {'class': 'pagination-details'})
    reviews = pagination.text if pagination is not None else None
    reviews = re.split('of | reviews', reviews)[1] if reviews is not None else None
    review_num_en = int(reviews.replace(',', '')) if reviews is not None else ''

    # Latitude & Longitude
    latitude, longitude = scrap_latitude_longitude(postal_code)

    json = {}
    json['_id'] = url.split('Restaurant_Review-')[1].split('-Reviews')[0]
    json['postal_code'] = postal_code
    json['latitude'] = latitude
    json['longitude'] = longitude
    json['restaurant_name'] = name
    json['url'] = url
    json['ranking'] = ranking
    json['address'] = address
    json['rating'] = rating
    json['rating_food'] = rating_food
    json['rating_service'] = rating_service
    json['rating_value'] = rating_value
    json['rating_atmosphere'] = rating_atmosphere
    json['cuisine'] = cuisine
    json['prices'] = price
    json['meal'] = meal
    json['reviews_number'] = review_num
    json['reviews_number_en'] = review_num_en
    json['TimeStamp'] = int(time.time())

    # Insert directly
    db_raw.restaurants.insert_one(json)
    return soup_page


def scrap_latitude_longitude(postal_code):
    target = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(postal_code) + '&returnGeom=Y&getAddrDetails=Y&pageNum=1'

    response = requests.get(target)
    z = response.json()
    if z['found'] != 0:
        longtitude = z['results'][0]['LONGITUDE']
        latitude = z['results'][0]['LATITUDE']
    else:
        longtitude = ''
        latitude = ''

    return longtitude, latitude


def scrap_restaurant_reviews(rest_id, dynamic_url, soup_page):
    # Restaurant Name & url
    heading_title = soup_page.find('h1', {'class': 'heading_title'})
    rest_name = heading_title.text if heading_title is not None else ''

    # Ranking
    header_popularity = soup_page.find('span', {'class': 'header_popularity popIndexValidation'})
    rest_rank = header_popularity.find('span').text if header_popularity is not None and header_popularity.find('span') is not None else ''

    # Get reviews of the first page
    print('page = {}'.format('0'))
    scrap_reviews_lists(rest_id, rest_rank, rest_name, soup_page)

    # Get total numbers of reviews
    total_reviews = soup_page.find('p', {'class': 'pagination-details'}).text if soup_page is not None and soup_page.find('p', {'class': 'pagination-details'}) is not None else ''
    if total_reviews == '':
        return False
    total_reviews = re.split('of | reviews', total_reviews)[1]
    total_reviews = int(total_reviews.replace(',', ''))

    # Get reviews of other pages
    for page in range(0, total_reviews, 10):
        if page == 0:
            continue

        print('page = {}'.format(page))
        page_url = dynamic_url.format(page)
        soup_page = get_parser(page_url)
        time.sleep(1)
        while soup_page is None:
            soup_page = get_parser(page_url)
            time.sleep(1)

        scrap_reviews_lists(rest_id, rest_rank, rest_name, soup_page)


def scrap_reviews_lists(rest_id, rest_rank, rest_name, soup_page):
    containers = soup_page.findAll('div', {'class': 'review-container'}) if soup_page is not None else None

    if containers is not None:
        for con in containers:
            json = {}
            # Review Details
            quote = con.find('div', {'class': 'quote'})
            href = main_path + quote.find('a').get('href') if quote is not None else None
            json = scrap_reviews_details(href)

            # Reviewers
            member_info = con.find('div', {'class': 'member_info'})
            uid = member_info.find('div').get('id') if member_info is not None else ''
            uid = re.split('UID_|-SRC', uid)[1] if len(re.split('UID_|-SRC', uid)) > 2 else ''
            if uid == '':
                continue

            href = main_path + '//MemberOverlay?Mode=owa&uid=' + uid
            scrap_reviews_reviewers(href)

            json['RestaurantID'] = rest_id
            json['Rank'] = rest_rank
            json['Restaurant Name'] = rest_name
            json['TimeStamp'] = int(time.time())
            # Insert directly
            db_raw.reviews.insert_one(json)


def scrap_reviews_details(url):
    # Get reviews of the first page
    soup_page = get_parser(url)
    time.sleep(1)
    while soup_page is None:
        soup_page = get_parser(url)
        time.sleep(1)

    reviews = soup_page.find('div', {'class': 'review hsx_review ui_columns is-multiline is-mobile inlineReviewUpdate provider0'}) if soup_page is not None else None

    # Review Title
    no_quotes = reviews.find('span', {'class': 'noQuotes'}) if reviews is not None else None
    review_title = no_quotes.text if no_quotes is not None else ''

    # Reviewer
    scrname = reviews.find('span', {'class': 'expand_inline scrname'}) if reviews is not None else None
    review_reviewer = scrname.text if scrname is not None else ''

    # Review Text
    partial_entry = reviews.find('p', {'class': 'partial_entry'}) if reviews is not None else None
    review_text = partial_entry.text if partial_entry is not None else ''

    # Review Rating
    rating = reviews.find('div', {'class': 'rating reviewItemInline'}) if reviews is not None else None
    rating_class = rating.find('span').get('class')[1] if rating is not None else None
    review_rating = int(rating_class.split('_')[1]) / 10 if rating_class is not None else ''

    # Like of review
    badge_text = reviews.findAll('span', {'class': 'badgetext'}) if reviews is not None else None
    review_like = badge_text[1].text if badge_text is not None and len(badge_text) == 2 else ''

    # Review Date
    relative_date = rating.find('span', {'class': 'ratingDate relativeDate'}) if rating is not None else None
    review_date = relative_date.get('title') if relative_date is not None else ''

    json['review_title'] = review_title
    json['reviewer'] = review_reviewer
    json['review_text'] = review_text
    json['review_rating'] = review_rating
    json['likes_of_review'] = review_like
    json['review_date'] = review_date
    return json


def scrap_reviews_reviewers(url):
    # Get reviews of the first page
    soup_page = get_parser(url)
    time.sleep(1)
    while soup_page is None:
        soup_page = get_parser(url)
        time.sleep(1)

    # Name
    name = soup_page.find('h3', {'class': 'username reviewsEnhancements'}) if soup_page is not None else None
    name = name.text if name is not None else ''

    # Country & Join Date & Age Group
    description = soup_page.find('ul', {'class': 'memberdescriptionReviewEnhancements'}) if soup_page is not None else None
    lis = description.findAll('li') if description is not None else None
    if lis is not None and len(lis) > 1:
        join_date = lis[0].text.split('since')[1] if lis[0] is not None else ''
    if lis is not None and len(lis) > 2:
        age_group = lis[1].text.split('from')[0] if lis[1] is not None else ''
        country = lis[1].text.split('from')[1] if lis[1] is not None else ''

    # Level Contributor
    level_info = soup_page.find('div', {'class': 'badgeinfo'}) if soup_page is not None else None
    level = level_info.find('span').text if level_info is not None and level_info.find('span') is not None else ''

    # No of Reviews
    badge_text = soup_page.find('span', {'class': 'badgeTextReviewEnhancements'}) if soup_page is not None else None
    no_review = badge_text.text.split(' ')[0] if badge_text is not None else ''

    # Travel Type
    member_tags = soup_page.findAll('ul', {'class': 'memberTagsReviewEnhancements'}) if soup_page is not None else None
    travel_type = ''
    if member_tags is not None:
        for tag in member_tags:
            travel_type = travel_type + tag.text + ',' if tag is not None else travel_type
    travel_type = travel_type[:len(travel_type) - 1] if travel_type != '' and len(travel_type) > 0 else travel_type

    json['reviewer_name'] = name
    json['reviewer_country'] = country
    json['reviewer_level'] = level
    json['number_of_reviews'] = no_review
    json['reviewer_travel_type'] = travel_type
    json['reviewer_join_date'] = join_date
    json['reviewer_age_group'] = age_group
    return json


if __name__ == '__main__':
    main_path = 'https://www.tripadvisor.com.sg'

    # Connect to Raw MongoDB
    client = pymongo.MongoClient('localhost', 27017)
    db_raw = client.cadb_raw

    for i in range(0, 10):
        print('Current page = {}'.format(i))
        y = str(i * 30)
        url = main_path + '//RestaurantSearch-g294265-oa' + y + '-Singapore.html#EATERY_LIST_CONTENTS'

        # Get restaurant from list
        soup_page = get_parser(url)
        time.sleep(1)

        count = 1
        containers = soup_page.findAll('div', {'class': 'ui_column is-9 shortSellDetails'})
        for x in containers:
            print('The number of restaurant = {}'.format(count))
            count = count + 1
            # URL
            rest_url = x.find('a',{'class':'property_title'})['href']
            if rest_url is None or rest_url == '':
                continue

            print('Restaurant URL = {}'.format(rest_url))
            # Get restaurant details
            soup_page = scrap_restaurant_details(rest_url)

            # Get reviews details
            rest_id = rest_url.split('Restaurant_Review-')[1].split('-Reviews')[0]
            dynamic_url = main_path + rest_url.split('Reviews')[0] + 'or{}' + rest_url.split('Reviews')[1]
            scrap_restaurant_reviews(rest_id, dynamic_url, soup_page)