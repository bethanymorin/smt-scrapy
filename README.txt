Get Started:
create and activate a python virtual environment
pip install -r requirements.txt

Configuration:
This script requires you to be able to connect to the source
database of SMT drupal site. The easiest way to do this is
using platform.sh. Once you have this set up on your computer,
you can open up a connection to the database using:

$ platform tunnel:open

Update the values in scraper/db_settings.py if needed to match
the port number, host, user, or database name. But you shouldn't
need to do this.

Run the script:
The process is broken up into two spiders - one for stories
and one for authors.

The stories spider will query a drupal database for URLs of
pubished story posts to parse. These will be fed to the spider
as the "start_urls" value.

The authors spider, which must be run after the stories script,
will parse the output file of the stories spider and gather the
contributor URLs from that to use as the "start_urls" value.

This process is captured in the crawl_smt.py python script,
which executes the scrapy commands in the proper order, and then
outputs some information about what it did. It will save files
in output/stories.jl and output/authors.jl.

So, basically, all you need to do is:

python crawl_smt.py
