FROM python:3

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY ./ /code/
RUN apt-get update \
    && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install sqlite3 -y \
    && pip install -r requirements.txt \
    && python manage.py makemigrations \
    && python manage.py migrate

CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000"]
