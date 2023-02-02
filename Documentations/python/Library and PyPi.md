# Creating a Library and deploying it into PyPi

## Creating a Library
In your environment, make sure you have pip installed wheel, setuptools and twine. We will need them for later to build our Python library.
> pip install wheel
> pip install setuptools
> pip install twine

Make sure that you have the following structure:

```
\mylibfolder
--\setup.py
--\README.md
--\mylib
-----\__init__.py
-----\code1.py
-----\code2.py
```

- The `setup.py` is the file used to build your library 
- `mylib` is the module of your library (that's why it needs to have the file `__init__.py` to say that this is a module)
- `code1.py` and `code2.py` are the codes of your library

To build your library you should run the following comand in the root of your library folder>

`python setup.py bdist_wheel`

The `setup.py` should have simething like this>

```python
from setuptools import find_packages, setup

setup(
    name='dtwinpy',
    packages=find_packages(),
    version='0.0.2.4',
    description='Digital Twin Library',
    long_description = open("README.md").read(),
    author='Pedro Bacelar and Alex',
    license='MIT'
)

```

In this case we are using `find_packages()`, which means that all the folders with `__init__.py` will be add to you library and the other folders will ignored, so take care about it.

> It's important to say that what you're going to import is the module's name and not the library name, so it's recomended to have a main module folder with the same name as the library, so you will be kind of importing the library name!

After running this, 3 new folders will appear in the root of your library:
- build
- `dist` (very important, this where the package of your library is stored)
- mylib.egg-info

### Manually installing the library

In order to munually install the library you just need the path of the file generated within the folder "dist" (`dist\dtwinpy-0.0.2.4-py3-none-any.whl`).
Next you just use the normal commands to install a library using pip or pipenv:

`pip install "dtwinpylib\dist\dtwinpy-0.0.2.4-py3-none-any.whl"`

## Deploying it on PyPi

You need to follow the steps:
1. Create an account in PyPi
2. Create an token in PyPi (scroll down in setting and will have an option to create an API token)
3. In the home folder (`C:User\username\`) create the file `.pypirc` (it's better to create this file using VS Code):

```python
[distutils]
index-servers =
  pypi

[pypi]
username= __token__
password= <API Token>
```
4. Run the following command>

`python -m twine upload dist/*`

Some observations:
- If it's the first time of the day uploading to pip you should enter your username and also password
- You can specify what package are you upload by change the termination like this: `dist/dtwinpy-0.0.2.4-py3-none-any.whl`

5. After this you're finished, you can already check in the oficial site of PyPi your library and download it as well just using the normal command of pip `pip install mylib`

## Maintainance

- After any final change in the code just run: `python setup.py bdist_wheel`
- To upload the change, just run: `python -m twine upload dist/*`


## References:
- https://medium.com/analytics-vidhya/how-to-create-a-python-library-7d5aea80cc3f
- https://laxmena.com/posts/publish-pip-package
