from sqlalchemy import create_engine
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.4f' % x)
from sklearn.preprocessing import MinMaxScaler


def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit


def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


#########################
# Verinin Veri Tabanından Okunması
#########################


creds = {'user': 'synan_dsmlbc_group_2_admin',
         'passwd': 'iamthedatascientist*****!',
         'host': 'db.github.rocks',
         'port': 3306,
         'db': 'synan_dsmlbc_group_2'}




# MySQL conection string.
connstr = 'mysql+mysqlconnector://{user}:{passwd}@{host}:{port}/{db}'
conn = create_engine(connstr.format(**creds))


#pd.read_sql_query("show databases;", conn)
#pd.read_sql_query("show tables", conn)
#pd.read_sql_query("select * from online_retail_2010_2011 where Country = 'United Kingdom' ", conn)


retail_uk_df = pd.read_sql_query("select * from online_retail_2010_2011 where Country = 'United Kingdom' ", conn)
retail_uk_df.shape

df = retail_uk_df.copy()


#########################
# Veri Ön İşleme
#########################

df.describe().T  # price ve Quantity de eksi değerler var .. Birşeyler yanlış düzenleme yapılmalı
df.dropna(inplace=True) # Null değerleri düş
df = df[~df["Invoice"].str.contains("C", na=False)] # iadeleri düş
df = df[df["Quantity"] > 0]

replace_with_thresholds(df, "Quantity") # outlier düzenlemesi
replace_with_thresholds(df, "Price") # outlier düzenlemesi
df.describe().T

df["TotalPrice"] = df["Quantity"] * df["Price"]
today_date = dt.datetime(2011, 12, 11)

#########################
# Lifetime Veri Yapısının Hazırlanması
#########################


cltv_df = df.groupby('Customer ID').agg({'InvoiceDate': [lambda date: (date.max() - date.min()).days,
                                                         lambda date: (today_date - date.min()).days],
                                         'Invoice': lambda num: num.nunique(),
                                         'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

cltv_df.columns = cltv_df.columns.droplevel(0) # ilk satırı sil..
cltv_df.columns = ['recency', 'T', 'frequency', 'monetary']

cltv_df["monetary"] = cltv_df["monetary"] / cltv_df["frequency"]

cltv_df = cltv_df[cltv_df["monetary"] > 0]

# BGNBD için recency ve T'nin haftalık cinsten ifade edilmesi
cltv_df["recency"] = cltv_df["recency"] / 7
cltv_df["T"] = cltv_df["T"] / 7


# frequency'nin 1'den büyük olması gerekmektedir.
cltv_df = cltv_df[(cltv_df['frequency'] > 1)]


##############################################################
#BG-NBD Modelinin Kurulması (Expected Number of Transaction)
##############################################################

bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(cltv_df['frequency'], #  a: 0.12, alpha: 11.66, b: 2.51, r: 2.21
        cltv_df['recency'],
        cltv_df['T'])


##############################################################
# GAMMA-GAMMA Modelinin Kurulması (Expected Average Profit)
##############################################################

ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df['frequency'], cltv_df['monetary'])

cltv_df["expected_average_profit"] = ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                                                             cltv_df['monetary'])







############################################################
##########GÖREV 1 ##########################################
############################################################
# 6 aylık CLTV Prediction
# 2010-2011 UK müşterileri için 6 aylık CLTV prediction yapınız.

cltv_6m = ggf.customer_lifetime_value(bgf,
                                   cltv_df['frequency'],
                                   cltv_df['recency'],
                                   cltv_df['T'],
                                   cltv_df['monetary'],
                                   time=6,  # 3 aylık
                                   freq="W",  # T'nin frekans bilgisi. Haftalık
                                   discount_rate=0.01)


cltv_6m.describe().T

cltv_6m = cltv_6m.reset_index()

cltv_6m.columns = cltv_6m.columns.str.replace('clv', '6m_CLTV')

cltv_6m.head()


cltv_final = cltv_df.merge(cltv_6m, on="Customer ID", how="left")
cltv_final.head()

cltv_final.describe([0.5]).T

