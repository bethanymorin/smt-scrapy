# SMT scrapy
This is a set of scripts for pulling some data out of the SMT database and 
scraping data from the site itself in order to get the node and author data 
that we want.

There are two phases to this. The first phase is to get the data and urls to 
crawl out of the database and into some files. The second phase is to use 
those files to crawl and scrape pages and output the combined data for nodes 
and authors.


## Get Started

Create and activate a python virtual environment. Then install the requirements.

````
pip install -r requirements.txt
````


## Configuration
For the first phase you need to be able to connect to the source database.
The easiest way to do this is to tunnel with platform.sh on the command line.
Once you have the platform.sh CLI set up and you're in the correct platform.sh 
environment, run the following to open the tunnel.


````
$ platform tunnel:open
````

Update the values in scraper/db_settings.py if needed to match
the port number, host, user, or database name. While you're there also make 
sure the site_url is pointing to the site you want to scrape. It's a good idea 
to make sure that site_url is for the same environment that has the databse 
you're using. Otherwise you might get messed up data because of a mismatch.

For phase 2, you'll just need the nodes.json and urls.txt files created in 
phase 1. No database connection required. This way it's easier to upload the 
files somewhere and run scrapy from there for the actual scraping.

## Run the scripts

### Phase 1

After you set up your db_settings with db connection details and site_url, 
you're ready for the first phase.

Run this to pull data from the database and write it to files.

````
./pull-data
````

This creates two new files.
1. urls.txt: A listing of story URLs to crawl, one URL per line.
2. nodes.json: Data about the nodes that is combined with the scraped data 
later on.

### Phase 2

With those two files, you're now ready to run scrapy. Since everything is in 
those files, you can run this anywhere you want without needing a platform.sh 
tunnel or local database copy. Just copy those files to the working directory 
of an smt-scrapy checkout and you should be good for the next steps.

There is a scrapy spider called "stories" that crawls all URLs listed in 
urls.txt and saves some node data. It also looks for author profile page URLs 
and crawls those, saving author data in the process.

Run scrapy like this:

````
scrapy crawl stories
````

This will output logging to stdout and stderr, and save a jsonlines file that 
includes both node and author data. The jsonlines file is saved in 
`feeds/stories/`. A new one is created for each spider run and the files are 
named by the timestamp of the spider run.

#### Pro tip

If you're running scrapy on a server, run it with `screen` or 
something similar so that when you log out it'll keep running.

Here's how I do this:

````
ssh whatever
cd smt-scrapy
screen
scrapy crawl stories

# See that it's really doing it's thing.
````

When you're ready to leave, hit `ctrl+a` then `ctrl+d`. The first combination 
is to tell screen to pay attention, the second is to "detach". Now you'll be 
back in your normal shell session and the screen is still running. You can 
exit normally from here.

To reattach to the screen, after logging back in, use `screen -r`.

Check in on it some time later. If it's done your screen will be back to its 
prompt, and you can just `exit` to destroy the screen.
