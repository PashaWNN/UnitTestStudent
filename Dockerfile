FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Python requirements
COPY requirements.txt /app/

# Build packages
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

COPY ./ /app/

RUN chown -R root:root /app

CMD gunicorn main.wsgi:application -c /app/gunicorn.conf.py
