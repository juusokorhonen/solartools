# solartools
Tools for solving solar energy problems.

## Installation

### Install python2.7
$ brew install python

### Install pip
$ easy_install pip

### Install virtualenv and virtualenvwrapper
$ pip install virtualenv virtualenvwrapper

### Make virtualenv
$ mkvirtualenv --no-site-packages solartools

### Switch to new virtualenv
$ workon solartools

### Install python dependencies
$ pip install -r requirements.txt

### Install redis server
$ brew install redis
$ ln -sfv /usr/local/opt/redis/*.plist ~/Library/LaunchAgents
$ launchchtl load ~/Library/LaunchAgents/homebrew.mxcl.redis.plist

### Run solartools
$ python manage.py runserver
