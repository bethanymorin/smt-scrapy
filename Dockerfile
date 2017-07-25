FROM python:2.7

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt

COPY . /app/

CMD ["/app/smt-scrapy", "--help"]
