
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup as soup
import pandas as pd
import numpy as np


# In[ ]:


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
url = "https://www.zomato.com/singapore/restaurants?page=1"
html_page = requests.get(url,headers=headers)


# In[ ]:


soup_page = soup(html_page.content, "html.parser")


# # Fields To Be Scraped

# In[ ]:


df_restaurant = pd.DataFrame(columns=['restaurant_name',
                           'restaurant_link',
                           'restaurant_subzone',
                           'restaurant_address',
                           'cuisines',
                           'cost',
                           'rating',
                           'votes',
                           'hours',
                           'establishment_type'])

#df_subzones = pd.DataFrame(columns=['subzone',
#                           'subzone_link'])


# In[ ]:


rest_list_container = soup_page.findAll('div',{'class':'search-snippet-card'})


# In[ ]:


print(len(rest_list_container))


# In[ ]:


#establishement type
establishment_type = rest_list_container[0].find('div',{'class':'res-snippet-small-establishment'}).text
#print(establishment_type)

#establishement link
establishment_link = rest_list_container[0].find('div',{'class':'res-snippet-small-establishment'}).find('a').get('href')
#print(establishment_link)

#restaurant name
restaurant_name = rest_list_container[0].find('a',{'class':'result-title'}).text.strip()
#print(restaurant_name)

#restaurant_link
restaurant_link = rest_list_container[0].find('a',{'class':'result-title'}).get('href')
#print(restaurant_link)

#restaurant_subzone
restaurant_subzone = rest_list_container[0].find('a',{'class':'search_result_subzone'}).text
#print(restaurant_subzone)

#restaurant_subzone_link
restaurant_subzone_link = rest_list_container[0].find('a',{'class':'search_result_subzone'}).get('href')
#print(restaurant_subzone_link)

#restaurant_address
restaurant_address = rest_list_container[0].find('div',{'class':'search-result-address'}).text.strip()
#print(restaurant_address)

####more details
restaurant_details = rest_list_container[0].find('div',{'class':'search-page-text'})
#print(len(restaurant_details))

#cuisines
cuisines = restaurant_details.find('div').findAll('a')
cuisines_string = restaurant_details.find('div').text.split(": ")[1]
#print(cuisines_string)
# for cuisine in cuisines:
#     print(cuisine.text)
    
#cost
cost = restaurant_details.find('span',{'itemprop':'priceRange'}).findAll('span')
#print("Price : ",len(cost),"/ 4")

#hours
hours = restaurant_details.find('div',{'class':'res-timing'}).find('div')
#print(hours.text.strip())

#rating
rating = float(rest_list_container[0].find('div',{'class':'rating-popup'}).text.strip())
#print(rating)

#votes
votes = int(rest_list_container[0].find('div',{'class':'search_result_rating'}).find('span').text.split(" ")[0])
#print(votes)

s = pd.Series({'restaurant_name': restaurant_name,
               'restaurant_link':restaurant_link,
               'restaurant_subzone':restaurant_subzone,
               'restaurant_address':restaurant_address,
               'cuisines':cuisines_string,
               'cost':len(cost),
               'rating':rating,
               'votes':votes,
               'hours':hours.text.strip(),
               'establishment_type':establishment_type})

print(s)

df_restaurant = df_restaurant.append(s, ignore_index=True)


# # Multiple Pages

# In[ ]:


import requests
from bs4 import BeautifulSoup as soup
import pandas as pd
import numpy as np
import time
import re

# Create a Pandas dataframe from some data.
#df = pd.DataFrame({'Data': [10, 20, 30, 20, 15, 30, 45]})

# Create a Pandas Excel writer using XlsxWriter as the engine.
#writer = pd.ExcelWriter('ZomatoScraped.xlsx', engine='xlsxwriter')


# In[ ]:


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


# In[ ]:


df_restaurant = pd.DataFrame(columns=['restaurant_name',
                                        'restaurant_link',
                                        'restaurant_subzone',
                                        'restaurant_address',
                                        'postal_code',
                                        'cuisines',
                                        'cost',
                                        'rating',
                                        'votes',
                                        'hours',
                                        'establishment_type'])


# In[ ]:



