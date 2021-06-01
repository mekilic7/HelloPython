###########################################
###################ÖDEV-1##################

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def load_titanic():
    df = pd.read_csv("H2/datasets/titanic.csv")
    return df

df = load_titanic()

def cat_summary(dataframe, col_name, plot=False, hueCol=""):
    print(pd.DataFrame({col_name: dataframe[col_name].value_counts(),
                        "Ratio": 100 * dataframe[col_name].value_counts() / len(dataframe)}))
    print("##########################################")
    if plot:
        if (hueCol == ""):
            sns.countplot(x=dataframe[col_name], data=dataframe)
            plt.show()
        else:
            sns.countplot(x=dataframe[col_name], data=dataframe, hue=dataframe[hueCol])
            plt.show()

cat_summary(df, "Sex", plot=True)



###########################################
###################ÖDEV-2##################


################
####ÖDEV-2.1####
################
def cat_summary(dataframe, col_name, plot=False, hueCol=""):
    """
    Veris setindeki kategorik değişkenle ilgili özet bilgi (categori sınıflarının ve frekeans ve oranları) sunar.
    Opsiyonel olarak countplot çizimi yapar
    Son eklenen özellikle beraber opsiyonel olarak 3. kırılımı da grafiğe eker

    Parameters
    ----------

    dataframe: dataframe
            Değişken isimleri alınmak istenilen dataframe
    col_name: string
            Özet bilgisi istenen kolon ismi
    plot: bool, optional
            Grafik çizilip çizilmeyeceğini belirten parametre
    hueCol: string,optional
            Grafik çizilirken 3.bir değişken dahil edilip edilmeyeceğini belirten parametre.

    Examples
    ------
       import pandas as pd
       import matplotlib.pyplot as plt
       df = pd.read_csv("H2/datasets/titanic.csv")
       cat_summary(df, "Sex", plot=True)
       cat_summary(df, "Sex", plot=True, hueCol="Pclass")

    -------

    """

    print(pd.DataFrame({col_name: dataframe[col_name].value_counts(),
                        "Ratio": 100 * dataframe[col_name].value_counts() / len(dataframe)}))
    print("##########################################")
    if plot:
        if (hueCol == ""):
            sns.countplot(x=dataframe[col_name], data=dataframe)
            plt.show()
        else:
            sns.countplot(x=dataframe[col_name], data=dataframe, hue=dataframe[hueCol])
            plt.show()

cat_summary(df, "Sex", plot=True, hueCol="Pclass")


################
####ÖDEV-2.2####
################
def check_df(dataframe, head=5):
    """
    Dataframe ilgili hızlı bir genel değerlendirme yapar
    Parameters
    ----------
    dataframe: dataframe
            Hakkında gözlem yapılacak dataframe
    head:int,optional
            Baştan kaç gmölemin gösterileceği bilgisi

     Notes
    ------
    Konsol ekrana , fonksiyona parametra olarakk girilen dataframe ile ilgili bilgiyi basar.

     Examples
    ------
    import pandas as pd

        df = pd.read_csv("datasets/titanic.csv")
        check_df(df)
        check_df(df,10)
    """

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







