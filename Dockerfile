FROM python:3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app/

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system