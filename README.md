# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### Summary of set up for Linux ###

To be written

### Summary of set up for Microsoft Windows ###

* Download Python 2.7 from [https://www.python.org/downloads/windows/](Python 2.7 for Windows)  
* [Install get-pip.py](https://bootstrap.pypa.io/get-pip.py) to computer and run it from python. 
* Change into project directory
```
python get-pip.py
pip install virtualenv
mkdir \venvs
virtualenv \venvs\logos2
\venvs\logos2\Scripts\activate

pip install -r requirements.txt
manage.py syncdb
manage.py syncdb --database=bibles
manage.py syncdb --database=settings
manage.py import
```

The last import command may need to be run several times if a 
MemoryError results.  Import automatically continues where left off.
Haven't yet tracked down what causes this.

* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact