
import datetime as dt
import pandas as pd

pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
####################################
#############Görev 1################
####################################

#1. Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.

df_ = pd.read_excel("H3/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.shape


#2. Veri setinin betimsel istatistiklerini inceleyiniz.
df.describe().T

#v.2
def check_df(dataframe, head=5):
 print("##################### Shape #####################")
 print(dataframe.shape)
 print("##################### Types #####################")
 print(dataframe.dtypes)
 print("##################### Head #####################")
 print(dataframe.head(head))
 print("##################### Tail #####################")
 print(dataframe.tail(head))
 print("##################### NA #####################")
 print(dataframe.isnull().sum())
 print("##################### Quantiles #####################")
 print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

check_df(df)



#3. Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
df.isnull().sum()
#4. Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
df.dropna(inplace=True)

#5. Eşsiz ürün sayısı kaçtır?
len(df["StockCode"].unique())

#6. Hangi üründen kaçar tane vardır?
df["StockCode"].value_counts()
#6 v.2
df.groupby(["StockCode","Description"]).agg({"StockCode":["count"]})


#7.En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.
df[["StockCode"]].value_counts().nlargest(5)
# 7 v.2
df[["StockCode","Description"]].value_counts().nlargest(5) # ref:https://stackoverflow.com/questions/35364601/group-by-and-find-top-n-value-counts-pandas



#8. Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.


df.shape
df = df[~df["Invoice"].str.contains("C", na=False)] # iadeleri çıkar.
df.shape

#9. Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.

df["TotalPrice"] = df["Quantity"] * df["Price"]
df.head()


####################################
#############Görev 2################
####################################
#RFM metriklerinin hesaplanması

#Recency, Frequency ve Monetary tanımlarını yapınız.

"""
Recency  : Müşterinin en son alışveriş yaptığı gün ile analiz yapılan tarih(yada analiz yapan kişinin belirlediği tarih)
          arasındaki gün cinsinden zaman farkı.
         
Frequency: Müşterinin toplam alışveriş(Transaction) sayısı

Monetary : Müşteriden elde edilen toplam kazanç

"""

#Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile hesaplayınız.

#Not 1: recency değeri için bugünün tarihini (2011, 12, 11) olarak kabul ediniz.
max_date = df["InvoiceDate"].max()
today_date = max_date + pd.DateOffset(2)


#Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.

rfm = df.groupby("Customer ID").agg({ "InvoiceDate": lambda x:(today_date - x.max()).days,
                               "Invoice" : lambda x: x.nunique(),
                               "TotalPrice" : lambda x: x.sum()
                             })
#Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.
rfm.columns = ['recency', 'frequency', 'monetary']

#Not 2: rfm dataframe’ini oluşturduktan sonra veri setini "monetary>0" olacak şekilde filtreleyiniz.
rfm = rfm[rfm["monetary"] > 0]

rfm.head()
####################################
#############Görev 3################
####################################

# RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi
# Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
# Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

# ▪ recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RFM_SCORE olarak kaydediniz.
# DİKKAT! monetary_score’u dahil etmiyoruz.

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))


####################################
#############Görev 4################
####################################
#RFM skorlarının segment olarak tanımlanması
# ▪ Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlamaları yapınız.
# ▪ Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz.
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

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()


####################################
#############Görev 5################
####################################
# Aksiyon zamanı!
# ▪ Önemli bulduğunuz 3 segmenti seçiniz. Bu üç segmenti;
# - Hem aksiyon kararları açısından,Hem de segmentlerin yapısı açısından (ortalama RFM değerleri) yorumlayınız.
rfm_sum =  rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm.loc["champions"]

# ilk ve en çok önemsediğim segment *CHAMPIONS* segmenti
# Geçen seneye göre karşılaştırma yaptığımızda ,*champions* segmentinde bir azalma görülüyor
# Bu segmentle ilgili yapılanlar yada yapılmayanları gözden geçiririm. Burada bir şeyler yanlış yapılıyor gibi
#Belli bir puanı harcama limitini aşanlar ile ilgili kampanyalar düzenlenebilir bu grupla ilgili



# ikinci öncelikli segment *LOYAL_CUSTOMERS*
#Bu segmentte kişi sayısında ve karlılıkta artış var müşteri kartı ve kartla yapılan harcamalarda indirim tarzı
# aksiyonlar olabilir.


#üçünücü öncelikli segment *CANT_LOOSE*
# Seni çok özledik gel bak sana güzel güzel hediyeler vereceğiz temalı Mail SMS v.b gönderilebilir.


#################2010-2011 dönemine ait istatistikler####################################

                    # recency       frequency       monetary
                    #    mean count      mean count     mean count
# segment
# about_to_sleep       54.50427   351   1.16239   351  461.06151   351
# at_Risk             156.06207   580   2.86552   580 1076.50643   580
# cant_loose          133.42857    63   8.38095    63 2796.15587    63
# champions             6.87678   633  12.41706   633 6857.96392   633
# hibernating         218.89765  1065   1.10141  1065  487.70758  1065
# loyal_customers      34.46917   827   6.45828   827 2856.72033   827
# need_attention       54.06452   186   2.32796   186  889.22640   186
# new_customers         7.85714    42   1.00000    42  388.21286    42
# potential_loyalists  18.12398   492   2.01016   492 1034.90547   492
# promising            24.44444    99   1.00000    99  355.35131    99


#################2009-2010 dönemine ait istatistikler####################################

                    # recency       frequency       monetary
                    #    mean count      mean count     mean count
# segment
# about_to_sleep        53.82   343      1.20   343   441.32   343
# at_Risk              152.16   611      3.07   611  1188.88   611
# cant_loose           124.12    77      9.12    77  4099.45    77
# champions              7.12   663     12.55   663  6852.26   663
# hibernating          213.89  1015      1.13  1015   403.98  1015
# loyal_customers       36.29   742      6.83   742  2746.07   742
# need_attention        53.27   207      2.45   207  1060.36   207
# new_customers          8.58    50      1.00    50   386.20    50
# potential_loyalists   18.79   517      2.02   517   729.51   517
# promising             25.75    87      1.00    87   367.09    87






# ▪ "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.

loyal_customers_df = pd.DataFrame()
loyal_customers_df["new_customer_id"] = rfm[rfm["segment"] == "loyal_customers"].index
loyal_customers_df.head()
loyal_customers_df.to_csv("H3/loyal_customers.csv")