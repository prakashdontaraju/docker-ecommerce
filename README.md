# docker-ecommerce

## Business Case

Our customers (subscribers) seek help to build skills to deploy simple and viable batch pipelines entirely on Docker involving the following relational and NoSQL databases:
* Cassandra
* MySQL
* Redis
 
### Focus

I successfully engineered 3 batch data processing pipelines with PySpark while having the databases entirely on Docker.

I ingested, pre-processed and visualized the data in these databases to validate their successful deployment.

## Data

I chose the [eCommerce behavior data from multi category store](https://www.kaggle.com/mkechinov/ecommerce-behavior-data-from-multi-category-store) data to focus on successfully implementing the 3 batch pipelines.

However, the business data I work with at my company and in most other environments requires more pre-processing than this data.

### Properties of data

 Data file contains behavior data for a 1 month (November 2019) from a large multi-category online store.
 
 Each row in the file represents an event.

* All events are related to products and users

* There are 3 different types of events
    * view
    * cart
    * purchase

Here's the distribution of events in the data:

![Event Types](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/data/event_types.PNG)

## Batch Pipelines 

### Analysis

I performed the following analyses on the pre-processed store data

* Purchase conversion rate

* Purchase conversion volume

* Top 20 brands purchased

* Purchase category vs Volume

* Hour vs Event Type vs Price

* Most visited sub-categories

* Views by category

* Daily event count


### Pipelines Implementation

![Batch Pipelines Implementation](https://github.com/prakashdontaraju/docker-ecommerce/blob/main/docker_pipeline.PNG)

## Acknowledgement

All data, I based my analysis on, is colleced by and belongs to [Open CDP](https://rees46.com/en/open-cdp) project.

## Connect with me
**Prakash Dontaraju** [LinkedIn](https://www.linkedin.com/in/prakashdontaraju) [Twitter](https://twitter.com/WittyGrit) [Medium](https://medium.com/@wittygrit)
