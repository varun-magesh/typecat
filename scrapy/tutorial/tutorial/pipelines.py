import scrapy
import scrapy.pipelines.files as sp
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#
# class TutorialPipeline(object):
#
#     def process_item(self, item, spider):
#         with open("home/timothy/dl_fonts/{}.zip".format(item['url']), 'w+') as f:

class FontZipPipeline(sp.FilesPipeline):
    def file_path(self, request, response=None, info=None):
        return request.meta.get('filename', '')
    def get_media_requests(self, item, info):
        file_url = item['file_url']
        meta = {'filename': item['name']}
        yield scrapy.Request(url=file_url, meta=meta)