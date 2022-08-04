FROM node:16-alpine
WORKDIR /usr/src/app
COPY . .
# install libs...
RUN npm ci && npm cache clean --force && npm install -g typescript && cd frontend && npm ci
# build frontend and node server
RUN npm run build
# these are not needed now, save some space
RUN rm -rf frontend/node_modules


EXPOSE 8080
CMD [ "node", "dist/src/index.js" ]