# Build the frontend Vue app with usual vue cli build
# Vue Build Container
FROM node:16.13.0-alpine as VUE
WORKDIR /frontend
COPY frontend .
RUN npm install && npm run build

FROM python:3.10

WORKDIR /app

COPY --from=VUE /frontend/dist /app2/dist
COPY --from=VUE /frontend/dist ./dist
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .


EXPOSE 5000
ENTRYPOINT ["./docker-entrypoint.sh"]