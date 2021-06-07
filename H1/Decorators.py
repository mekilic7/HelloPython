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
#//***********extras ** assert kullanımı****************



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