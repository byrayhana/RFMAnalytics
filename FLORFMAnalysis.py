import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


df_=pd.read_csv("C:/Miuul/CRM/FLOMusteriSegmentasyonu-221116-002343/FLOMusteriSegmentasyonu/flo_data_20k.csv")
df=df_.copy()
df.head()
df.shape
df["order_channel"].value_counts()
df.describe().T
df.isnull().sum()
df.info()
df["master_id"].unique().shape

# Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir. Her bir müşterinin toplam
# alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz.

df["total_order"]= df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["total_value"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

# Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.

date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.info()

#Alışveriş kanallarındaki müşteri sayısının,
# toplam alınan ürün sayısının ve toplam harcamaların dağılımına bakınız.

df.groupby("order_channel").agg({ "master_id" : "count",
                                  "total_order" : "sum",
                                  "total_value" : "sum" })

# En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.

df.sort_values(by="total_value", ascending=False).head(10)

#En fazla siparişi veren ilk 10 müşteriyi sıralayınız.
df.sort_values(by="total_order", ascending=False).head(10)

#Veri ön hazırlık sürecini fonksiyonlaştırınız.

def date_prep(dataframe):
    dataframe["total_order"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["total_value"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)
    return df
#############################################

# RFM Analizi
## veri setindeki en son  alışveriş yapıldığı tarihten 2 gün sonrasının analiz tarihi
df["last_order_date"].max()   # 2021-05-30
analysis_date= dt.datetime(2021,6,1)

rfm = pd.DataFrame()
rfm["cusomer_id"] = df["master_id"]
rfm["recency"] = (analysis_date - df["last_order_date"]).astype("timedelta64[D]")
rfm["frequency"] = df["total_order"]
rfm["monetary"] = df["total_value"]


# Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
rfm["recency_score"] = pd.qcut(rfm["recency"],5,[5,4,3,2,1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"),5,[1,2,3,4,5]) ## duplicate veriler olabilir
rfm["monetary_score"] = pd.qcut(rfm["monetary"],5,[1,2,3,4,5])
rfm["rf"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

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

## Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.

rfm.groupby("segment").agg({"recency" : "mean",
                            "frequency" : "mean",
                            "monetary" : "mean" })


# RFM analizi yardımıyla aşağıda verilen 2 case için ilgili profildeki müşterileri bulun ve müşteri id'lerini csv olarak kaydediniz.
# a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri
# tercihlerinin üstünde. Bu nedenle markanın tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak
# iletişime geçmek isteniliyor. Sadık müşterilerinden(champions, loyal_customers) ve kadın kategorisinden alışveriş
# yapan kişiler özel olarak iletişim kurulacak müşteriler. Bu müşterilerin id numaralarını csv dosyasına kaydediniz.

target_ids = rfm[rfm["segment"].isin(["champions","loyal_customers"])]["cusomer_id"]
cust_ids = df[(df["master_id"].isin(target_ids)) & (df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]
cust_ids.to_csv("yeni_hedef_musteri.csv",index=False)
cust_ids.shape


# Erkek ve Çocuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte
# iyi müşteri olan ama uzun süredir alışveriş yapmayan kaybedilmemesi gereken müşteriler, uykuda olanlar ve yeni
# gelen müşteriler özel olarak hedef alınmak isteniyor. Uygun profildeki müşterilerin id'lerini csv dosyasına kaydediniz.
target_ids = rfm[rfm["segment"].isin(["hibernating","cant_loose","new_customers","at_Risk"])]["cusomer_id"]
cust_ids = df[(df["master_id"].isin(target_ids)) & ( (df["interested_in_categories_12"].str.contains("ERKEK")) | (df["interested_in_categories_12"].str.contains("COCUK")))]["master_id"]
cust_ids.to_csv("yeni_hedef_musteri.csv",index=False)
cust_ids.shape

