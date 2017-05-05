rm *.jl
scrapy crawl stories --output=smt_stories.jl --output-format=jsonlines
scrapy crawl authors --output=smt_authors.jl --output-format=jsonlines
