# README #

This is the Logos-V2 project, a Django/Twisted IRC bot  originally based (in concept) on the [CancelBot Project](http://cancelbot.sourceforge.net/home.html), but no longer shares any code (except for a few lines) with the original project.  No longer binds to XChat but is completely self contained. Is cross platform and supports Centos, Ubuntu & Windows.  (Basically anywhere Django, Twisted and Python 2.7 is supported).  Released under the Apache License.

### Features ###

Features include:
  * Written in Python using Twisted and Django frameworks
  * Compatible with CancelBot bible translations
  * Easy to customise for your own personalised bot
  * Optional Django webserver for setup (work in progress)
  * Fine grained permission system based on Django-guardian (new feature)

Plugins:
  * Everything (or mostly) is designed as a plugin
  * Plugin architecture for extending bot

Bible Plugin:
  * Simple bible verse lookups
  * Fast concordance searches
  * Strongs number lookups
  
### Summary of set up for Linux ###

#### Centos ####
```bash
# yum groupinstall "Development Tools"
# yum install python-devel
# yum install python-pip
```

As normal user ...

```
$ git clone https://github.com/kiwiheretic/logos-v2.git ~/logos2
$ cd ~/logos2
$ virtualenv ~\venvs\logos2
$ source ~\venvs\logos2\bin\activate

$ pip install -r requirements.txt

```
If you want to use the email registration edit the email_settings.py file and
put in valid settings for your email server.  If not, then just copy the file email_settings-dist.py to email_settings.py in order to suppress any errors.
```
$ cp logos/email_settings-dist.py logos/email_settings.py
$ python manage.py syncdb
$ python manage.py syncdb --database=bibles
$ python manage.py syncdb --database=game-data
$ python manage.py syncdb --database=settings
$ python manage.py loaddata --database=game-data scriptures.json
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
```
If you want to use the email registration edit the email_settings.py file and
put in valid settings for your email server.  If not, then just copy the file email_settings-dist.py to email_settings.py in order to suppress any errors.
```
$ cp logos/email_settings-dist.py logos/email_settings.py
$ python manage.py syncdb
$ python manage.py syncdb --database=bibles
$ python manage.py syncdb --database=settings
$ python manage.py syncdb --database=game-data
$ python manage.py loaddata --database=game-data scriptures.json
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
```
If you want to use the email registration edit the email_settings.py file and
put in valid settings for your email server.  If not, then just copy the file email_settings-dist.py to email_settings.py in order to suppress any errors.
```
copy logos/email_settings-dist.py logos/email_settings.py
manage.py syncdb
manage.py syncdb --database=bibles
manage.py syncdb --database=settings
manage.py syncdb --database=game-data
manage.py loaddata --database=game-data scriptures.json
manage.py import
```

### Admin Permission System ###

It is now possible to set up individual users with very specific permissions (thanks to [Django Guardian](https://django-guardian.readthedocs.org/en/v1.2/) permission system).

First you will need to add your own nick as user replacing &lt;username&gt;, &lt;email&gt; and &lt;password&gt; with the appropriate information.
```
$ python manage.py admin adduser <username> <email> <password>
$ python manage.py admin assignperm <irc-server> '#' <username> net_admin
```
(The '#' indicates that this command refers to the whole IRC network, not just any room.)  Now when you login you type on IRC network (preferrable in private window to the bot) something like the following:
```
/nick <username>
!login <password>
```
You can change your own password later on with:
```
!set password <newpassword>
```
Again this should be done in a private window to bot for security reasons.
See the [wiki](https://github.com/kiwiheretic/logos-v2/wiki) for more details.

### Developing or modifying the bot ###
See the [wiki](https://github.com/kiwiheretic/logos-v2/wiki) for more details.


