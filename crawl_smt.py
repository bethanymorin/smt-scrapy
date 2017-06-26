import subprocess
import json
import datetime
import argparse
import os
import logging

logFormatter = logging.Formatter("%(asctime)s\t[%(levelname)s]\t%(message)s")
rootLogger = logging.getLogger()

DEFAULT_LIMIT = 1000
DEFAULT_OFFSET = 0

parser = argparse.ArgumentParser(
    description=(
        'Manager for running a scrapy script for SMT stories & authors'
    )
)

parser.add_argument(
    '--limit',
    help='INT: limit initial node query',
    dest='limit',
    type=int,
    required=False
)

parser.add_argument(
    '--offset',
    help='INT: offset initial node query',
    dest='offset',
    type=int,
    required=False
)
args = parser.parse_args()

limit = int(args.limit or DEFAULT_LIMIT)
offset = int(args.offset or DEFAULT_OFFSET)

end = offset + limit
out_dir = 'output/%s-%s' % (offset, end)

if not os.path.exists('.crawl_smt'):
    os.makedirs('.crawl_smt')
settings_file = open('.crawl_smt/settings.txt', 'w+')
settings_file.write('%d,%d,%s' % (limit, offset, out_dir))
settings_file.close()

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

logging.basicConfig(level=logging.DEBUG)
fileHandler = logging.FileHandler('%s/log' % out_dir)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

logging.info(" >>>>>>>>>>>>>>>>>> START")
logging.info("start record: %d" % offset)
logging.info("end record: %d" % end)

starttime = datetime.datetime.now()

outfile_story = '%s/stories.jl' % out_dir
outfile_author = '%s/authors.jl' % out_dir


first_commad = 'scrapy crawl stories --output=%s --output-format=jsonlines' % outfile_story
logging.info("running command: `%s`" % first_commad)

process = subprocess.Popen(first_commad, shell=True)
process.wait()
print process.returncode

second_commad = 'scrapy crawl authors --output=%s --output-format=jsonlines' % outfile_author
logging.info("running command: `%s`" % second_commad)

process = subprocess.Popen(second_commad, shell=True)
process.wait()
print process.returncode


endtime = datetime.datetime.now()
total_time = endtime - starttime

unique_urls = []
contributor_count = 0
article_count = 0

try:
    with open(outfile_story) as result_file:
        for line in result_file:
            line_data = json.loads(line)
            if line_data['url'] not in unique_urls:
                unique_urls.append(line_data['url'])
                article_count += 1
except Exception:
    print "couldn't open stories.jl"
    logging.error("couldn't open stories.jl")

try:
    with open(outfile_author) as result_file:
        for line in result_file:
            line_data = json.loads(line)
            if line_data['url'] not in unique_urls:
                unique_urls.append(line_data['url'])
                contributor_count += 1
except Exception:
    print "couldn't open authors.jl"
    logging.error("couldn't open authors.jl")


logging.info("%d unique urls scraped" % len(unique_urls))
logging.info("%d articles parsed" % article_count)
logging.info("%d profiles parsed" % contributor_count)
logging.info("Total time: %s" % total_time)
logging.info(" >>>>>>>>>>>>>>>>>> END\n")
