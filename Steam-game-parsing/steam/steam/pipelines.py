# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json


class SteamPipeline:

    def __init__(self):
        self.file = None

    def open_spider(self, spider):
        self.file = open("items.json", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        try:
            # in the normal case the date format will be as follows: '6 Oct, 2022'
            game_year = int(item["rel_date"].split()[-1])
            # check: if the year is later than or equal to 2000, record the information
            if game_year >= 2000:
                line = json.dumps(ItemAdapter(item).asdict()) + '\n'
                self.file.write(line)
        except ValueError:
            # tried to convert a word out of letters to int 
            # for example, it could be 'coming soon'
            # then we skip
            pass

        return item
