## Installation
```
$ git clone git@github.com:Dddarknight/questions.git
$ cd questions
$ make install
$ touch .env

To get SECRET_KEY for Django app:
$ python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> get_random_secret_key()

Then add new SECRET_KEY to .env file

$ make run
```