FROM python:3.8
RUN useradd -u 1000 -d /app -M -s /bin/false app \
	&& pip install poetry gunicorn
ENV POETRY_VIRTUALENVS_CREATE=false
ENV DEBUG=false

COPY . /app/
WORKDIR /app/
RUN poetry install --no-dev --no-interaction \
	&& python manage.py collectstatic --no-input

USER 1000
CMD ["gunicorn", "--access-logfile", "-", "--error-logfile", "-", "-b", "0.0.0.0:8080", "-t", "300", "--threads", "16", "send.wsgi:application"]
