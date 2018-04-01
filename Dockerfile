# build
# docker build -t slackertracker .

# run
# docker run -dt -p 80:5000 slackertracker
FROM ubuntu:latest
MAINTAINER Team SlackerTracker
EXPOSE 5000

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip

VOLUME /slackertracker/instance
RUN mkdir -p /slackertracker/instance
COPY ./requirements.txt /slackertracker
WORKDIR /slackertracker
RUN pip3 install -r /slackertracker/requirements.txt
COPY . /slackertracker

ENV FLASK_APP manage.py
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

CMD flask db upgrade && flask run --host=0.0.0.0

