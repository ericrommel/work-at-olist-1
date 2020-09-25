Work at Olist - Challenge
======

This is an implement of a simple application for a library to store book and authors data.
This application provides an HTTP REST API to attend the requirements.

[![Build Status](https://travis-ci.com/ericrommel/work-at-olist-1.svg?branch=master)](https://travis-ci.com/github/ericrommel/work-at-olist-1)
[![codecov](https://codecov.io/gh/ericrommel/work-at-olist-1/branch/master/graph/badge.svg)](https://codecov.io/gh/ericrommel/work-at-olist-1)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)


Requirements
======

- [Python 3](http://python.org/)
- [Pip](https://pip.pypa.io/)
- [Flask](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite](http://sqlite.org/) (or any other supported database)

These are optional but recommended.

- [Codecov](http://codecov.io/)
- [Flake8](http://flake8.pycqa.org/)
- [Pipenv](http://pipenv.readthedocs.io)
- [Pre-commit](http://pre-commit.com/)

Brief description
-------
This project was written using:
- OS: Windows 10 PRO in an Asus laptop (Intel i7 8GB, NVIDIA 256GB dedicated)
- [PyCharm Community](https://www.jetbrains.com/pycharm/download/#section=windows) 2020.2
- CI/CD with [Travis](https://travis-ci.com/)
- Deployed at [Heroku](https://www.heroku.com/)
- Code coverage with [Codecov](https://codecov.io/)

Installing
-------

The default Git version is the master branch. ::

    # clone the repository
    $ cd desired/path/
    $ git clone https://github.com/ericrommel/work-at-olist-1


The next step is install the project's Python dependencies. Just like _Git_ if you still don't have it go to the [official site](http://python.org/) and get it done. You'll also need [Pip](https://pip.pypa.io/), same rules applies here.  It is strongly recommended to use a virtual environment before install the dependencies. You can check how you can do that [here](https://docs.python.org/3/library/venv.html#creating-virtual-environments).
Another interesting tool that is not required but strongly recommended is [Pipenv](http://pipenv.readthedocs.io), it helps to manage dependencies and virtual environments.

Installing with **Pip**:

    $ cd path/to/work-at-olist-project
    $ pip install -r requirements.txt

Installing with **Pipenv**:

    $ pip install --upgrade pipenv
    $ cd path/to/work-at-olist-project
    $ pipenv sync -d

All packages used in this project will be installed.

Run
---
Before run the application, you need to configure the application. This will require you to define a few variables and create the database.

Set the environment variables::

    $ export FLASK_APP=src
    $ export FLASK_ENV=development

Or on Windows cmd::

    > set FLASK_APP=src
    > set FLASK_ENV=development

Create the database::

    $ flask db init
    $ flask db migrate
    $ flask db upgrade

Run the application::

    $ flask run

Open http://127.0.0.1:5000 in a browser.


Tests
----

From Postman::
- Import the collection file: postman/
- Import the environment file: postman/
- Click on Runner button
- Select the collection imported
- Select the environment imported
- Click on Run button

From Python code tests (unit tests)::

    $ cd path/to/work-at-olist-project
    $ pytest

Run with coverage report::

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser

About
======
This project is part of the Work-at-Olist challenge.

Author
======
- [Eric Dantas](https://www.linkedin.com/in/ericrommel)