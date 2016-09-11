# README #

### Preamble ###

Several years ago was looking for an IRC bot that I could run anywhere.  Some required mIRC, others required XChat, others would only run on Linux, and some would run only on Windows.  This bot is my solution to that problem.

### History ###

This is the Logos-V2 project, a Django/Twisted IRC bot  originally based (in concept) on the [CancelBot Project](http://cancelbot.sourceforge.net/home.html), but no longer shares any code (except for a few lines) with the original project.  No longer binds to XChat but is completely self contained. Is cross platform and supports Centos, Ubuntu & Windows.  (Basically anywhere Django, Twisted and Python 2.7 is supported).  Released under the Apache License.

### Features ###

Features include:
  * Fine grained permission system based on Django-guardian (new feature)
  * User and developer documentation on [wiki](https://github.com/kiwiheretic/logos-v2/wiki)
  * Written in Python using Twisted and Django frameworks
  * Compatible with CancelBot bible translations
  * Easy to customise for your own personalised bot
  * Everything (or mostly) is designed as a plugin
  * Plugin architecture for extending bot

Plugins:
  * Cloud Memos - just like a web based MemoServ
  * [Cloud Notes](https://biblebot.wordpress.com/cloud-notes/) system accessible from web and IRC.  Useful for storing bible notes.
  * Atom+RSS Feed plugin for room news feed
  * Twitter Plugin for room news feed from Twitter
  * Google Calendar access
  * Symbolic Computations from IRC (uses SymPy)  (**coming soon**)

Bible Plugin:
  * Simple bible verse lookups
  * Fast concordance searches
  * Strongs number lookups

Memos Plugin
  * Works like MemoServ with a web interface.

Notes Plugin
  * A note system with hash tags accessible via web or IRC.
  * Web interface is extremely lightweight and mobile friendly.
  * Mobile note upload integrates well with [OI File Manager](https://play.google.com/store/apps/details?id=org.openintents.filemanager&hl=en)

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
$ virtualenv ~/venvs/logos2
$ source ~/venvs/logos2/bin/activate

$ pip install -r requirements.txt

```
If you want to use the email registration edit the email_settings.py file and
put in valid settings for your email server.  If not, then just copy the file email_settings-dist.py to email_settings.py in order to suppress any errors.
```
$ cp logos/email_settings-dist.py logos/email_settings.py
$ cp allowed_hosts-dist.txt allowed_hosts.txt
$ python manage.py migrate
$ python manage.py migrate --database=bibles
$ python manage.py import
```

#### Ubuntu ####
```bash
$ sudo apt-get install python-dev python-pip build-essentials
$ sudo apt-get install libxml2-dev libxslt1-dev
$ sudo apt-get install zlib1g-dev
$ sudo pip install virtualenv
$ virtualenv ~/venvs/logos2
$ source ~/venvs/logos2/bin/activate

$ git clone https://github.com/kiwiheretic/logos-v2.git ~/logos2
$ cd ~/logos2
$ pip install -r requirements.txt
```
If you want to use the email registration edit the email_settings.py file and
put in valid settings for your email server.  If not, then just copy the file email_settings-dist.py to email_settings.py in order to suppress any errors.
```
$ cp logos/email_settings-dist.py logos/email_settings.py
$ cp allowed_hosts-dist.txt allowed_hosts.txt
$ python manage.py migrate
$ python manage.py migrate --database=bibles
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
manage.py migrate
manage.py migrate --database=bibles
manage.py import
```

### Admin Permission System ###

It is now possible to set up individual users with very specific permissions (thanks to [Django Guardian](https://django-guardian.readthedocs.org/en/v1.2/) permission system).

First you will need to add your own nick as user replacing &lt;username&gt;, &lt;email&gt; and &lt;password&gt; with the appropriate information.
```
$ python manage.py admin adduser <username> <email> <password>
$ python manage.py admin assignperm <irc-server> '#' <username> bot_admin
```
(The '#' indicates that this command refers to the whole IRC network, not just any room.)  Now when you login you type on IRC network (preferrable in private window to the bot) something like the following:

```
/nick <username>
!login <password>
```
You can change your own password later on with:
```
!set password <newpassword>

To activate the bible plugin you need to...
!activate plugin bible
!enable plugin #yourRoom bible

The same goes for any other plugins you wish to use.  Replace the word "bible" 
with the plugin ID of the plugin you wish to enable.
```
Again this should be done in a private window to bot for security reasons.
See the [wiki](https://github.com/kiwiheretic/logos-v2/wiki) for more details.

### Developing or modifying the bot ###
See the [wiki](https://github.com/kiwiheretic/logos-v2/wiki) for more details.

# Using the Website #
For working with the website you need to copy the file _allowed_hosts-dist.txt_ 
to _allowed_hosts.txt_ and add in your domain name (or ip address) to the list.  
If you have more than one domain name add one per line.  If this step is missed
or forgotten your web browser will receive a 400 error.

If running on the development server (ie: python manage.py runserver) then 
you need to add your computer's hostname.  To find your hostname simply run the following from a python shell:

```python
import socket
print socket.gethostname()
```

Put this in the file debug_hosts.txt and place that file in the logos\ folder.
