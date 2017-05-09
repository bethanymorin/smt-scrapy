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
pubished story posts to parse. These URLs will be printed to
a local HTML file, the location of which will then be fed
to the Scrapy Spider as the value of start_urls.

The authors spider, which must be run after the stories script,
will parse the output file of the stories spider and gather the
contributor URLs from the stored stories. These URLs will be
printed to a local HTML file, the location of which will then
be fed to the Scrapy Spider as the value of start_urls.

This process is captured in the crawl_smt.py python script,
which executes the scrapy commands in the proper order, and then
outputs some information about what it did.

You can give this script a couple of arguments:
--limit: sets given limit the returned number of rows from the SMT database
	* if not set, this defaults to 1000, due to the size of the SMT database

--offset: sets given offset the returned number of rows from the SMT database
	* if not set, defaults to 0

These two settings can be combined in order to break the whole export process
up into manageable chunks. For example:

	$ python crawl_smt.py --limit=100
	[......output.....]
	$ python crawl_smt.py --limit=100 --offset=100
	[......output.....]
	$ python crawl_smt.py --limit=100 --offset=200

	etc.

For each run, a subdirectory will be created in output (if it does not already
exist) named for the start and end rows of the batch it will export, based on
the given limit and offset. You will end up with an output directory that
looks something like:

- pwd/
	- output/
		- 0-5000/
			- authors.jl
			- stories.jl
		- 10000-15000/
			- authors.jl
			- stories.jl
		- 15000-20000/
			- authors.jl
			- stories.jl
		- 20000-25000/
			- authors.jl
			- stories.jl
		[....etc.]
