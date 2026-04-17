#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd


# In[6]:


prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow//'
url = f'{prefix}/yellow_tripdata_2021-01.csv.gz'
df = pd.read_csv(url, nrows=100)


# In[7]:


df.head()


# In[8]:


df.dtypes


# In[9]:


df.shape


# In[10]:


dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

df = pd.read_csv(
    url,
    nrows=100,
    dtype=dtype,
    parse_dates=parse_dates
)


# In[11]:


df.head()


# In[12]:


df['tpep_pickup_datetime']


# In[13]:


get_ipython().system('uv add sqlalchemy psycopg2-binary')


# In[14]:


from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')


# In[15]:


df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')


# In[16]:


print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))


# In[17]:


len(df)


# In[18]:


df_iter = pd.read_csv(
    url,
    dtype=dtype,
    parse_dates=parse_dates,
    iterator = True,
    chunksize=100000,
)


# In[19]:


from tqdm.auto import tqdm


# In[ ]:


for df_chunk in tqdm(df_iter):
    df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')


# In[ ]:


get_ipython().system('uv run jupyter nbconvert --to=script notebook.ipynb')


# In[ ]:


get_ipython().system('wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet')


# In[ ]:


get_ipython().system('wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv')


# In[ ]:


df_zones= pd.read_csv('taxi_zone_lookup.csv')


# In[ ]:


df_zones.head()


# In[ ]:




