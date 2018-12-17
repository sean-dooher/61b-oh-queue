FROM node:8-alpine as react-pkg
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh dumb-init
USER node
COPY --chown=node:node django/webpack.config.js django/.babelrc /django/
COPY --chown=node:node django/package.json django/package-lock.json /django/
RUN cd /django && npm install
COPY --chown=node:node django/assets /django/assets
RUN cd /django && npm run build
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

FROM python:3.6-alpine
ARG user_id=1000

RUN adduser -D -u $user_id django && \
    mkdir /django && \
    chown django:django /django

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN apk update && apk add dumb-init postgresql-dev postgresql-client gcc python3-dev musl-dev jpeg-dev zlib-dev

COPY requirements.txt /django/requirements.txt
RUN pip install -r /django/requirements.txt

COPY --chown=django:django ./django/ /django/
COPY --chown=django:django config/entrypoint-*.sh /entry/
COPY --chown=django:django run_tests.sh /django/
COPY --from=react-pkg /django/assets/bundles/main.js /django/assets/bundles/main.js
COPY --from=react-pkg /django/webpack-stats.json /django


RUN mkdir -p /static && chown django:django /static
RUN mkdir -p /reports && chown django:django /reports

USER django
WORKDIR /django
ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
