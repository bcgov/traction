FROM python:3.10-slim-buster

WORKDIR /app
ENV ENDORSER_API_PORT=5000
COPY requirements.txt requirements.txt

RUN apt-get update && \ 
  apt-get install gcc python3-dev -y

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE ${ENDORSER_API_PORT}
ENTRYPOINT ["./docker-entrypoint.sh"]