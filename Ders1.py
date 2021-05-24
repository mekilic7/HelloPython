#semantic doygunluk
#conda > pip
#conda = virtual environment management tool
#pip = packet management tool

#Çok satırlı karekter dizisi """ """

s = """" 
asdasdasd
asdasd
asdas
d
asd
sad
"""
name = "Mehmet"
name[::-1]

#len()  it's out of an object so is a FUNCTION
len(name)
type(len)

#upper() it's in an object so is a METHOD of class str(object):
"m".upper()

"foo".isalnum()
"foo9".isalnum()
"foo9".isnumeric()
"9".isnumeric()



notes = [1,2,3,4,"a"]


dir(notes)

"""
['__add__', '__class__', '__contains__', '__delattr__',
 '__delitem__', '__dir__', '__doc__', '__eq__', '__format__', 
 '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', 
 '__iadd__', '__imul__', '__init__', '__init_subclass__', '__iter__', 
 '__le__', '__len__', '__lt__', '__mul__', '__ne__', '__new__', 
 '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', 
 '__rmul__', '__setattr__', '__setitem__', '__sizeof__', '__str__', 
 '__subclasshook__', 'append', 'clear', 'copy', 'count', 'extend', 
 'index', 'insert', 'pop', 'remove', 'reverse', 'sort']
"""



t = ("john","mark",1,2)
t[0:3]
t[1]="a"

t[0] = "999" #TypeError: 'tuple' object does not support item assignment


#update tuple
t=list(t)
type(t)
t[0] = "merhaba"
t = tuple(t)
type(t)
t




#*****Functions *************************
#parametre fonksiyon tanımlanırken kullanılan adlandırma
#fonksiyona argüman yollanır fonksiyon çağrılırken argüman kullanılır.

#pep8
#https://birhankarahasan.com/pep8-nedir-python-stil-rehberi-yazim-kurallari#:~:text=Pep8%2C%20python%20kodunun%20nas%C4%B1l%20yaz%C4%B1laca%C4%9F%C4%B1n%C4%B1,Nick%20Coghlan%20taraf%C4%B1ndan%20yaz%C4%B1lan%20belgedir.



##################
#Docstring
##################

def summer(arg1,arg2):
    """

    :param arg1: int,float
    :param arg2: int,float
    :return:
    """


help(summer)



def toplama():
    assert (1 == 1)
    print("birinci")
    assert (1 == 2), "Oh no! This assertion failed! 1"
    print("İkinici")



toplama()




#***********************DECORATORS**************************

def disKapalama(func):
    def wrapper(*args, **kwargs):
        print("Dış kaplama Yapıldı")
        func()
        print("Merhaba Kardaşş")
    return wrapper


@disKapalama
def ickaplama():
    print("Mobilyalar değişti")



ickaplama()
#//***********extra       ** assert kullanımı****************
def factorial(n: int):
    print("Hello")
    assert type(n) == int , "Oh no! This assertion failed! 1"
    assert n >= 0 , "Oh no! This assertion failed! 2"


    print("let's go")
    def fact(n):
        if n <= 1:
            return 1
        return n * fact(n - 1)

    return fact(n)

print(factorial(4))