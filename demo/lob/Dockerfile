FROM python:3
COPY app/ /
COPY requirements.txt /
RUN pip install -r requirements.txt
EXPOSE 8088
CMD [ "python", "-u", "server.py" ]
