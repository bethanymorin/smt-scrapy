# SMT scrapy
This pulls user and node data from Social Media Today.


## Running locally

This is setup to run in a docker container. If you're in a place with a docker runtime, simply run:

````
make
````

and it will build the image locally and run the crawl. Afterwards the results will be in the `feeds` directory.

If you're developing this code, hop the container with the following:

````
docker run -it --rm -v ${PWD}:/app industrydive/smt-scrapy:latest bash
````

and run `scrapy` things to your heart's content.


## Scrapinghub Cloud

This runs on Scrainghub Cloud which is much much better and more useful than running locally when you're not developing for the code.
