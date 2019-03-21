# Foodie_Hunt

## 0.TLDR (If you are not interested in reading the report below.)

This report is done by a team of 4 focusing on 
Data Source, Data Acquisition, Data Management and Business Intelligence (BI). 

Roles I had done

I had scraped EventBrite API to obtain the events around Singapore based ont the Date, Lontitude and Latitude. 
After which, I had done a mapredeuce to aggregate the results based on the restaurants scraped by my teammates through Zomato and Tripadvisor.

The lontitude and Latitude are obtain via ONEMAP SG. 

After which, I connect the MongoDB via a connector to Tableau and working on the visualizing the results which can be seen in the TWB file.


## 1.INTRODUCTION
Singapore has a diverse population and presents a unique massing of different cultures from all over the world, each contributing their style to the world of food. For Singaporeans, it has become a national pastime to venture out to the different corners of the island to discover the best food. This well-known trademark has also inspired the world travelers around the world to come to Singapore to experience these delicacies. We aim to assist these travelers to find the best food in Singapore.


## 2.	BUSINESS UNDERSTANDING
### 2.1	Business Goals
The following are our business goals:
•	Finding the best restaurants to eat in Singapore, based on 
o	Cuisine
o	Nationality
•	Sentiment Analysis on Restaurant Reviews
•	Restaurants rating comparison across different website
•	Filtering down to a restaurant near a public event
2.2	Business Questions
There are several questions we want to ask to satisfy our business goals, such as:
•	What is the trend of sentiment analytics of reviews across restaurants ranking?
•	What is the rating of the restaurant across different website?
•	Which are the nearby restaurants of a public event?
•	What is the reviewer contributor trends?
### 3.	OVERALL ARCHITECTURE
 
 ![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/0.png)
Figure – 1 Overall Architecture of Data Pipeline

The system architecture shows the overall architecture of our data pipeline and analysis model. It is broadly classified into 4 tiers - Data Source, Data Acquisition, Data Management and Business Intelligence (BI). 
Due to the requirements and computational flexibility requirement for our project, MongoDB, a document datastore is used for persistence.
The raw data scrapped from different websites are first loaded into the staging database. In consideration of both initial data and delta updates from these websites, we have included a check timestamp to identify the latest data. In the initial run, all data is scraped; in the subsequent runs, a scheduler initiates scripts to run and load the updates. The collected data is inserted into different collections in the staging database. For each collection, we have designed schemas and archiving strategies to optimize the whole process.
In the tradition of designing NoSQL solutions, ELTL (Extract-Load-Transform-Load) strategy is followed to load the extracted data again from the staging database and transform to suitable format (MapReduce scripts to restructure our collections) and load into our production database, which is in the data management layer. To improve the scalability, availability and manageability of our database, we have config server, proxy instance and replica set in this layer to simulate our sharding strategy. For the replica set, we used the minimum configuration which contains one primary replicate that can accept write operations and two secondary replicates that can process read operations. Simple NLP analysis has been done for the reviews text data, to get some insights from more than 130 thousand lines of records. Tableau is used as the business intelligence tool to visualize the data and explore the meaningful insights. 
## 4.	DATA SOURCES AND ASSUMPTIONS
### 4.1 Data Sources
There are five websites’ data in our data source layer, which are TripAdvisor, OneMap, EventBrite, Zomato and Google Reviews.
TripAdvisor is our primary source of data as it is the largest English Travel website in the world. In Singapore alone, we found over 10K restaurants and 338 hotels. The current count of restaurant reviews right now stands at 440K. TripAdvisor holds a significant amount of information that will be useful for analysis and insight discovery. We also scraped ratings from Google Reviews and Zomato to have a more diverse set of user ratings. The restaurant data from TripAdvisor is further enriched with additional data from Zomato.
The events in Eventbrite allows us to capture the happenings around Singapore around the year. The aim is to investigate the relationship of having events around the area might increase the number of customers in the food and beverage sectors around the location which in turn boost the number of reviews.
OneMap API serves as a function to check the Longitude and the Latitude of the postal codes of the restaurant. It will aid us in our analysis of the location.
### 4.2 Assumptions
Due to the sheer amount of data our team is scraping, we limit our dataset to meet the scope of the project. Therefore, the following assumptions have been made:
1)	The reviewers have had food from the restaurant for which they have reviewed. 
2)	The reviewer who had posted the review dined within the same month of posting.
3)	The review posted is unbiased.
4)	Only restaurants with review count more than 100 and less than 500 in TripAdvisor have been considered for our study. The same list has been used to scrape for from Google Reviews.
5)	The unique ID of the restaurant is the trimmed version of the TripAdvisor URL.
6)	Eventbrite events have been limited within the time frame of 2015 to 2018.
7)	We have filtered 9 out of the 21 categories of events from Eventbrite. Namely,

