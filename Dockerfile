FROM node:8-alpine as react-pkg
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh dumb-init
USER node
COPY --chown=node:node exampleproject/webpack.config.js exampleproject/.babelrc /exampleproject/
COPY --chown=node:node exampleproject/package.json exampleproject/package-lock.json /exampleproject/
RUN cd /exampleproject && npm install
COPY --chown=node:node exampleproject/frontend/assets /exampleproject/frontend/assets
RUN cd /exampleproject && npm run build
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

FROM python:3.6-alpine
ARG user_id=1000

RUN adduser -D -u $user_id exampleproject && \
    mkdir /exampleproject && \
    chown exampleproject:exampleproject /exampleproject

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN apk update && apk add dumb-init postgresql-dev postgresql-client gcc python3-dev musl-dev jpeg-dev zlib-dev

COPY requirements.txt /exampleproject/requirements.txt
RUN pip install -r /exampleproject/requirements.txt

COPY --chown=exampleproject:exampleproject ./exampleproject/ /exampleproject/
COPY --chown=exampleproject:exampleproject config/entrypoint-*.sh /entry/
COPY --chown=exampleproject:exampleproject run_tests.sh /exampleproject/
COPY --from=react-pkg /exampleproject/frontend/assets/bundles/main.js /exampleproject/frontend/bundles/main.js
COPY --from=react-pkg /exampleproject/webpack-stats.json /exampleproject


RUN mkdir -p /static && chown exampleproject:exampleproject /static
RUN mkdir -p /reports && chown exampleproject:exampleproject /reports

USER exampleproject
WORKDIR /exampleproject
ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
