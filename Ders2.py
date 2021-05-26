#Functions ****************************************
from numpy.distutils.from_template import item_re

a = 1
b = 2

if a == 1:
    print("aaa")


student=["a","b","c","d"]

type(student[1])





#Enumarate
students = ["John","Mark","Adam","Bob"]

for index,student in enumerate(students,5): #inde start from 5
    print(index ,student)





#zip
students = ["John","Mark","Adam","Bob"]
departments=["mat","stats","physics","astr"]
ages = [34,22,56,56]

print(list(zip(students,departments,ages)))

"""
[('John', 'mat', 34), 
('Mark', 'stats', 22), 
('Adam', 'physics', 56), 
('Bob', 'astr', 56)]
"""




#lambda
#lambda "parameters": "operations"
new_sum = lambda a,b: a+b
new_sum(2,2)*5

#MAP
#list(map("function","iterable object"))

salary = [1000,2000,2300,2500,7897]
list(map(lambda x:x*20/100 +x,salary))
list(map(lambda x:x.upper(),"Merhaba Arkadaşlar ben geldim"))



#FILTER
#list(filter("function","iterable"))
list_store = [1,2,3,4,5,6,7,8,9,10]
list(filter(lambda x: x % 2 == 0,list_store))


#REDUCE
from functools import reduce
list_store = [1,2,3,4]
#reduce("function","sequence")
reduce(lambda a,b: a+b,list_store)
#1+2+3+4 cumulativ


# hi my name is john and i am learning python

string = "hi my name is john and i am learning python"
new_string=""
for i in range(len(string)):
    if i % 2 == 0:
        new_string += string[i].upper()
    else:
        new_string += string[i].lower()

print(new_string)


string = "hi my name is john and i am learning python"
new_string=""
[ string[i].upper() if i % 2 == 0 else string[i].lower() for i in range(len(string))]




#########################################################
#COMPREHENSIONS
##########################################################

salaries = [1000,2000,2300,2500,7897]


[(salary*0.2 + salary) if salary < 3000 else (salary) for salary in salaries]




#########################################################
#Dictionary COMPREHENSIONS
##########################################################

dictionary = {"a":1,"b":2,"c":3,"d":4}

dictionary.keys()
dictionary.values()
dictionary.items()



{k+"a":v*5 for (k,v) in dictionary.items()}
#{'aa': 5, 'ba': 10, 'ca': 15, 'da': 20}




numbers = range(10)

{number:number**2 if number % 2 == 0 else number**3 for number in numbers}



import seaborn as sns
df = sns.load_dataset("car_crashes")
df.columns
new_cols =  [col for col in df.columns if df[col].dtype != "O"]
agg_list = ["mean","min","max","sum"]
{col:agg_list for col in new_cols }



df = sns.load_dataset("tips")
df.head(5)

new_cols = [col for col in df.columns if df[col].dtype in [int , float]]
new_dict =  {col:agg_list for col in new_cols}

df.groupby("time").agg(new_dict)
df.groupby("time").agg({'total_bill': ['mean'], 'tip': ['min', 'max'], 'size': ['sum']})
{k:[k+"_"+_v for _v in v] for k,v in new_dict.items()}



#çözüm

import seaborn as sns
df = sns.load_dataset("car_crashes")
agg_list = ["mean","min","max","sum"]

{col : [str(col) +"_"+ c for c in agg_list] for col in df.columns}




import seaborn as sns
df = sns.load_dataset("car_crashes")
num_cols = [col for col in df.columns if df[col].dtype in [int , float]]

new_df =  df[num_cols]

df[num_cols].head(5)


df[num_cols].values

{row[0]: [str(s) for s in row[1:]] for row in df[num_cols].values }