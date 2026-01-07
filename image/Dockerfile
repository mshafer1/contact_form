FROM python:3.14.1-alpine3.21 AS base

RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/America/Chicago /etc/localtime

RUN apk update && apk -U upgrade

# tools to build uwsgi
RUN apk add --no-cache \
    gcc \
    libc-dev \
    linux-headers

RUN python3 -m pip install -U pip supervisor

RUN mkdir /app
WORKDIR /app
RUN mkdir --parent /var/log/uwsgi_email_form /app/contact_form

RUN apk add shadow && groupmod --gid 33 www-data

FROM base AS poetry_installed

RUN python3 -m pip install poetry==2.0.1


COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock
RUN touch /app/contact_form/__init__.py

RUN python3 -m venv /app/venv
RUN . /app/venv/bin/activate && poetry install --only main

FROM base AS app_installed

COPY --from=poetry_installed /app/venv /app/venv

# COPY ./contact_form /app/contact_form
COPY ./image/config/wsgi.ini /app/config/wsgi.ini
COPY ./image/config/supervisord.conf /etc/supervisord.conf


ARG DOMAIN
ENV DOMAIN $DOMAIN

CMD ["supervisord"]
