.PHONY: build crawl

crawl: |build
	docker run -it --rm -v ${PWD}:/app industrydive/smt-scrapy:latest scrapy crawl socialmediatoday

build:
	docker build -t industrydive/smt-scrapy:latest .