|   |  |  |
| ------------- | ------------- | ------------- |
| Food & Drink  | Performing & Visual Arts  | Film,Media & Entertainment |
| Seasonal & Holiday  | Science & Technology  | Travel & Outdoor |
| Seasonal & Holiday  | Fashion & Beauty  | Hobbies & Special Interest |

Table 1 – Categories of EventBrite Chosen

8)	We have also only included Events that are only hosted on the online platform.
9)	We have only included free events listed in EventBrite.
#### **TripAdvisor**

The assumptions (1), (2) & (3), allow us to ensure that our data is unbiased. As such, our analysis will be like the census on the ground within the similar time frame. 
For assumption (4) & (5), we limit the scope of the project to a manageable scale. By setting the cut-off to be 100 reviews, unpopular restaurants are filtered out. It allows us to have a more accurate analysis of the ratings with smaller variance. We limit the total number of reviews to be 500, to reduce the time needed for scraping data off TripAdvisor. With this limitation 733 restaurants were scrapped, and the total number of reviews and customers obtained is around 130,000 and about 60,000 lines of records respectively.
#### **EventBrite**
For assumption (6), to find the relationship between events and restaurants, the data of events from 2015 to end of 2018 have been considered. We have set 3 years to be the timeframe. This is to ensure that the data is as accurate as possible. For assumption (7) & (8), we have curated the category listing of the events in a way that they have the most impact on the restaurants surrounding them. 
#### **Google Reviews**
The restaurant list consolidated from (4) is used to collect user ratings from peer sites such as Google Reviews. Only the overall average ratings across all reviews were considered as part of the scraping region of interest.
#### **Zomato**
For scraping restaurants from Zomato, we assume that the overall rating displayed is a true reflection of customer’s individual rating. There are restaurants listed on Zomato, which have no customer reviews or ratings at all, but still boasts of an overall rating.
## 5.	WEBSCRAPING METHODS
### 5.1 Web Scraping Techniques
|   |  | 
| ------------- | ------------- | 
| Selenium | – Google Reviews | 
| Beautiful Soup & Requests | – Trip Advisor, OneMap API, EventBrite API, Zomato | 
### 5.2 Web Scraping Details

#### TripAdvisor

From the web structure of TripAdvisor, we found that there are 30 restaurants in each page and 20 reviews in each page for every restaurant, and there is one customer for a review. Based on this structure, the scraping procedure follows as below:
1)	Connect to Raw Database in MongoDB with package ‘pymongo’
2)	Get the URL of main page with specific format, and then get the detail URL link of each restaurant in this page;
3)	Scrape the detail values about one restaurant as shown in (Appendix A1).
4)	Get the latitude and longitude of the restaurant through OneMap API and insert all records about restaurant into database as shown in (Appendix A2).
5)	For restaurants with reviews between 100 and 500, we obtain the URL of each review list page and get the detail URL link of each review. After which, we get the customer’s URL of the review through its UID value; we scape the detail of one review as shown in (Appendix A3). 
EventBrite API
Eventbrite has exposed an API that allow us to scrape data from their website and we have used the parameters as shown in (Appendix A4). As mentioned earlier, we have the longitude and latitude of each restaurant. As such, by placing these values into EventBrite API, we are able to obtain the nearby events for each restaurant during this 3-year time frame. 
According to response values of API, we can only get the ‘Restaurant-Event’ relationship like Figure - 3. However, this relationship obtained will not be useful for our analysis. As such, we implemented a mapping function to remap the relationship as below.

