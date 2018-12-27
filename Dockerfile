FROM node:8-alpine as react-pkg
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh dumb-init
USER node
COPY --chown=node:node ohqueue/jest-setup.js ohqueue/jest.config.js ohqueue/webpack.config.js ohqueue/webpack.prod.config.js ohqueue/.babelrc /ohqueue/
COPY --chown=node:node ohqueue/package.json ohqueue/package-lock.json /ohqueue/
RUN cd /ohqueue && npm install
COPY --chown=node:node ohqueue/frontend/assets /ohqueue/frontend/assets
RUN cd /ohqueue && npm run build-production
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

FROM python:3.6-alpine
ARG user_id=1000

RUN adduser -D -u $user_id ohqueue && \
    mkdir /ohqueue && \
    chown ohqueue:ohqueue /ohqueue

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN apk update && apk add dumb-init postgresql-dev postgresql-client gcc python3-dev musl-dev jpeg-dev zlib-dev

COPY requirements.txt /ohqueue/requirements.txt
RUN pip install -r /ohqueue/requirements.txt

COPY --chown=ohqueue:ohqueue ./ohqueue/ /ohqueue/
COPY --chown=ohqueue:ohqueue config/entrypoint-*.sh /entry/
COPY --chown=ohqueue:ohqueue run_tests.sh /ohqueue/
COPY --from=react-pkg /ohqueue/frontend/assets/bundles/main.js /ohqueue/frontend/bundles/main.js
COPY --from=react-pkg /ohqueue/webpack-stats.json /ohqueue


RUN mkdir -p /static && chown ohqueue:ohqueue /static
RUN mkdir -p /reports && chown ohqueue:ohqueue /reports

USER ohqueue
WORKDIR /ohqueue
ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
