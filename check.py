import json

unique_urls = []
total_count = 0
contributor_count = 0
article_count = 0

with open('smt_stories.jl') as result_file:
    for line in result_file:
        line_data = json.loads(line)
        if line_data['url'] not in unique_urls:
            unique_urls.append(line_data['url'])
            article_count += 1
        total_count += 1

with open('smt_authors.jl') as result_file:
    for line in result_file:
        line_data = json.loads(line)
        if line_data['url'] not in unique_urls:
            unique_urls.append(line_data['url'])
            contributor_count += 1
        total_count += 1

print "%d total pages in file" % total_count
print "%d unique urls in file" % len(unique_urls)
print "%d articles parsed" % article_count
print "%d profiles parsed" % contributor_count
