from ubuntu:18.04

MAINTAINER Sebastian Strajan "strajan.sebastian@yahoo.com"

RUN apt update && apt install -y python-pip

# avoid reinstalling requirements at each code change
RUN mkdir /app
COPY webapp/requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt

COPY webapp /app

CMD python /app/main.py
