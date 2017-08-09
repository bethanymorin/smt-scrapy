FROM python:3.6.2-stretch

RUN mkdir /app

WORKDIR /app

EXPOSE 6023

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt

COPY . /app/

CMD ["scrapy", "crawl", "socialmediatoday"]
