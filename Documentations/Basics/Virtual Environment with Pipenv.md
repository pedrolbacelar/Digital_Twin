# Virtual Environment with Pipenv

Virtual Environment is good to make sure that you’re using the right libraries in your code and also to not mixed different versions of libraries with different projects using the same library.

To create a virtual environment, follow the steps:

1. Create a folder in your desktop that it’s not include in the github folder or the project folder. You could do this using cmd:

```python
mkdir virtenv
cd virtenv
```

1. Check if you have pipenv installed, if not just intall it:

```python
pip install pipenv
```

1. THIS IS NOT WORKING (14-12-2022) Then initiate the virtual enviorment with the comment (make sure that you are typing in the right directory) (skip if not working):

```python
pipenv –-three
```

1. Start the virtual environment

```python
pipenv shell
```

1. Now you can install any package you want if the comand:

```python
	pipenv install <package_name>
```

### 🚧 Install all packages from a file:

First, within the the virtual environment folder you need to have a .txt file with all the necessaries packages with the versions, like that:

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/2f6c27da-cfe9-460a-830b-5418144a22be/Untitled.png)

Then just run:

```python
pipenv install -r "requirements.txt"
```

If you want to see the libraries used in your virtual environment:

```python
pipenv graph
```

If you want to delete some package, just type:

```python
pipenv uninstall <package_name>
```

## ⚠️ Using the Virtual Environment

If you were with the VS code opened it’s better to restart it before trying to use the new virtual environment.

1. Select to change the python path: **3.9.5(#####)**

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/f3d69fdf-c4d6-4e1f-a5c6-db155b2f8065/Untitled.png)

1. Choose the folder name that you created the virtual environment

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/893e3155-c146-4fe9-a4fe-cc5472a9b1b2/Untitled.png)

## Troubleshoot

- If “*pipenv”* **** function returns error, rewrite the command with following prefix: *python3 -m <*your syntax*>*
