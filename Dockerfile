FROM python:3

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN apt update \
    && apt install sqlite3 \
    && pip install -r requirements.txt \
    && python manage.py makemigrations \
    && python manage.py migrate
COPY ./ /code/

CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000"]
