
#agg_df["customers_level_based"] = agg_df["COUNTRY"].upper()



#[col["COUNTRY"].upper() + "_" + col["SOURCE"].upper() + "_" + col["SEX"].upper() + "_" + col["AGE_CAT"]
#      for col in agg_df.columns]

#[agg_df["COUNTRY"] for col in agg_df.columns]






check_df(agg_df)


agg_df.values


agg_df["customers_level_based"] = [row[0].upper() + "_"+ row[1].upper() +  "_"+  row[2].upper()+ "_"+row[5]  for row in agg_df.values]


[col for col in agg_df.columns]









### agg_df te alınabilirdi ama kaynak kullanımı açısından bu şekilde daha verimli olacağını düşündüm :)

persona_df["SEGMENT"] = pd.qcut(persona_df["PRICE"],4,labels=["D","C","B","A"])



#agg_df.groupby("SEGMENT").agg({"PRICE":["min","max","sum"]}).sort_values(by=["SEGMENT"],ascending=False)




c_seg_df = persona_df[persona_df["SEGMENT"] == "C"]

check_df(c_seg_df)



persona_df =  persona_df.reset_index()

new_user_t = "TUR_ANDROID_FEMALE_30_40"

persona_df[persona_df["customers_level_based"] == new_user_t]

new_user_f= "FRA_ANDROID_FEMALE_30_40"
persona_df[persona_df["customers_level_based"] == new_user_f]