for i in range(501,575):
    time.sleep(2)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    url = "https://www.zomato.com/singapore/restaurants?page=" + str(i)
    html_page = requests.get(url,headers=headers)
    soup_page = soup(html_page.content, "html.parser")
    
    print(url)
    
    rest_list_container = soup_page.findAll('div',{'class':'search-snippet-card'})
    
    for j in range(0,len(rest_list_container)):
        
        restaurant = rest_list_container[j]
        
        #establishement type
        establishment_type =""
        if restaurant.find('div',{'class':'res-snippet-small-establishment'}) is not None:
            establishment_type = restaurant.find('div',{'class':'res-snippet-small-establishment'}).text

        #establishement link
        establishment_link =""
        if restaurant.find('div',{'class':'res-snippet-small-establishment'}) is not None:
            establishment_link = restaurant.find('div',{'class':'res-snippet-small-establishment'}).find('a').get('href')

        #restaurant name
        restaurant_name =""
        if restaurant.find('a',{'class':'result-title'}) is not None:
            restaurant_name = restaurant.find('a',{'class':'result-title'}).text.strip()

        #restaurant_link
        restaurant_link =""
        if restaurant.find('a',{'class':'result-title'}).get('href') is not None:
            restaurant_link = restaurant.find('a',{'class':'result-title'}).get('href')

        #restaurant_subzone
        restaurant_subzone =""
        if restaurant.find('a',{'class':'search_result_subzone'}) is not None:
            restaurant_subzone = restaurant.find('a',{'class':'search_result_subzone'}).text

        #restaurant_subzone_link
        restaurant_subzone_link =""
        if restaurant.find('a',{'class':'search_result_subzone'}) is not None:
            restaurant_subzone_link = restaurant.find('a',{'class':'search_result_subzone'}).get('href')

        #restaurant_address
        restaurant_address =""
        if restaurant.find('div',{'class':'search-result-address'}) is not None:
            restaurant_address = restaurant.find('div',{'class':'search-result-address'}).text.strip()
        
        # postal code
        postal_code = ""
        if len(re.findall(r'(\d{6})', restaurant_address)) != 0:
            postal_code = re.findall(r'(\d{6})', restaurant_address)[0]

        ####more details 
        restaurant_details =""
        if restaurant.find('div',{'class':'search-page-text'}) is not None:
            restaurant_details = restaurant.find('div',{'class':'search-page-text'})

        #cuisines
        cuisines =""
        cuisines_string =""
        if restaurant_details.find('div').findAll('a') is not None:
            cuisines = restaurant_details.find('div').findAll('a')
            cuisines_string = restaurant_details.find('div').text.split(": ")[1]        
        
        #cost
        cost =""
        if restaurant_details.find('span',{'itemprop':'priceRange'}) is not None:
            cost = restaurant_details.find('span',{'itemprop':'priceRange'}).findAll('span')

        #hours
        hours =""
        if restaurant_details.find('div',{'class':'res-timing'}) is not None:
            hours = restaurant_details.find('div',{'class':'res-timing'}).find('div').text.strip()

        #rating
        rating =""
        if restaurant.find('div',{'class':'rating-popup'}) is not None:
            if(isfloat(restaurant.find('div',{'class':'rating-popup'}).text.strip())):
                rating = float(restaurant.find('div',{'class':'rating-popup'}).text.strip())

        #votes
        votes =""
        if restaurant.find('div',{'class':'search_result_rating'}).find('span') is not None:
            votes = int(restaurant.find('div',{'class':'search_result_rating'}).find('span').text.split(" ")[0])

        s = pd.Series({'restaurant_name': restaurant_name,
                       'restaurant_link':restaurant_link,
                       'restaurant_subzone':restaurant_subzone,
                       'restaurant_address':restaurant_address,
                       'postal_code':postal_code,
                       'cuisines':cuisines_string,
                       'cost':len(cost),
                       'rating':rating,
                       'votes':votes,
                       'hours':hours,
                       'establishment_type':establishment_type})

        print(j)
        df_restaurant = df_restaurant.append(s, ignore_index=True)
    
    print(i) 
        


# In[ ]:


df_restaurant


# In[ ]:


# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('ZomatoScraped_501-575.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df_restaurant.to_excel(writer, sheet_name='Sheet2')

# Close the Pandas Excel writer and output the Excel file.
writer.save()


# In[ ]:


import re
s ='25 Scotts Road, Level Royal Plaza 228220'
re.findall(r'(\d{6})', s)[0]

