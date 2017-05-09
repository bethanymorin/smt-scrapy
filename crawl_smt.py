import subprocess
import json
import datetime
import argparse
import os

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

starttime = datetime.datetime.now()

outfile_story = '%s/stories.jl' % out_dir
outfile_author = '%s/authors.jl' % out_dir


first_commad = 'scrapy crawl stories --output=%s --output-format=jsonlines' % outfile_story
process = subprocess.Popen(first_commad, shell=True)
process.wait()
print process.returncode

second_commad = 'scrapy crawl authors --output=%s --output-format=jsonlines' % outfile_author
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

try:
    with open(outfile_author) as result_file:
        for line in result_file:
            line_data = json.loads(line)
            if line_data['url'] not in unique_urls:
                unique_urls.append(line_data['url'])
                contributor_count += 1
except Exception:
    print "couldn't open authors.jl"


print "%d unique urls scraped" % len(unique_urls)
print "%d articles parsed" % article_count
print "%d profiles parsed" % contributor_count
print "Total time: %s" % total_time
