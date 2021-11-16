# Pynai

## Requirements

### Linux & MacOS

Prerequisites:

- [Python][python-download]
- [Django][django-download]
- [Docker][docker-download]

Instructions for doing locally:

1.  Download pip (only for linux):

        $ sudo apt install python3-pip

1.  Download Django:

        $ pip3 install -r requirements.txt

1.  Run:

        $ cd pyinterview/
        $ ./manage.py migrate --run-syncdb
        $ ./manage.py runserver

        or

        $ cd pyinterview/
        $ python3 manage.py migrate --run-syncdb
        $ python3 manage.py runserver

Instructions for doing in Docker and Docker Compose:

        $ python3 manage.py migrate --run-syncdb && sudo docker-compose build && sudo docker-compose up

Check http://127.0.0.1:8000/ or http://localhost:8000/

### Windows

Prerequisites:

- [Python][python-download]
- [Django][django-download]
- [Docker][docker-download]

Instructions:

1.  Download Django:

        $ pip3 install -r requirements.txt

1.  Run:

        $ cd pyinterview
        $ python manage.py migrate --run-syncdb
        $ python manage.py runserver

        or

        $ cd pyinterview
        $ python3 manage.py migrate --run-syncdb
        $ python3 manage.py runserver

After doing `python3 manage.py runserver`, check http://127.0.0.1:8000/ or http://localhost:8000/

[django-download]: https://www.djangoproject.com/download/
[python-download]: https://www.python.org/downloads/
[docker-download]: https://docs.docker.com/engine/install/
