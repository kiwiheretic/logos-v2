# README #

This is the Logos-V2 project, a Django/Twisted IRC bot  originally based (in concept) on the  [CancelBot Project](http://cancelbot.sourceforge.net/home.html), but no longer shares any code (except for a few lines) with the original project.  No longer binds to XChat but is completely self contained.  Is cross platform and supports Centos, Ubuntu & Windows.  (Basically anywhere Django, Twisted and Python 2.7 is supported)  Released under the Apache License.

### Features ###

Features include:
  * Everything (or mostly) is designed as a plugin
  * Compatible with CancelBot bible translations.
  * Simple bible verse lookups
  * Fast concordance searches
  * Strongs number lookups
  * Optional Django webserver for setup (work in progress)
  * Plugin architecture for extending bot
  * Written in Python using Twisted and Django frameworks


### Summary of set up for Linux ###

#### Centos ####
```bash
# yum groupinstall "Development Tools"
# yum install python-devel
# yum install python-pip
```

As normal user ...

```bash
$ git clone https://github.com/kiwiheretic/logos-v2.git ~/logos2
$ cd ~/logos2
$ virtualenv ~\venvs\logos2
$ source ~\venvs\logos2\bin\activate

$ pip install -r requirements.txt
$ python manage.py syncdb
$ python manage.py syncdb --database=bibles
$ python manage.py syncdb --database=settings
$ python manage.py import
```

#### Ubuntu ####
```bash
$ sudo apt-get install python-dev python-pip build-essentials
$ sudo pip install virtualenv
$ virtualenv ~\venvs\logos2
$ source ~\venvs\logos2\bin\activate

$ git clone https://github.com/kiwiheretic/logos-v2.git ~/logos2
$ cd ~/logos2
$ pip install -r requirements.txt
$ python manage.py syncdb
$ python manage.py syncdb --database=bibles
$ python manage.py syncdb --database=settings
$ python manage.py import
```

### Summary of set up for Microsoft Windows ###

* Download Python 2.7 from [https://www.python.org/downloads/windows/](Python 2.7 for Windows)  
* [Install get-pip.py](https://bootstrap.pypa.io/get-pip.py) to computer and run it from python. 
* Change into project directory

```
python get-pip.py
pip install virtualenv
mkdir ..\venvs
virtualenv ..\venvs\logos2
..\venvs\logos2\Scripts\activate

pip install -r requirements.txt
manage.py syncdb
manage.py syncdb --database=bibles
manage.py syncdb --database=settings
manage.py import
```

The last import command may need to be run several times if a 
MemoryError results.  Import automatically continues where left off.
Haven't yet tracked down what causes this.

### Extending the bot ###

See the [wiki](https://github.com/kiwiheretic/logos-v2/wiki) for more details.

### Dependencies ###

Currently ...
  * Twisted 14.0
  * Django 1.7
  * Python 2.7
  * django-registration-redux 1.1
  * psutil 2.1.3
  * zope.interface 4.1.1

See the requirements.txt file in the source tree for most up to date information.

### Database configuration ###

Very little.  Uses sqlite3.

### How to run tests ###

Ummm .... still trying to figure out what constitutes a good test given the unpredictability and potential laggyness of IRC servers in general.

### Deployment instructions ###

As above

### Contribution guidelines ###

### Writing tests ###

Open to suggestions

* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin

kiwiheretic (at) myself (dot) com
