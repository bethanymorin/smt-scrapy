# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class SmtArticlePipeline(object):
    def process_item(self, item, spider):
        import pdb
        pdb.set_trace()
        return item


class SmtContributorPipeline(object):
    def process_item(self, item, spider):
        import pdb
        pdb.set_trace()
        return item
