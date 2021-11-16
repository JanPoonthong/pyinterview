FROM python:3
MAINTAINER Jan Poonthong "janpoonthong628@gmail.com"

ENV PYTHONUNBUFFERED=1
ENV DEBUG 0

WORKDIR /code
COPY requirements.txt /code/
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
COPY . /code/

# collect static files
RUN python manage.py collectstatic --noinput

RUN python manage.py makemigrations
RUN python manage.py migrate --run-syncdb
