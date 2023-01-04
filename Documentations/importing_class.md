# Importing Class

## Importing

### Using Sys Path
Yes, you can use the sys.path.append() function multiple times to add multiple paths to the sys.path list. For example:

```python
import sys
sys.path.append('/path/to/folder1')
sys.path.append('/path/to/folder2')

from file1 import MyClass1
from file2 import MyClass2

obj1 = MyClass1(10)
print(obj1.value)

obj2 = MyClass2(20)
print(obj2.value)
```

In this example, we have added the paths to the folders containing the file1.py and file2.py files to the sys.path list using the sys.path.append() function. This allows us to import the MyClass1 class from the file1.py file and the MyClass2 class from the file2.py file using the from file1 import MyClass1 and from file2 import MyClass2 statements, respectively.

Alternatively, you can use the PYTHONPATH environment variable to specify a list of directories to search for Python modules, separating the directories with colons on Unix-like systems (including Linux and macOS) or semicolons on Windows. For example:

```python
export PYTHONPATH=$PYTHONPATH:/path/to/folder1:/path/to/folder2
```
This will allow you to import the MyClass1 and MyClass2 classes from the file1.py and file2.py files using the from file1 import MyClass1 and from file2 import MyClass2 statements as usual

### Using Modules

Yes, you can use the from module import class syntax to import a class from a module located in a subfolder.

For example, suppose you have the following directory structure:

```python
root/
    folder1/
        folder2/
            file1.py
    main.py
```    

In this case, you can import the MyClass1 class from the file1.py module located in the folder1/folder2 subfolder like this:

```python
from folder1.folder2.file1 import MyClass1

obj = MyClass1(10)
print(obj.value)
```

Alternatively, you can use the import statement to import the module, and then use the dot notation to access the class within the module:

```python
import folder1.folder2.file1

obj = folder1.folder2.file1.MyClass1(10)
print(obj.value)
```

### Big Example:

```python
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
```

files structures

<img width="138" alt="image" src="https://user-images.githubusercontent.com/72768576/210576688-6d698590-bab0-433c-8296-59449e6c210d.png">

example of class>

```python
class MyClass1:
    def __init__(self, value):
        self.value = value
```