cltv_final.sort_values(by="6m_CLTV", ascending=False).head(10)
      # Customer ID  recency       T  frequency  monetary  expected_average_profit    6m_CLTV
# 2486   18102.0000  52.2857 52.5714         60 3584.8878                3595.1926 85651.0105
# 589    14096.0000  13.8571 14.5714         17 3159.0771                3191.3867 55650.6468
# 2184   17450.0000  51.2857 52.5714         46 2629.5299                2639.4193 48533.3101
# 2213   17511.0000  52.8571 53.4286         31 2921.9519                2938.2745 36797.0067
# 1804   16684.0000  50.4286 51.2857         28 2120.0470                2133.2036 25083.0254
# 406    13694.0000  52.7143 53.4286         50 1267.3626                1271.7854 25060.7087
# 587    14088.0000  44.5714 46.1429         13 3859.6015                3911.3188 25010.0591
# 1173   15311.0000  53.2857 53.4286         91  667.5968                 668.8945 23591.3895
# 133    13089.0000  52.2857 52.8571         97  605.1866                 606.2937 22927.6930
# 1057   15061.0000  52.5714 53.2857         48 1108.3078                1112.3471 21123.0821


# Elde ettiğiniz sonuçları yorumlayıp üzerinde değerlendirme yapınız.
# -- İlk 10 sıradaki müşterileri incelediğimizde 2. sıradaki müşteri dikkat çekicidir.
#   Yeni bir müşteri olmasına rağmen yüksek potansiyeli sayesinde 2. sıraya yerleşmiştir.

# -- Birinci sıradaki müşteriye yakın şekilde recency ve frequency değerlerine sahip olan 6. sıradaki müşteri
#   monetary değerinin düşük olması sebebiyle gerilerde görünüyor.

# -- /7. sıradaki müşteri monetary yüksek olmasına rağmen yüksek recency ve düşük frequency değerlerinden kaybediyor
#  gibi görünüyor.



############################################################
#################### GÖREV 2 ###############################
############################################################

# Farklı zaman periyotlarından oluşan CLTV analizi
# 2010-2011 UK müşterileri için 1 aylık ve 12 aylık CLTV hesaplayınız.
# 1 aylık CLTV'de en yüksek olan 10 kişi ile 12 aylık'taki en yüksek 10 kişiyi analiz ediniz.
# Fark var mı? Varsa sizce neden olabilir?

cltv_1m = ggf.customer_lifetime_value(bgf,
                                   cltv_df['frequency'],
                                   cltv_df['recency'],
                                   cltv_df['T'],
                                   cltv_df['monetary'],
                                   time=3,  # 3 aylık
                                   freq="W",  # T'nin frekans bilgisi. Haftalık
                                   discount_rate=0.01)


cltv_1m = cltv_1m.reset_index()
cltv_1m.head()
cltv_1m.columns = cltv_1m.columns.str.replace('clv', '1m_CLTV')
cltv_final = cltv_df.merge(cltv_1m, on="Customer ID", how="left")
cltv_final.head()






cltv_12m = ggf.customer_lifetime_value(bgf,
                                   cltv_df['frequency'],
                                   cltv_df['recency'],
                                   cltv_df['T'],
                                   cltv_df['monetary'],
                                   #time=3, default 12 aylık
                                   freq="W",  # T'nin frekans bilgisi. Haftalık
                                   discount_rate=0.01)

cltv_12m.head()
cltv_12m = cltv_12m.reset_index()
cltv_12m.columns = cltv_12m.columns.str.replace('clv', '12m_CLTV')
cltv_final = cltv_final.merge(cltv_12m, on="Customer ID", how="left")
cltv_final.head(10)


cltv_final.sort_values(by="1m_CLTV", ascending=False).head(10)
cltv_final.sort_values(by="12m_CLTV", ascending=False).head(10)



cltv_final["rate of increase"] = cltv_final["12m_CLTV"] / cltv_final["1m_CLTV"]

########1 AYLIK CLTV ##########
 #       Customer ID    clv
