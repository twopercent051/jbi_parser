import asyncio
import os
from sys import argv

import requests
from sqlalchemy.exc import IntegrityError

from database import JBIItemsDAO
from settings import settings
from main import Parser


class ItemParser:

    @staticmethod
    def telegram_message(text: str):
        requests.get(
            f'https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage',
            params={
                'chat_id': settings.ADMIN,
                'text': text,
                'parse_mode': 'HTML'
            }
        )

    @classmethod
    async def get_item_info(cls, server_id: int):
        path = f'{os.getcwd()}/data/cards/file_{server_id}.json'
        catalog = Parser.open_json_by_full_path(path)
        counter = 0
        for item in catalog:
            title = item['title']
            href = item['href']
            parent_1 = item['parent1']
            parent_2 = item['parent2']
            parent_3 = item['parent3']
            parent_4 = item['parent4']
            try:
                card = await Parser.get_async_soup(href)
                parameters = card.find(class_='props').text.replace('Размеры:', '').strip()
                image = card.find(class_='pcard-images').find('a').get('href')
                await JBIItemsDAO.add(
                    title=title,
                    href=href,
                    parent_1=parent_1,
                    parent_2=parent_2,
                    parent_3=parent_3,
                    parent_4=parent_4,
                    parameters=parameters,
                    image=image
                )
                counter += 1
            except IntegrityError:
                print('Уже существует')
            except Exception as ex:
                cls.telegram_message(f'<b>Server: {server_id} || Error: {ex}</b>')
            if counter % 1000 == 0 and counter > 0:
                cls.telegram_message(f'Server {server_id} || Saved {counter} items')
            # if counter == len(catalog):
        cls.telegram_message(f'Server {server_id} finished')


if __name__ == '__main__':
    server = argv[1]
    asyncio.run(ItemParser.get_item_info(server_id=server))
    # ItemParser.telegram_message('1234')
