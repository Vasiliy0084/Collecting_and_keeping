# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy1710p6

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_hh(item['salary'])
            item['company'] = self.process_company(item['company'])
            del item['salary']
        if spider.name == 'sjru':
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_sjob(item['salary'])
            item['company'] = self.process_company(item['company'])
            del item['salary']
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_company(self, company):
        company = ''.join(company).replace(u'\xa0', u' ')
        return company

    def process_salary_hh(self, salary):
        salary_min = None
        salary_max = None
        currency = None

        salary = ''.join(salary).replace(u'\xa0', u'')
        salary = re.split(r'\s|-', salary)

        if salary[0] == 'до':
            salary_min = None
            salary_max = int(salary[1])
        elif salary[0] == 'от':
            salary_min = int(salary[1])
            salary_max = None
        else:
            salary_min = int(salary[0])
            salary_max = int(salary[2])

        currency = salary[-1]

        return salary_min, salary_max, currency

    def process_salary_sjob(self, salary):
        salary_min = None
        salary_max = None
        currency = None

        for i in range(len(salary)):
            salary[i] = salary[i].replace(u'\xa0', u'')
            salary = re.split(r'\s|-', salary)

        if salary[0] == 'до':
            salary_max = salary[2]
        elif len(salary) == 3 and salary[0].isdigit():
            salary_max = salary[0]
        elif salary[0] == 'от':
            salary_min = salary[2]
        elif len(salary) > 3 and salary[0].isdigit():
            salary_min = salary[0]
            salary_max = salary[2]

        currency = self._get_name_currency(salary[-1])

        return salary_min, salary_max, currency

    def _get_name_currency(self, currency_name):
        currency_dict = {
            'EUR': {'€'},
            'KZT': {'₸'},
            'RUB': {'₽', 'руб.'},
            'UAH': {'₴', 'грн.'},
            'USD': {'$'}
        }

        name = None

        for item_name, items_list in currency_dict.items():
            if currency_name in items_list:
                name = item_name

        return name