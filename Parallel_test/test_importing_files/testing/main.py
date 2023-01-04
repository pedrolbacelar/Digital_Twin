from folder1.file1 import MyClass1
from folder1.file2 import MyClass2
from folder1.folder2.file3 import MyClass3
import sys



obj1 = MyClass1(1)
print("obj1 = ", obj1.value)

obj2 = MyClass2(1)
print("obj2 = ", obj2.value)

obj3 = MyClass3(1)
print("obj3 = ", obj3.value)