![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/1.png)
Figure – 2 Original Relationship
![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/2.png)
Figure – 3 New Relationship
With the mapping function, we have obtained the following data which is to be directly imported into MongoDB as shown in (Appendix A5).
Google Reviews
Initially we tried to use BeautifulSoup to extract the information (user ratings and user votes) from the tags. However, we realized that Google has ‘cloaking’ mechanisms to misguide the scraper service from the browser-based content. To overcome this issue, we used Selenium to simulate an actual browser interaction with the webpages and mouse hover and clicks to mimic a human, create artificial delays (using system sleep) and retrieve the data. Though we scraped from the same site – Facebook and HungryGoWhere ratings as well, their count and impact on the list of restaurants were negligible and were ignored in the analysis stage.
Zomato
We scraped the restaurant details of restaurants available in Singapore. The list had a total of 8,580 restaurants, with each webpage having details for 15 restaurants. Data collected is shown in (Appendix A6).
### 5.3 Data Summary
Based on what we have discussed above, the total number of records we have got from each website are as below.

| Data Source | Home Page | Data Type | Total No. of Records |
| ------------- | ------------- | ------------- | ------------- |  
| TripAdvisor | https://www.tripadvisor.com.sg/Restaurants | Restaurant | 8,400 |
| |  | Review and customer | 136,203 |
| EventBrite API | https://www.eventbrite.sg/ | Event | 329 |
| Zomato | https://www.zomato.com/singapore | Restaurant | 8,580 |
| Google Reviews | https://www.google.com/ | Rating of Restaurant | 672 |

Table 2 – Data Summary

## 6.	MONGODB INTEGRATION DETAILS
### 6.1 Staging Database
A staging database has been used to load data from website. After modifying and cleaning the data, it is placed in a production database. This facilitates restart ability and minimize the impact of scraping by keeping 1 copy in staging database. If the ETL fails, there is no need to scrape a 2nd time by restarting the ETL from the last successful timestamp. Another benefit is that it is very straightforward and convenient for distributed work. This is so, because the schema of staging database is based on the data structure after scraping, and for each website we have a specific collection to store. This means that any modification in the future will affect only a single collection, and there is no need for changing the data structure before inserting into the database.                 
We have five collections in our staging database, namely ‘events’, ‘google_ratings’, ‘restaurants’, ‘reviews’ and ‘zomatos’, The detail schema is as shown below. 
![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/3.png)
### 6.2 Extract-Load-Transform-Load (ELTL)                                                      
The raw data was extracted from websites and dumped into the staging database (ELT). In the second step, it requires to be cleaned before transferring into the production database (ETL) is used. ETL is a data pipeline to collect data from various sources and transform the data according to our business analysis tasks. After which, it will load the data into the production database.  
In case of downtime or loss of data, we have devised a procedure which makes our production database check on the last updated timestamp before performing the data scraping process. This way, we reduce the amount of data required to scrape, hereby reducing the down time. With this procedure, we improve the efficiency of scraping performance and reduce the amount of storage resources required. The next web scraping will start from the follow-up point of the last timestamp and our production database will match its own last timestamp so that the new extracting action will only consider the data after that date to append to pervious loaded data. For next ETL action, the procedure remains the same.
We have coded a python script using package ‘pymongo’ to implement this and load formatted data into our production data. At the initial stage, we have loaded all data in staging date into our production database. However, the timestamp checking strategy will be used in every next action.
![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/4.png)
### 6.3 Production Database
Bases on our business analysis and insight discovery’s requirements later, the total schema diagram has been designed. There are four original collections which load data from the staging database directly, with different schema structures.
For the collection ‘restaurants’, data from ‘restaurants’, ‘zomatos’ and ‘google_ratings’ is merged in staging database into one single collection. The collection ‘reviews’ in staging database has been split into two collections, namely ‘customers’ and ‘reviews’. No change is made to ‘events’ collection. It is another data layer for which same data structure is synchronized directly. There are another two collections named ‘mr_cuisines’ and ‘nlp_sentiment_analysis’. The ‘mr_cuisines’ collection, is obtained by refactoring the data in the original collections using MapReduce. The ‘nlp_sentiment_analysis’ collection is a result of the NLP Analysis which is discussed in next section.                                                                                                                                              
**Embedded Data**
Embedded document capture relationships between data by storing related data in a single document structure. As we know, MongoDB documents make it possible to embed document structures in a field or array within a document. These denormalized data models allow us to retrieve and manipulate related data in a single database operation during business analysis. 
![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/5.png)
Figure – 6 Embedded Data Model

