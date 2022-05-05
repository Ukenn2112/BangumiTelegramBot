FROM python:3.9-slim-bullseye

RUN apt-get update -yq && \
    apt-get install -yq curl

WORKDIR /app

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock

RUN pip install pipenv
RUN pipenv install --deploy

COPY model /app/model
COPY plugins /app/plugins
COPY templates /app/templates
COPY utils /app/utils
COPY bot.py /app/bot.py
COPY oauth.py /app/oauth.py

VOLUME ["/app/config.py", "/app/data"]

CMD pipenv run
