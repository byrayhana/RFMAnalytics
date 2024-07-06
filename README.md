Sure, here's the README file formatted properly:

---

# Customer Segmentation and RFM Analysis

This repository contains a Python script for performing customer segmentation and RFM (Recency, Frequency, Monetary) analysis on a dataset of customer transactions. The script processes the data, performs segmentation, and outputs customer IDs for targeted marketing campaigns.

## Requirements

- Python 3.x
- pandas library

## Setup

1. Install the required libraries:

   ```bash
   pip install pandas
   ```

2. Download the dataset `flo_data_20k.csv` and place it in the appropriate directory (`C:/Miuul/CRM/FLOMusteriSegmentasyonu-221116-002343/FLOMusteriSegmentasyonu/`).

## Usage

1. Load and explore the data:

   ```python
   import datetime as dt
   import pandas as pd

   pd.set_option('display.max_columns', None)
   pd.set_option('display.float_format', lambda x: '%.3f' % x)

   df_ = pd.read_csv("C:/Miuul/CRM/FLOMusteriSegmentasyonu-221116-002343/FLOMusteriSegmentasyonu/flo_data_20k.csv")
   df = df_.copy()
   df.head()
   df.shape
   df["order_channel"].value_counts()
   df.describe().T
   df.isnull().sum()
   df.info()
   df["master_id"].unique().shape
   ```

2. Create new variables for total orders and total value:

   ```python
   df["total_order"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
   df["total_value"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
   ```

3. Convert date columns to datetime format:

   ```python
   date_columns = df.columns[df.columns.str.contains("date")]
   df[date_columns] = df[date_columns].apply(pd.to_datetime)
   df.info()
   ```

4. Analyze customer distribution across order channels:

   ```python
   df.groupby("order_channel").agg({"master_id": "count", "total_order": "sum", "total_value": "sum"})
   ```

5. Identify the top 10 customers by revenue and order count:

   ```python
   df.sort_values(by="total_value", ascending=False).head(10)
   df.sort_values(by="total_order", ascending=False).head(10)
   ```

6. Define a function for data preprocessing:

   ```python
   def date_prep(dataframe):
       dataframe["total_order"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
       dataframe["total_value"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
       date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
       dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)
       return dataframe
   ```

7. Perform RFM analysis:

   ```python
   df["last_order_date"].max()   # 2021-05-30
   analysis_date = dt.datetime(2021, 6, 1)

   rfm = pd.DataFrame()
   rfm["customer_id"] = df["master_id"]
   rfm["recency"] = (analysis_date - df["last_order_date"]).astype("timedelta64[D]")
   rfm["frequency"] = df["total_order"]
   rfm["monetary"] = df["total_value"]

   rfm["recency_score"] = pd.qcut(rfm["recency"], 5, [5, 4, 3, 2, 1])
   rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, [1, 2, 3, 4, 5])
   rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, [1, 2, 3, 4, 5])
   rfm["rf"] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str)

   seg_map = {
       r'[1-2][1-2]': 'hibernating',
       r'[1-2][3-4]': 'at_Risk',
       r'[1-2]5': 'cant_loose',
       r'3[1-2]': 'about_to_sleep',
       r'33': 'need_attention',
       r'[3-4][4-5]': 'loyal_customers',
       r'41': 'promising',
       r'51': 'new_customers',
       r'[4-5][2-3]': 'potential_loyalists',
       r'5[4-5]': 'champions'
   }

   rfm['segment'] = rfm['rf'].replace(seg_map, regex=True)
   ```

8. Analyze segment statistics:

   ```python
   rfm.groupby("segment").agg({"recency": "mean", "frequency": "mean", "monetary": "mean"})
   ```

9. Save customer IDs for targeted marketing:

   - Case 1: New women's shoe brand promotion:

     ```python
     target_ids = rfm[rfm["segment"].isin(["champions", "loyal_customers"])]["customer_id"]
     cust_ids = df[(df["master_id"].isin(target_ids)) & (df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]
     cust_ids.to_csv("new_target_customers.csv", index=False)
     ```

   - Case 2: Discount on men's and children's products:

     ```python
     target_ids = rfm[rfm["segment"].isin(["hibernating", "cant_loose", "new_customers", "at_Risk"])]["customer_id"]
     cust_ids = df[(df["master_id"].isin(target_ids)) & ((df["interested_in_categories_12"].str.contains("ERKEK")) | (df["interested_in_categories_12"].str.contains("COCUK")))]["master_id"]
     cust_ids.to_csv("new_target_customers.csv", index=False)
     ```

## Conclusion

This script provides a comprehensive approach to customer segmentation using RFM analysis. It allows businesses to identify valuable customer segments and target them with specific marketing strategies. The script can be extended and customized based on specific business requirements.