We have used three embedded data models as below in our ‘restaurants’ collection: 
1.	Embedded sub-document 1: Splitting original ‘address’ column into four parts, which are ‘street’, ‘extended_add’, ‘country’, ‘postal_code’, and combining them with original ‘postal_code’, ‘latitude’ and ‘longitude’ into this sub-document.
2.	Embedded sub-document 2: Combing original ‘rating_atmosphere’,                                  
 ‘rating_food’, ‘rating_service’ and ‘rating_value’ into this sub-document.
3.	Embedded sub-document 3: As our original ‘meal’ value only contains six types value, which are ‘breakfast’, ‘lunch’, ‘dinner’, ‘after-hours’, ‘drinks’ and ‘brunch’. So, we used them to represent what type of meal the restaurant can offer, for example, if it has ‘breakfast’ in original ‘meal’ value, then this column will be ‘Y’, otherwise, it will be empty.
**Normalized Data**
As we can see from the previous total schema diagram, there are some relationships between different collections. Therefore, we         have normalized our data to describe one-to-one or one-to many relationships using references between collections, which can provide more flexibility than embedding. For the detail relationships between them are as left.

![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/6.png)

Figure – 7 Normalized Data Model  

**Indexing**
Similar to SQL database, Indexes support the efficient execution of queries in MongoDB. Without index, MongoDB must perform a collection scan, like scanning every document in a collection, to select those documents that match the query statement, which will produce a huge amount of time consuming when the volume of data is very large. If an appropriate index exists for a query, MongoDB can use the index to limit the number of documents it must inspect. In addition, MongoDB can return sorted results by using the ordering in the index.
Based on what we will query during doing business analysis in Tableau, several indexes as below have been created to support our efficient equality matches and range-based query operations.

![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/7.png)
Figure – 8 Create Index

