# Build the frontend Vue app with usual vue cli build
# Vue Build Container
FROM node:16.13.0-alpine as VUE
WORKDIR /frontend
COPY frontend .
RUN npm install && npm run build

FROM python:3.10
WORKDIR /traction/app
COPY docker-entrypoint.sh docker-entrypoint.sh
COPY alembic.ini alembic.ini
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY api ./api

# vue app goes outside of the app (allows hotloading of app)
COPY --from=VUE /frontend/dist /traction/static

EXPOSE 5000
ENTRYPOINT ["./docker-entrypoint.sh"]