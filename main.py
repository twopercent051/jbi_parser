import glob
import json
import logging
import os
import time
from datetime import datetime

import aiohttp as aiohttp
import requests

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


logger = logging.getLogger(__name__)
file_log = logging.FileHandler("logger.log")
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out), level=logging.WARNING,
                    format="%(asctime)s %(levelname)s %(message)s")


class Parser:

    @staticmethod
    def get_soup_obj(url: str) -> BeautifulSoup:
        """Создает объект класса soup"""
        useragent = UserAgent()
        headers = {
            "Accept": "*/*",
            "User-Agent": useragent.random
        }
        session = requests.Session()
        retry = Retry(connect=100, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        req = session.get(url=url, headers=headers)
        req.encoding = 'utf-8'
        src = req.text
        soup = BeautifulSoup(src, 'lxml')
        return soup

    @staticmethod
    async def get_async_soup(url: str) -> BeautifulSoup:
        useragent = UserAgent()
        headers = {
            "Accept": "*/*",
            "User-Agent": useragent.random
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers) as resp:
                src = await resp.text()
        soup = BeautifulSoup(src, 'lxml')
        return soup

    @staticmethod
    def save_json(data: list, json_title: str):
        """Сохраняет результат в json"""
        with open(f'{os.getcwd()}/data/{json_title}.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def open_json(json_title: str) -> list:
        """Открывает json"""
        with open(f'{os.getcwd()}/data/{json_title}.json') as file:
            result_list = json.load(file)
        return result_list

    @staticmethod
    def open_json_by_full_path(json_title: str) -> list:
        """Открывает json по полному пути"""
        with open(json_title) as file:
            result_list = json.load(file)
        return result_list

    @classmethod
    def get_first_catalog(cls):
        """Каталог первого уровня"""
        url = 'http://tdajbi.ru/catalog-jbi.html'
        parent_menu = cls.get_soup_obj(url).find('ul', attrs={'class': 'ul-lev0'})
        parent_categories = parent_menu.find_all('li')
        result_list = []
        for category in parent_categories:
            title = category.find('a').text
            href = category.find('a').get('href')
            data_childs = category.get('data-childs')
            cat_dict = {'title': title, 'href': href, 'data_childs': data_childs}
            result_list.append(cat_dict)
        cls.save_json(result_list, 'first_catalog')

    @classmethod
    def get_second_catalog(cls):
        """Каталог второго уровня"""
        first_catalog = cls.open_json('first_catalog')
        result_list = []
        for item in first_catalog:
            print(item['title'])
            if item['data_childs'] == 'empty':
                item['parent_1'] = ''
                result_list.append(item)
            else:
                url = item['href']
                second_cat_block = cls.get_soup_obj(url).find(class_='ul-lev1-wrap')
                second_cats = second_cat_block.find_all('li')
                parent_title = item['title']
                for second_cat in second_cats:
                    title = second_cat.find('a').text
                    href = second_cat.find('a').get('href')
                    data_childs = second_cat.get('data-childs')
                    cat_dict = {'title': title, 'href': href, 'data_childs': data_childs, 'parent_1': parent_title}
                    result_list.append(cat_dict)
        cls.save_json(result_list, 'second_catalog')

    @classmethod
    def get_third_catalog(cls):
        """Каталог третьего уровня"""
        second_catalog = cls.open_json('second_catalog')
        result_list = []
        for item in second_catalog:
            print(item['title'])
            if item['data_childs'] == 'empty':
                item['parent_2'] = ''
                result_list.append(item)
            else:
                url = item['href']
                print(url)
                third_cat_block = cls.get_soup_obj(url).find(class_='ul-lev2-wrap')
                third_cats = third_cat_block.find_all('li')
                parent1_title = item['parent_1']
                parent2_title = item['title']
                for third_cat in third_cats:
                    title = third_cat.find('a').text
                    href = third_cat.find('a').get('href')
                    data_childs = third_cat.get('data-childs')
                    cat_dict = {
                        'title': title,
                        'href': href,
                        'data_childs': data_childs,
                        'parent_1': parent1_title,
                        'parent_2': parent2_title
                    }
                    result_list.append(cat_dict)
        cls.save_json(result_list, 'third_catalog')

    @classmethod
    def get_fourth_catalog(cls):
        """Каталог четвёртого уровня"""
        third_catalog = cls.open_json('third_catalog')
        result_list = []
        for item in third_catalog:
            print(item['title'])
            if item['data_childs'] == 'empty':
                item['parent_3'] = ''
                result_list.append(item)
            else:
                url = item['href']
                print(url)
                third_cat_block = cls.get_soup_obj(url).find(class_='ul-lev3-wrap')
                fourth_cats = third_cat_block.find_all('li')
                parent1_title = item['parent_1']
                parent2_title = item['parent_2']
                parent3_title = item['title']
                for fourth_cat in fourth_cats:
                    title = fourth_cat.find('a').text
                    href = fourth_cat.find('a').get('href')
                    data_childs = fourth_cat.get('data-childs')
                    cat_dict = {
                        'title': title,
                        'href': href,
                        'data_childs': data_childs,
                        'parent_1': parent1_title,
                        'parent_2': parent2_title,
                        'parent_3': parent3_title
                    }
                    result_list.append(cat_dict)
        cls.save_json(result_list, 'fourth_catalog')

    @classmethod
    def catalog_empty_proof(cls):
        """Проверка каталога 4го уровня на пустые значения"""
        third_catalog = cls.open_json('item_list')
        count = 0
        for item in third_catalog:
            if item['parent4'] == 'Плиты перекрытия многопустотные ПБ шириной 0,6 метра':
                count += 1
        print(count)

    @classmethod
    def item_counter(cls):
        """Подсчет количества позиций"""
        path = f"{os.getcwd()}/data/item_lists/*.json"
        file_list = glob.glob(path)
        counter = 0
        for file in file_list:
            cat = cls.open_json_by_full_path(file)
            counter += len(cat)
        print(counter)

    @classmethod
    def get_items_list(cls):
        """Получение списка карточек товара"""
        first_catalog = cls.open_json('first_catalog')
        catalog = cls.open_json('fourth_catalog')
        now = datetime.now()
        counter = 0
        for first_cat in first_catalog:
            first_title = first_cat['title']
            result_list = []
            for cat in catalog:
                cat_title = cat['title']
                if cat['parent_1'] == '':
                    parent_1 = cat_title
                else:
                    parent_1 = cat['parent_1']
                if first_title == parent_1:
                    url = cat['href']
                    item_block = cls.get_soup_obj(url).find(class_='box-list-products').find(class_='list_showtable'
                                                                                                    '-wrap')
                    total_time = (datetime.now() - now)
                    print(total_time, cat_title, sep=' || ')
                    # print(item_block)
                    item_list = item_block.find_all('tr')
                    for item in item_list:
                        # print(item)
                        item_title = item.find('td').text.strip()
                        item_href = item.find('td').find('a').get('href')
                        item_dict = {
                            'title': item_title,
                            'href': item_href,
                            'parent4': cat_title,
                            'parent3': cat['parent_3'],
                            'parent2': cat['parent_2'],
                            'parent1': cat['parent_1'],
                        }
                        result_list.append(item_dict)
                    time.sleep(0.6)
            print(f"{'#' * 10}\n", f'{first_title} Сохранен\n', '#' * 10, sep='\n')
            cls.save_json(result_list, f'item_lists/{first_title}')

    @classmethod
    def get_total_list(cls):
        """Получение общего списка"""
        path = f"{os.getcwd()}/data/item_lists/*.json"
        file_list = glob.glob(path)
        result_list = []
        for file in file_list:
            catalog = cls.open_json_by_full_path(file)
            for item in catalog:
                result_list.append(item)
        cls.save_json(result_list, f'cards/total')

    @classmethod
    def division_items(cls):
        """Разделение списка по 10к позиций"""
        total_list = cls.open_json('cards/total')
        item_counter = 0
        file_counter = 0
        file_list = []
        for item in total_list:
            item_counter += 1
            file_list.append(item)
            if item_counter % 10000 == 0 or item_counter == len(total_list):
                file_counter += 1
                cls.save_json(file_list, f'cards/file_{file_counter}')
                file_list = []

    @classmethod
    def get_item_info(cls):
        """Получение информации по карточке"""
        path = f"{os.getcwd()}/data/item_lists/*.json"
        file_list = glob.glob(path)
        print(file_list)
        counter = 0
        for file in file_list:
            catalog = cls.open_json_by_full_path(file)
            category = file.split('/')[-1].split('.')[0]
            print(category, len(catalog), counter, sep=' || ')
            counter += 1
        # for file in file_list:
        #     catalog = cls.open_json_by_full_path(file)
        #     category = file.split('/')[-1].split('.')[0]
        #     item_list = []
        #     for item in catalog:
        #         try:
        #             title = item['title']
        #             print(category, title, sep=' || ')
        #             href = item['href']
        #             parent_1 = item['parent1']
        #             parent_2 = item['parent2']
        #             parent_3 = item['parent3']
        #             parent_4 = item['parent4']
        #             card = cls.get_soup_obj(href)
        #             parameters = card.find(class_='props').text.replace('Размеры:', '').strip()
        #             image = card.find(class_='pcard-images').find('a').get('href')
        #             item_dict = {
        #                 'title': title,
        #                 'href': href,
        #                 'parent_1': parent_1,
        #                 'parent_2': parent_2,
        #                 'parent_3': parent_3,
        #                 'parent_4': parent_4,
        #                 'parameters': parameters,
        #                 'image': image
        #             }
        #             item_list.append(item_dict)
        #         except Exception as ex:
        #             logger.warning(f'Ошибка в категории {category} || {ex}')
        #     cls.save_json(item_list, f'cards/{category}')


