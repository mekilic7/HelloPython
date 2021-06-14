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


##############################################################
#BG-NBD ve GG modeli ile CLTV'nin hesaplanması. (1 aylık ve 12 aylık)
##############################################################


cltv_1m = ggf.customer_lifetime_value(bgf,
                                   cltv_df['frequency'],
                                   cltv_df['recency'],
                                   cltv_df['T'],
                                   cltv_df['monetary'],
                                   time=3,  # 3 aylık
                                   freq="W",  # T'nin frekans bilgisi. Haftalık
                                   discount_rate=0.01)


cltv_12m = ggf.customer_lifetime_value(bgf,
                                   cltv_df['frequency'],
                                   cltv_df['recency'],
                                   cltv_df['T'],
                                   cltv_df['monetary'],
                                   #time=3, default 12 aylık
                                   freq="W",  # T'nin frekans bilgisi. Haftalık
                                   discount_rate=0.01)






cltv_1m.head()
cltv_12m.head()


cltv_1m = cltv_1m.reset_index()
cltv_12m = cltv_12m.reset_index()


cltv_1m.sort_values(by="clv", ascending=False).head(10)
cltv_12m.sort_values(by="clv", ascending=False).head(10)

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















cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")

cltv_final.sort_values(by="clv", ascending=False).head(10)


# CLTV'nin Standartlaştırılması
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(cltv_final[["clv"]])
cltv_final["scaled_clv"] = scaler.transform(cltv_final[["clv"]])

# Sıralayalım:
cltv_final.sort_values(by="scaled_clv", ascending=False).head()



##############################################################
# 5. CLTV'ye Göre Segmentlerin Oluşturulması
##############################################################

cltv_final["segment"] = pd.qcut(cltv_final["scaled_clv"], 4, labels=["D", "C", "B", "A"])

cltv_final.head()


cltv_final.groupby("segment").agg(
    {"count", "mean", "sum"})


