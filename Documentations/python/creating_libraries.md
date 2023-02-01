# Creating Libraries

To create your own library in Python, you will need to follow these steps:

Create a directory for your library. This directory should contain all of the Python modules (i.e., .py files) that make up your library, as well as any other files (e.g., documentation, tests, etc.) that are part of your library.

Define your library's API (Application Programming Interface). This is the set of classes, functions, and variables that you want to expose to users of your library. You should define these in the top-level modules of your library, so that they can be imported directly.

Write documentation for your library. This can include a README file, API documentation, and examples of how to use your library.

Test your library. You should write unit tests for your library to ensure that it is correct and reliable.

Package your library. You can use the setup.py script and the distutils module to create a distribution package for your library. This will allow users to install your library using the pip command.

Here is an example setup.py script for a simple library called mylib:

```python
from distutils.core import setup

setup(
    name='mylib',
    version='1.0',
    py_modules=['mylib'],
    )
```

To create the distribution package for your library, run the `python setup.py sdist` command. This will create a `tar.gz` file containing your library in the `dist` directory.

To install your library, users can run the `pip install /path/to/mylib.tar.gz` command. This will install your library and make it available for import in their Python programs.

Alternatively, you can use tools like setuptools or poetry to package and distribute your library. These tools provide additional features and automation to make it easier to create, publish, and manage Python libraries.

## Libraries with multiple modules:

Here is an example of a Python library that has different folders for different classes:

```python
library/
    __init__.py
    module1/
        __init__.py
        class1.py
        class2.py
    module2/
        __init__.py
        class3.py
        class4.py
```

In this example, the library has two modules: module1 and module2. Each module has its own __init__.py file and one or more class files. The __init__.py file is used to initialize the module and can contain code to import the classes within the module.

For example, the module1/__init__.py file might contain the following code to import class1 and class2:

```python
from .class1 import Class1
from .class2 import Class2
```

This allows you to use the classes in your code like this:

```python
from library.module1 import Class1, Class2

class1 = Class1()
class2 = Class2()
```
## Big Example:

For each folder inside of the library you can have different python files with different classes, but you always need to have one __init__.py file to your folder be recognize as packgage. So it would look like this:

```python
#__init__.py
from .mylib2 import mylib2
from .mylib2 import mylib2_2

#mylib2.py
class mylib2:
    def __init__(self, value):
        self.value = value
    def printer(self):
        print(self.value)

class mylib2_2:
    def __init__(self, value):
        self.value = value
    def printer2(self):
        print(self.value * 2)
```

you can also have files just in the main root folder. Even for that files you will need to have one __init__.py file

```python
#mylib
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
        

#__init__
from .mylib import MyClass
```



