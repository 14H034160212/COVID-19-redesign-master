# COVID-19 Web Application

## Description

A Web application that demonstrates use of Python's Flask framework. The application also makes use of the SQLAlchemy ORM framework, and other libraries such as the Jinja templating library and WTForms. Architectural design patterns including Repository, Service Layer, and Unit of Work have been used to design the application. The application uses Flask Blueprints to maintain a separation of concerns between application functions. Testing includes unit, integration and end-to-end testing using the pytest and coverage tools. 

## Installation

**Installation via requirements.txt**

```shell
$ cd COVID-19
$ py -3 -m venv venv  ## or use "python -m venv venv" 
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

When using PyCharm, set the virtual environment using 'File'->'Settings' and select 'Project:COVID-19' from the left menu. Select 'Project Interpreter', click on the gearwheel button and select 'Add'. Click the 'Existing environment' radio button to select the virtual environment. 

## Execution

**Running the application**

From the *COVID-19* directory, and within the activated virtual environment (see *venv\Scripts\activate* above):

````shell
$ flask run
```` 

## Configuration

The *COVID-19/.env* file contains variable settings. They are set with appropriate values. Only `REPOSITORY` need be changed to toggle between using a memory or database implementation of the repository.

* `FLASK_APP`: Entry point of the application (should always be `wsgi.py`).
* `FLASK_ENV`: The environment in which to run the application (either `development` or `production`).
* `SECRET_KEY`: Secret key used to encrypt session data.
* `SQLALCHEMY_DATABASE_URI`: SQLAlchemy connection URI to a SQL database.
* `TESTING`: Set to False for running the application. Overridden and set to True automatically when testing the application.
* `WTF_CSRF_SECRET_KEY`: Secret key used by the WTForm library.
* `REPOSITORY`: Application variable set to either `memory` or `database` for a memory or database implementation of the repository respectively.


## Testing

Testing requires that file *COVID-19/tests/conftest.py* be edited to set the value of `TEST_DATA_PATH`. You should set this to the absolute path of the *COVID-19/tests/data* directory. 

Using Python on Windows requires the use of \\\ as directory separators. E.g.

`TEST_DATA_PATH = 'C:\\Users\\ian\\python-dev\\COVID-19\\tests\\data'`

You can then run tests from within PyCharm.

To run all tests using pytest from a terminal window running the virtual environment, you should first install the COVID-19 project in the virtual environment. From within the *COVID-19* directory:

````
$ pip install -e .
````

To run all tests within a terminal window, from within the *COVID-19* directory:

```
$ pytest
```

To measure code coverage and generate a HTML report, from within the *COVID-19* directory:

````
$ coverage run -m pytest
$ coverage html
````

The generated report is stored in the *htmlcov* directory. Open the *COVID-19/htmlcov/index.html* file in a Web browser to see the report.
 
