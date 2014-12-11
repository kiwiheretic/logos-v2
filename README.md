# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Quick summary

Project is loosely based on the [CancelBot Project](http://cancelbot.sourceforge.net/home.html)
Has been in private development since at least mid 2014 and only in Dec 2014 
released publicly on GitHub.  Is compatible with CancelBot bible translations.

Features include:
  * Simple bible verse lookups
  * Fast concordance searches
  * Strongs number lookups
  * Optional Django webserver for setup (in progress)
  * Plugin architecture for extending bot
  * Written in Python using Twisted and Django frameworks


* Version

Version 0.90

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