import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from EDA_Kit import *



def load_persona():
    df = pd.read_csv("H2/datasets/persona.csv")
    return df

df = load_persona()


############################################
########GÖREV-1#############################
############################################



############################################
#Soru 1: persona.csv dosyasını okutunuz ve veri seti ile ilgili genel bilgileri gösteriniz.
def load_persona():
    df = pd.read_csv("H2/datasets/persona.csv")
    return df

df = load_persona()

#from EDA_Kit
check_df(df)
#from EDA_Kit
num_summary(dataframe=df,numerical_col="AGE",plot=False)


############################################
#Soru 2: Kaç unique SOURCE vardır? Frekansları nedir?

df["SOURCE"].unique()
df[["SOURCE"]].value_counts()
#Soru 2: versiyon 2
df.groupby("SOURCE").agg({"SOURCE":"count"})


############################################
#Soru 3: Kaç unique PRICE vardır?
df["PRICE"].unique()

############################################
#Soru 4: Hangi PRICE'dan kaçar tane satış gerçekleşmiş?
df[["PRICE"]].value_counts()

############################################
#Soru 5: Hangi ülkeden kaçar tane satış olmuş?
df[["COUNTRY"]].value_counts()

############################################
#Soru 6: Ülkelere göre satışlardan toplam ne kadar kazanılmış?

df.groupby("COUNTRY").agg({"PRICE":"sum"})

############################################
#Soru 7: SOURCE türlerine göre göre satış sayıları nedir?
df.groupby("SOURCE").agg({"SOURCE":"count"})

#############################################
#Soru 8: Ülkelere göre PRICE ortalamaları nedir?
df.groupby("COUNTRY").agg({"PRICE":"mean"})

#############################################
#Soru 9: SOURCE'lara göre PRICE ortalamaları nedir?
df.groupby("SOURCE").agg({"PRICE":"mean"})

###############################################
#Soru 10: COUNTRY-SOURCE kırılımında PRICE ortalamaları nedir?

df.pivot_table(index="COUNTRY",columns="SOURCE",values=["PRICE"], aggfunc="mean")
#version 2
df.groupby(["SOURCE","COUNTRY"]).agg({"PRICE":"mean"})



############################################
########GÖREV-2#############################
############################################

#COUNTRY, SOURCE, SEX, AGE kırılımında
#toplam kazançlar nedir?
df.groupby(["SOURCE","COUNTRY","SEX","AGE"]).agg({"PRICE":"sum"})





############################################
########GÖREV-3#############################
############################################
#Çıktıyı PRICE’a göre sıralayınız.

temp_df = df.groupby(["SOURCE","COUNTRY","SEX","AGE"]).agg({"PRICE":"sum"})

agg_df = temp_df.sort_values(by=['PRICE'],ascending=False)


############################################
########GÖREV-4#############################
############################################
#Index’te yer alan isimleri değişken ismine çeviriniz.

agg_df =agg_df.reset_index()

agg_df

############################################
########GÖREV-5#############################
############################################
#age değişkenini kategorik değişkene çeviriniz ve agg_df’e ekleyiniz.


agg_df['AGE_CAT'] = pd.cut(agg_df['AGE'], [0, 20, 25, 30, 40, 70],labels=['0_20','20_25','25_30','30_40','40_70'])


check_df(agg_df)



[col["COUNTRY"].upper() + "_" + col["SOURCE"].upper() + "_" + col["SEX"].upper() + "_" + col["AGE_CAT"]
       for col in agg_df.columns]

[agg_df["COUNTRY"] for col in agg_df.columns]


////////////////////////////////////////////*****************************************//////////////////////////////////




yeni 



########GÖREV-5#############################
############################################
#age değişkenini kategorik değişkene çeviriniz ve agg_df’e ekleyiniz.


agg_df['AGE_CAT'] = pd.cut(agg_df['AGE'], [0, 20, 25, 30, 40, 70],labels=['0_20','20_25','25_30','30_40','40_70'])


check_df(agg_df)


agg_df.values


agg_df["customers_level_based"] = [row[1].upper() + "_"+ row[0].upper() +  "_"+  row[2].upper()+ "_"+row[5]  for row in agg_df.values] 




[col["COUNTRY"].upper() + "_" + col["SOURCE"].upper() + "_" + col["SEX"].upper() + "_" + col["AGE_CAT"]
       for col in agg_df.columns]

[col for col in agg_df.columns]


agg_df["SEGMENT"] = pd.qcut(agg_df["PRICE"],4,labels=["D","C","B","A"]) 



agg_df.groupby("customers_level_based").agg({"PRICE" : "mean"})



agg_df.groupby("SEGMENT").agg({"PRICE":["min","max","sum"]}).sort_values(by=["SEGMENT"],ascending=False)


c_seg_df = agg_df[agg_df["SEGMENT"] == "C"]



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



check_df(c_seg_df)





new_user = "TUR_ANDROID_FEMALE_30_40"

agg_df[agg_df["customers_level_based"] == new_user]