# 2486   18102.0000     43893.5242
# 589    14096.0000     28804.6421
# 2184   17450.0000     24872.3887
# 2213   17511.0000     18856.5426
# 1804   16684.0000     12857.4778
# 406    13694.0000     12841.6441
# 587    14088.0000     12831.5719
# 1173   15311.0000     12088.2533
# 133    13089.0000     11748.9804
# 1485   16000.0000     11071.0238


########12 AYLIK CLTV ##########
#        Customer ID    clv
# 2486   18102.0000     163591.1268
# 589    14096.0000     104900.4429
# 2184   17450.0000     92694.2748
# 2213   17511.0000     70285.6523
# 1804   16684.0000     47890.3642
# 406    13694.0000     47871.9000
# 587    14088.0000     47688.8636
# 1173   15311.0000     45067.8094
# 133    13089.0000     43795.4729
# 1057   15061.0000     40348.8167



"""YORUM"""""
# Customer ID değerlerine bakıldığında 10 müşterinin 9 u yerini korumuş
# clv değerlerinde zamana bağımlı olarak bir artış görünüyor.
# 1 aylık sıralamda ilk 10 a giren 16000 id numarasına sahip müşteri 12 aylık sıralamada gerilere gitmiş
# büyük ihtimalle churn oldu. Düşük frequency ve yüksek monetary değerlerinin doğurmuş olduğu bir durum.


#cltv_final.sort_values(by="1m_CLTV", ascending=False).head(10)
      # Customer ID  recency       T  frequency  monetary  expected_average_profit    1m_CLTV    12m_CLTV  rate of increase
# 2486   18102.0000  52.2857 52.5714         60 3584.8878                3595.1926 43893.5242 163591.1268            3.7270
# 589    14096.0000  13.8571 14.5714         17 3159.0771                3191.3867 28804.6421 104900.4429            3.6418
# 2184   17450.0000  51.2857 52.5714         46 2629.5299                2639.4193 24872.3887  92694.2748            3.7268
# 2213   17511.0000  52.8571 53.4286         31 2921.9519                2938.2745 18856.5426  70285.6523            3.7274
# 1804   16684.0000  50.4286 51.2857         28 2120.0470                2133.2036 12857.4778  47890.3642            3.7247
# 406    13694.0000  52.7143 53.4286         50 1267.3626                1271.7854 12841.6441  47871.9000            3.7279
# 587    14088.0000  44.5714 46.1429         13 3859.6015                3911.3188 12831.5719  47688.8636            3.7165
# 1173   15311.0000  53.2857 53.4286         91  667.5968                 668.8945 12088.2533  45067.8094            3.7282
# 133    13089.0000  52.2857 52.8571         97  605.1866                 606.2937 11748.9804  43795.4729            3.7276
# 1485   16000.0000   0.0000  0.4286          3 2055.7867                2181.3236 11071.0238  39238.2498            3.5442
# cltv_final.sort_values(by="12m_CLTV", ascending=False).head(10)
#       Customer ID  recency       T  frequency  monetary  expected_average_profit    1m_CLTV    12m_CLTV  rate of increase
# 2486   18102.0000  52.2857 52.5714         60 3584.8878                3595.1926 43893.5242 163591.1268            3.7270
# 589    14096.0000  13.8571 14.5714         17 3159.0771                3191.3867 28804.6421 104900.4429            3.6418
# 2184   17450.0000  51.2857 52.5714         46 2629.5299                2639.4193 24872.3887  92694.2748            3.7268
# 2213   17511.0000  52.8571 53.4286         31 2921.9519                2938.2745 18856.5426  70285.6523            3.7274
# 1804   16684.0000  50.4286 51.2857         28 2120.0470                2133.2036 12857.4778  47890.3642            3.7247
# 406    13694.0000  52.7143 53.4286         50 1267.3626                1271.7854 12841.6441  47871.9000            3.7279
# 587    14088.0000  44.5714 46.1429         13 3859.6015                3911.3188 12831.5719  47688.8636            3.7165
# 1173   15311.0000  53.2857 53.4286         91  667.5968                 668.8945 12088.2533  45067.8094            3.7282
# 133    13089.0000  52.2857 52.8571         97  605.1866                 606.2937 11748.9804  43795.4729            3.7276
# 1057   15061.0000  52.5714 53.2857         48 1108.3078                1112.3471 10824.1523  40348.8167            3.7277
#






