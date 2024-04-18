FROM node:21-alpine
WORKDIR /usr/src/app
COPY . .
# install backend libs
RUN npm cache clean --force && npm ci
# install frontend libs
RUN cd frontend && npm cache clean --force && npm ci
# build backend
RUN npm run build
# build frontend
RUN cd frontend && npm run build
# these are not needed now, save some space
RUN rm -rf frontend/node_modules

EXPOSE 8080
CMD [ "node", "dist/src/index.js" ]