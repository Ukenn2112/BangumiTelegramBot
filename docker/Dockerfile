FROM python:3.9-slim-bullseye

RUN apt-get update -yq && \
    apt-get install -yq curl

WORKDIR /app

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock

RUN pip install pipenv
RUN pipenv install --deploy

COPY apiserver /app/apiserver
COPY data /app/data
COPY tgbot /app/tgbot
COPY utils /app/utils
COPY main.py /app/main.py

VOLUME ["/app/data/config.yaml", "/app/data"]

CMD pipenv run
