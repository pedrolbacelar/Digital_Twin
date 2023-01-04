
from mylib.folder1 import mylib1
from mylib.folder2 import mylib2_2, mylib2

class MyClass:
    def say_hello(self):
        obj = mylib1(10)
        print("from mylib1 = ", obj.value)
        print("Hello, world!")

    def lib2(self):
        obj1 = mylib2(1)
        obj2 = mylib2_2(1)
        obj1.printer()
        obj2.printer2()