### 6.4 MapReduce and NLP
**MapReduce**
The MapReduce paradigm helps in parallel and distributed batch processing of documents in MongoDB and suitable in cases wherein it is complicated to obtain the same aggregated result set using simple queries. MR in MongoDB groups similar Keys K in (K,V) and allows custom aggregation on the Values V. It was used to compute the I. review count across subzones with details on the top 10 restaurants in each subzone. II. Review count across cuisines and the top 10 restaurants serving those cuisines.
**NLP**
When dealing with unstructured text data, Natural Language Processing (NLP) can be done to get several use cases and insights can be drawn from the same. The objective of this analysis is to get the polarity of the reviews and analyse the polarity trends across restaurants. 
We are using python’s VADER (Valence Aware Dictionary and Sentiment Reasoner) package. VADER sentiment analysis is based on lexicons of sentiment-related words and produces four sentiment metrics. We are considering only three out of four namely, positive, negative and neutral. It represents the proportion of the text that falls into these categories.
All the reviews were passed through this package to get the metrics values and was stored into a newer collection in the MongoDB. This data was then pulled on to the tableau dashboard for analysis.
### 6.5 Sharding
Sharding has been used in our case to improve the scalability, availability and manageability of the database. Scalability means we can increase the number of servers as the application grows, just add and load to the new server. Availability means we do not need to stop the entire system from servicing after several of these shard servers are down, but only the users who need access to the data on these shard servers. And manageability means the upgrade and configuration of the system can be done according to shard one by one and will not have a significant impact on the service.
By distributing data across multiple machines, it allows deployment with very large dataset and high throughput operations. It improves scalability, availability and manageability of the database. The steps taken are in the Appendix B1.
### 6.6 Archiving
Currently, there are more than 150 thousand and 200 thousand lines of record in our staging and production database respectively, and they will grow quickly when insert new reviews of these restaurants. And it is also very time-consuming for the database to query the latest timestamp before starting new web scrapping and ETL jobs. Last but not least, without some strategy for managing the size of our database, most event logging systems can grow infinitely. Therefore, it is particularly important to determine some archiving strategies to avoid these problems, two different levels of archiving strategy as below are used in our staging database:
1)	**Renaming collections**: As in our staging database, the ‘reviews’ and ‘events’ collection may grow to a large scale of arrays during web scrapping in the future. It is necessary to rename the collections periodically when the data of it has been loaded into our production database, and only use the collections that have not been renamed each time, so that our data collections can rotate in much the same way with rotating log files.
2)	**Using capped collections**: As we know, capped collections have a fixed size, and drop old data when inserting new data after reaching cap. Therefore, except the first strategy, to guarantee the reasonable usage of storage resources, capped collections have been configured to drop the oldest collection automatically from the staging database.
However, depending on our data retention requirements as well as our reporting and analytics needs, any data should not be dropped based on time, so we will not use pervious two strategies directly in our production database. A very import archiving step has been considered for it, which is restoring those data will not be used in different collections, for example, restaurants have more than 500 reviews and events that have already closed. After that, we will use the above strategies for those collections.
## 7.	BUSINESS ANALYSIS
**Sentiment Analysis**
We have aggregated the metric values for each restaurant and plotted the same against the number of restaurants. We have also added a filter based on the ranking of the restaurant. With this, we can see that Rank 1 to 1000 restaurants have a better sentiment analysis throughout the 3 variables. Therefore, we can conclude people are generally happier with lower ranked restaurants.

![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/8.png)

Figure – 9 Sentiment Analysis
**Reviewer Contributions**
We try to find out reviewer's distribution in terms of number of reviews for measuring website’s popularity. The below plot is drawn between the review count v/s the reviewer’s count. We can find that close to 1700 distinct reviewers have posted only less than 10 reviews and there are around 800 odd reviewers who have posted 10-20 reviews. As the review count axis is scaled till 230 we can make out that there is at-least 1 reviewer who has continuously contributed towards the restaurant reviews over time.   

![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/9.png)                                                    
Figure – 10 Reviewer Contributions
**Comparative Study Across Top Restaurant**
In the image above, we have the comparative study on the different restaurants in Singapore based on the review ratings from different sites. The graph as shown is ranked based on the top ranking of restaurants in Singapore. We have the top 5 restaurants for comparison.

| Origin’s Grill | Chef Table | Alma by Juan | Shinji by Kanesaka | Positano Ristro |
| ------------- | ------------- | ------------- | ------------- |   ------------- | 
| Google | 13 | 67 | 59 | 91 | 127 |
| TripAdvisor | 135 | 154 | 313 | 336 | 243 |
| Zomato | 26 | 6 | 11 | 3 | 9 |

