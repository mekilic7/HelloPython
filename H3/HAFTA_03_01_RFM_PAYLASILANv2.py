###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################

# 1. İş Problemi (Business Problem)
# 2. Veriyi Anlama (Data Understanding)
# 3. Veri Hazırlama (Data Preparation)
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
# 7. Tüm Sürecin Fonksiyonlaştırılması

###############################################################
# 1. İş Problemi (Business Problem)
###############################################################

# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
# pazarlama stratejileri belirlemek istiyor.

# Veri Seti Hikayesi
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.


# Değişkenler

# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.



###############################################################
# 2. Veriyi Anlama (Data Understanding)
###############################################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# 2009-2010 yılı içerisindeki veriler
_df_ = pd.read_excel("H3/online_retail_II.xlsx", sheet_name="Year 2009-2010")


_df_.head()

_df_.shape

_df = _df_.copy()
_df.head()
_df.shape

_df.describe().T
_df["TotalPrice"] = _df["Quantity"] * _df["Price"]




###############################################################
# 3. Veri Hazırlama (Data Preparation)
###############################################################

_df.shape
_df.isnull().sum()
_df.dropna(inplace=True)
_df.shape
_df = _df[~_df["Invoice"].str.contains("C", na=False)] # iadeleri çıkar.

_df.shape
###############################################################
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
###############################################################

_df.head()

_df["InvoiceDate"].max() # son alışveriş tarihinden bu yana geçe süre
today_date = dt.datetime(2010, 12, 11) # GARANTİ OLSUN DİYE 2 GÜN SONRASINI AL -- gÜN FARKI 1 OLSUN DİYE

# recency
# frequency
# monetary

_rfm = _df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

_rfm.head()
_rfm.columns = ['recency', 'frequency', 'monetary']
_rfm.describe().T
_rfm = _rfm[_rfm["monetary"] > 0]


###############################################################
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
###############################################################

# Recency ÖNCE RECENCY HESAPLANIR KÜÇÜK OLAN DAHA İYİ
_rfm["recency_score"] = pd.qcut(_rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
# 0,20,40,60,80,100
_rfm.head()

#QCUT degerleri küçükten büyüğe sıralayıp labellara göre sınıflar.
_rfm["frequency_score"] = pd.qcut(_rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
# rank farklı çeyreklerde aynı değer deva ediyorsa çözmek için .... Bakılacak

_rfm["monetary_score"] = pd.qcut(_rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])


_rfm["RFM_SCORE"] = (_rfm['recency_score'].astype(str) +
                    _rfm['frequency_score'].astype(str))



###############################################################
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
###############################################################


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


_rfm['segment'] = _rfm['RFM_SCORE'].replace(seg_map, regex=True)

_rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])


_rfm[_rfm["segment"] == "need_attention"].head()

_rfm.head()


new_df = pd.DataFrame() # yeni dataframe oluşturma...
# Empty DataFrame
# Columns: []
# Index: []

new_df["new_customer_id"] = _rfm[_rfm["segment"] == "need_attention"].index
new_df.head()

new_df.to_csv("H3/need_attention.csv")  # df'i kaydet


###############################################################
# 7. Tüm Sürecin Fonksiyonlaştırılması
###############################################################

def create_rfm(dataframe):

    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df skorları kategorik değere dönüştürülüp df'e eklendi
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))


    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    return rfm

df = df_.copy()
rfm_new = create_rfm(df)
rfm_new.head()