FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN apk add --no-cache gcc musl-dev libffi-dev sqlite sqlite-dev && \
		pip install --upgrade pip && \
		pip install pipenv

WORKDIR /api

COPY Pipfile Pipfile.lock /api/

RUN pipenv install --deploy --ignore-pipfile --python 3.10

COPY . /api/

RUN pipenv run python artisan.py db:migrate

EXPOSE 8000

CMD ["pipenv", "run", "serve"]
