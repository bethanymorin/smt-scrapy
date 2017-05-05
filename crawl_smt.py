import subprocess
import json
import datetime


starttime = datetime.datetime.now()

outfile_story = 'output/stories.jl'
outfile_author = 'output/authors.jl'


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

with open(outfile_story) as result_file:
    for line in result_file:
        line_data = json.loads(line)
        if line_data['url'] not in unique_urls:
            unique_urls.append(line_data['url'])
            article_count += 1

with open(outfile_author) as result_file:
    for line in result_file:
        line_data = json.loads(line)
        if line_data['url'] not in unique_urls:
            unique_urls.append(line_data['url'])
            contributor_count += 1


print "%d unique urls scraped" % len(unique_urls)
print "%d articles parsed" % article_count
print "%d profiles parsed" % contributor_count
print "Total time: %s" % total_time
