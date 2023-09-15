# Backend API

## Virtual environment
This application uses a python virtual environment to manage dependencies. The environment was created using the following command:
```python -m venv .venv```


## Running the flask application
Execute the following command in the root directory
### 1) Start virtual environment on Windows:
```.\.venv\Scripts\activate```
### 2) Install the dependencies
```pip install -r requirements.txt```
### 3) Set the environment variables
In order for the Flask to detect the application entry, set the following environment variable in your Operating System
#### On Windows:
Run the following
``$env:FLASK_APP = "application.py"``
#### On macOS:
Run the following: ``export FLASK_APP = "application.py"``