This is a snapshot of the top 5 restaurants ranked by TripAdvisor. We can see that Zomato ratings are consistently lower than the ones from Google Reviews and TripAdvisor. This might be since Zomato has low number of reviews compared to the other two. Although, the number of reviews from Google is lower than TripAdvisor, the ratings for the top 5 restaurants are consistent with each other. In the Tableau storyboard, we have the whole list of restaurants ranked with the comparison of rating, sorted by TripAdvisor rankings.
![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/10.png)   
Through our shallow analysis, we have found out that the ratings for Google and TripAdvisor are similar while there is insufficient rating available in Zomato to make a proper analysis. As such, should a person be interested in the finding out the rating of restaurants, they can either go to TripAdvisor or Google Reviews to make an educated choice.
![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/11.png)   
The above image shows the nearby restaurant for each event. We have filtered based on the Start Date and End Date of the event and the list of events will be shown in the drop-down list. After selecting, the list of nearby restaurant will be shown on the map with the review counts on the graph below. This example shows that ‘Swee Choon Tim Sum’ is the most highly rated restaurant for this particular event.
The above image shows a map that shows the location of the restaurants and are filtered based on cuisines. On the right, we have filters that allows the user to choose the range of Rankings desired as well as the type of food based on cuisines. 
By clicking on the point, it showcases the address as well as the restaurant location with the TripAdvisor and Google Rating. In this case, we have chosen Alcohol to be the primary concern. With this, restaurants with the alcohol tag will pop on the map. Click on the point will showcase the name of the restaurant as well as the address, followed by the ratings. 
The main purpose of this page is to allow users to identify places to eat based on possible dietary restriction. As such, we have added “Gluten Free” & “Vegetarian Options” into this selection. In addition, we believe that Singapore’s night life is bustling.

![alt text](https://github.com/rickyken90/Foodie_Hunt/blob/master/Images/12.png) 
Figure – 13 Top Places Based on Cuisines

As such, we have included in the alcohol section which covers the pubs and bars in Singapore. We believe that this will aid the users tremendously in for easy information retrieval based on cuisine. 
Similarly, to the previous image, we present a map with the list of restaurants based on Nationality type. As we are a metropolitan city, we have lots of restaurant in Singapore of different cuisine. As such many of these restaurants have multiple Nationality tags. In addition, the list is long. As such, we have curated the list and only showcase those that are more prevalent in Singapore. 
 We have the filters based on the ranking of the restaurants as well as the Nationality of the Cuisines. In the example as shown above, we are interested in Chinese Food. By removing all except the Chinese tag, we are able to list out the restaurants around the city area. By clicking on the points, it will similarly showcase the name of the restaurant as well as the address followed by the ratings from Google and TripAdvisor.
The main purpose of this functionality is to allow user to choose what type of food they wish to eat. It is slightly different from the previous page where we are targeting the users with dietary restrictions or looking for drinking spots.                                                                  
## 8.	CONCLUSION
As managing continuous operation of the restaurant is a difficult business, so is for the customer for filtering down to his/her choice of restaurant in Singapore. For both the above said scenarios the customer reviews and restaurants ratings from dedicated websites form a great source of feedback. It would be difficult for both the business owner and the customer to analyze and comprehend from the enormous data that keeps flowing in constantly. Our story board which was developed post thorough analytics on a rich collective resource of customer reviews and ratings would be very helpful. Customers will be able to filter down to the restaurant of choice based on the cuisine and nationality. Also, business owners can see the trend of the sentiment analytics done on the reviews and improve. As an additional layering the story board also allows in shortlisting the restaurants around a public event. 
Of course, our story board can further be enhanced to get better insights by expanding the database, coming with newer metrics and a better user experience. We could also expand the scope to analyze for different countries, currently with the interest of time it’s limited to only Singapore.
## 9.	REFERENCES
[1] https://www.tripadvisor.com.sg/Tourism-g294262-Singapore-Vacations.html

[2] https://www.eventbriteapi.com/

[3] http://t-redactyl.io/blog/2017/04/using-vader-to-handle-sentiment-analysis-with-social-media-text.html

[4] https://docs.mongodb.com/manual/core/data-modeling-introduction/

[5] http://comp.social.gatech.edu/papers/icwsm14.vader.hutto.pdf
