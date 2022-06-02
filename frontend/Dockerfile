FROM node:18

WORKDIR /usr/src/frontend

COPY package.json yarn.lock ./

RUN yarn

COPY . ./