# Batch Pipeline On Docker To Easily Know Customer Purchasing Behaviors

## Business Case

Our customers (subscribers) seek help to build skills to deploy simple and viable batch pipelines entirely on Docker involving the following relational and NoSQL databases:
* Cassandra
* MySQL
* Redis
 
### Results

I successfully engineered 3 batch data processing pipelines with PySpark while having the databases entirely on Docker.

I ingested, pre-processed and visualized the data in these databases to validate their successful deployment.

I also analyzed customer purchasing behavior.

### Deployment

I plan to write a blog post about how to deploy these 3 batch pipelines on Docker soon. Stay tuned!

## Data

I chose the [eCommerce behavior data from multi category store](https://www.kaggle.com/mkechinov/ecommerce-behavior-data-from-multi-category-store) available on Kaggle to focus on successfully implementing the 3 batch pipelines.

Real business data requires more pre-processing than the transformations I performed with this data.

### Properties of data

 Data file contains customer behavior data on a large multi-category online store's website for 1 month (November 2019).
 
 Each row in the file represents an event.

* All events are related to products and users

* There are 3 different types of events &#8594; view, cart and purchase

The 2 purchase funnels are
* view &#8594; cart &#8594; purchase
* view &#8594; purchase

Here's the distribution of events in the data:

![Event Types](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/analysis/event_types.PNG)


## Batch Pipelines on Docker

### Implementation

![Batch Pipelines Implementation](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/docker_pipeline.PNG)

### Storage

Cassandra

![Cassandra](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/pyspark_cassandra/docker_cassandra.png)

MySQL

![MySQL](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/pyspark_mysql/docker_mysql.png)

Redis

![Redis](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/pyspark_redis/docker_redis.png)

## Analysis

I performed the following analyses on the pre-processed (transformed) data in storage

* Views by category

![Views By Category](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/analysis/views_by_category.png)

* Purchase category vs Volume

![Purchase category vs Volume](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/analysis/purchase_category_vs_volume.png)

* Top 20 brands purchased

![Top 20 Brands Purchased](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/analysis/top20_brands_purchased.png)

* Purchase conversion volume

![Purchase Conversion Volume](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/analysis/purchase_conversion_volume.png)


## Acknowledgement

All data, I based my analysis on, is collected by and belongs to [Open CDP](https://rees46.com/en/open-cdp) project.

## Connect with me
**Prakash Dontaraju** [LinkedIn](https://www.linkedin.com/in/prakashdontaraju) [Twitter](https://twitter.com/WittyGrit) [Medium](https://wittygrit.medium.com/)
