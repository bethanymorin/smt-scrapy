.phony: build run

run: build
	docker run -it --rm -v ${PWD}:/app industrydive/smt-scrapy

build:
	docker build -t industrydive/smt-scrapy .
