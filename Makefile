.phony: build crawl

crawl: |build nodes.json urls.txt
	docker run -it --rm -p 6023 -v ${PWD}:/app industrydive/smt-scrapy scrapy crawl stories

build:
	docker build -t industrydive/smt-scrapy:latest .

nodes.json: pull-data

urls.txt: pull-data

pull-data: build
    docker run -it --rm -v ${PWD}:/app industrydive/smt-scrapy ./pull-data
