import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


df_ = pd.read_excel("Kurs Materyalleri(CRM Analitig╠åi)/datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.shape
df.isnull().sum()
df["Description"].nunique()
df["Description"].value_counts().head()

df.groupby("Description").agg({"Quantity": "sum"}).head()
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
df["Invoice"].nunique()

df["TotalPrice"] = df["Quantity"] * df["Price"]
df.groupby("Invoice").agg({"TotalPrice": "sum"}).head()

df.shape
df.isnull().sum()
df.describe().T
df = df[(df['Quantity'] > 0)]
df.dropna(inplace=True)
df.info()
df["Invoice"] = df["Invoice"].astype(str)
df = df[~df["Invoice"].str.contains("C", na=False)]
## RFM
df["InvoiceDate"].max()  #('2011-12-09 12:50:00')
analysisDate= dt.datetime(2011,12,11)
rfm=df.groupby("Customer ID").agg({ "InvoiceDate": lambda InvoiceDate: (analysisDate - InvoiceDate.max()).days,
                                     "Invoice": lambda Invoice: Invoice.nunique(),
                                     "TotalPrice": lambda TotalPrice: TotalPrice.sum()
})
rfm.columns = ['recency', 'frequency', 'monetary']
rfm.describe().T
rfm = rfm[rfm["monetary"]>0]

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])  ## az olan daha değerli
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5,  labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5 ])

rfm["RF_score"]= (rfm["recency_score"].astype(str)) + (rfm["frequency_score"].astype(str))


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

rfm['segment'] = rfm['RF_score'].replace(seg_map, regex=True)

rfm.groupby("segment").agg({
    "recency": "mean",
    "frequency": "mean",
    "monetary": "mean"

})

## loyal customers bilgilerini çıkar
loyals= pd.DataFrame()
loyals["Loyals_ids"] = rfm[rfm["segment"] == "loyal_customers"].index

loyals.to_csv("loyals_ids.csv")