############################################################
#################### GÖREV 3 ###############################
############################################################
# Segmentasyon ve Aksiyon Önerileri
#2010-2011 UK müşterileri için 6 aylık CLTV'ye göre tüm müşterilerinizi 4 gruba
#(segmente) ayırınız ve grup isimlerini veri setine ekleyiniz.

cltv_6m_final = cltv_df.merge(cltv_6m, on="Customer ID", how="left")

# CLTV'nin Standartlaştırılması
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(cltv_6m_final[["6m_CLTV"]])
cltv_6m_final["scaled_clv"] = scaler.transform(cltv_6m_final[["6m_CLTV"]])
# Sıralayalım:
cltv_6m_final.sort_values(by="scaled_clv", ascending=False).head()

cltv_6m_final["segment"] = pd.qcut(cltv_6m_final["scaled_clv"], 4, labels=["D", "C", "B", "A"])

cltv_6m_final.head()


cltv_6m_final.groupby("segment").agg({"count", "mean", "sum"}).T

cltv_6m_final[cltv_6m_final["segment"] == "A"].sort_values(by="scaled_clv", ascending=False).head()

cltv_6m_final[cltv_6m_final["segment"] == "B"].sort_values(by="scaled_clv", ascending=False).head()

cltv_6m_final[cltv_6m_final["segment"] == "C"].sort_values(by="scaled_clv", ascending=False).head()

cltv_6m_final[cltv_6m_final["segment"] == "D"].sort_values(by="scaled_clv", ascending=False).head()


# --A segmenti değerlere bakıldığında tek başına ilgiyi hakediyor.
#   A segmentinin ilgilendiği ürünlere yoğunlaşılıp ürün çeşitliliği ve kalitesi hakkında çalışmalar yapılabilir.

# --B segmenti için frequncy değerini arttırırsak A segmentine geçiş yapma ihtimali yüksek müşteriler görünüyor.
#   B segmenti tarafından tercih edilen ürünlerde çeşitli indirim kampanyaları ve birlikte satış kampanyaları yapılabiliz.




############################################################
#################### GÖREV 4 ###############################
############################################################
#Veri tabanına kayıt gönderme

cltv_to_sql = cltv_df.copy()


cltv_to_sql["expected_purc_1_week"] = bgf.predict(1,
                                              cltv_to_sql['frequency'],
                                              cltv_to_sql['recency'],
                                              cltv_to_sql['T'])

cltv_to_sql["expected_purc_1_month"] = bgf.predict(4,
                                              cltv_to_sql['frequency'],
                                              cltv_to_sql['recency'],
                                              cltv_to_sql['T'])


_cltv = ggf.customer_lifetime_value(bgf,
                                   cltv_to_sql['frequency'],
                                   cltv_to_sql['recency'],
                                   cltv_to_sql['T'],
                                   cltv_to_sql['monetary'],
                                   #time=3, default 12 aylık
                                   freq="W",  # T'nin frekans bilgisi. Haftalık
                                   discount_rate=0.01)

_cltv = _cltv.reset_index()
cltv_to_sql = cltv_to_sql.merge(_cltv, on="Customer ID", how="left")

# CLTV'nin Standartlaştırılması
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(cltv_to_sql[["clv"]])
cltv_to_sql["scaled_clv"] = scaler.transform(cltv_to_sql[["clv"]])

# Segmentlerin oluşturulması
cltv_to_sql["segment"] = pd.qcut(cltv_to_sql["scaled_clv"], 4, labels=["D", "C", "B", "A"])


#Veritabanına gönderme

cltv_to_sql.to_sql(name='Mehmet_Emin_Kilic', con=conn, if_exists='replace', index=False)

# Kontrol Edilmesi
pd.read_sql_query("show tables", conn)

