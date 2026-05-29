FROM python:3.14.5-alpine3.23@sha256:5a824eb82cc75361f98611f3cfc5091ea33f10a6ccea4d4ebdabbc523b9a1614 AS poetry_installed

RUN apk update && apk add --no-cache curl python3-dev libressl-dev gcc libc6-compat rust libc-dev cargo pkgconf py3-openssl

RUN python3 -m pip install poetry poetry-plugin-export

FROM poetry_installed AS requirements_listed

COPY app/pyproject.toml app/poetry.lock ./

RUN poetry export -o requirements.txt

FROM python:3.14.5-alpine3.23@sha256:5a824eb82cc75361f98611f3cfc5091ea33f10a6ccea4d4ebdabbc523b9a1614 AS COMPILE_LAYER

RUN apk update && apk add --no-cache python3-dev build-base linux-headers

WORKDIR /app

COPY --from=requirements_listed requirements.txt ./

RUN python3 -m pip install -r requirements.txt

RUN pip wheel -w /wheels -r requirements.txt

FROM python:3.14.5-alpine3.23@sha256:5a824eb82cc75361f98611f3cfc5091ea33f10a6ccea4d4ebdabbc523b9a1614 AS app

COPY --from=COMPILE_LAYER /wheels /wheels
RUN python3 -m pip install --no-index --find-links=/wheels /wheels/*.whl

WORKDIR /app

COPY ./image/config/wsgi.ini /app/config/wsgi.ini
COPY ./image/config/supervisord.conf /etc/supervisord.conf

COPY ./app /app

RUN python3 -m pip install -e .

ARG DOMAIN
ENV DOMAIN $DOMAIN

CMD ["supervisord"]
