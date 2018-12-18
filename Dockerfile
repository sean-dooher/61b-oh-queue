FROM node:8-alpine as react-pkg
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh dumb-init
USER node
COPY --chown=node:node example_project/webpack.config.js example_project/.babelrc /example_project/
COPY --chown=node:node example_project/package.json example_project/package-lock.json /example_project/
RUN cd /example_project && npm install
COPY --chown=node:node example_project/frontend/static/assets /example_project/frontend/static/assets
RUN cd /example_project && npm run build
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

FROM python:3.6-alpine
ARG user_id=1000

RUN adduser -D -u $user_id example_project && \
    mkdir /example_project && \
    chown example_project:example_project /example_project

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN apk update && apk add dumb-init postgresql-dev postgresql-client gcc python3-dev musl-dev jpeg-dev zlib-dev

COPY requirements.txt /example_project/requirements.txt
RUN pip install -r /example_project/requirements.txt

COPY --chown=example_project:example_project ./example_project/ /example_project/
COPY --chown=example_project:example_project config/entrypoint-*.sh /entry/
COPY --chown=example_project:example_project run_tests.sh /example_project/
COPY --from=react-pkg /example_project/frontend/static/assets/bundles/main.js /example_project/frontend/static/bundles/main.js
COPY --from=react-pkg /example_project/webpack-stats.json /example_project


RUN mkdir -p /static && chown example_project:example_project /static
RUN mkdir -p /reports && chown example_project:example_project /reports

USER example_project
WORKDIR /example_project
ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
