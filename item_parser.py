import asyncio
import os
from sys import argv

import aiohttp
import aiofiles
import paramiko
import requests
from sqlalchemy.exc import IntegrityError
from transliterate import slugify

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

    @staticmethod
    async def ftp_upload(file: str):
        """Загрузка файла на сервер и удаление с локальной машины"""
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=settings.FTP_HOST, username=settings.FTP_USER, password=settings.FTP_PASS)
        ftp = ssh_client.open_sftp()
        ftp.put(f"{os.getcwd()}/{file}.jpg", f"/root/jbi_images/{file}.jpg")
        ftp.close()
        ssh_client.close()
        os.remove(f"{os.getcwd()}/{file}.jpg")

    @classmethod
    async def get_item_info(cls, server_id: int):
        path = f'{os.getcwd()}/data/cards/file_{server_id}.json'
        catalog = Parser.open_json_by_full_path(path)
        counter = 0
        for item in catalog:
            title = item['title']
            href = item['href']
            is_saved = await JBIItemsDAO.select_by_href(href=href)
            if is_saved:
                continue
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

    @classmethod
    async def get_image(cls, server_id: int):
        """Загрузка изображений"""
        counter = 0
        while True:
            image_data = await JBIItemsDAO.select_not_saved()
            if image_data is None:
                cls.telegram_message(f'Server {server_id} finished. Saved {counter} items')
                break
            image_title = slugify(image_data['title'])
            image_href = image_data['image']
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_href) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(f'{os.getcwd()}/images/{image_title}.jpg', mode='wb')
                            await f.write(await resp.read())
                            await f.close()
                            counter += 1
                        else:
                            cls.telegram_message(f'Ошибка {resp.status} || {image_href} || Server {server_id}')
                            await JBIItemsDAO.add(title=image_title, image=image_href)
                            await asyncio.sleep(10)
                # await cls.ftp_upload(image_title)
                if counter % 5000 == 0:
                    cls.telegram_message(f'<i>Server {server_id} saved {counter} items</i>')
            except Exception as ex:
                await JBIItemsDAO.add(title=image_title, image=image_href)
                cls.telegram_message(f'Ошибка || {image_href} || Server {server_id} || {ex}')
                await asyncio.sleep(10)


if __name__ == '__main__':
    server = argv[1]
    asyncio.run(ItemParser.get_image(server_id=server))
