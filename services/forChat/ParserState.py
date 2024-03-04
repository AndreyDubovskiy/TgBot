import os

from telebot import types
import pandas as pd
import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller
from db import database as db

class ParserState(UserState):
    async def start_msg(self):
        return Response(text="Для парсингу файла, відправте його наступним повідомленням у форматі .xlsx", buttons=markups.generate_cancel())

    async def next_msg_document(self, message: types.Message):
        await self.bot.send_message(chat_id=self.user_chat_id, text="Парсинг розпочато...")
        try:
            file_name = message.document.file_name
            file_id_info = await self.bot.get_file(message.document.file_id)
            downloaded_file = await self.bot.download_file(file_id_info.file_path)
            src = file_name
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)

            df = pd.read_excel(src)

            count = 0

            for index, row in df.iterrows():
                if index > 1:
                    name = str(row.get("ЗАГАЛЬНА ІНФОРМАЦІЯ", "Нема")) + " " + str(row.get("Unnamed: 2", "Нема"))
                    phone = str(row.get("КОНТАКТНІ ДАНІ", "Нема"))
                    db.create_user(name, phone)
                    count+=1
            try:
                os.remove(src)
            except:
                pass
            return Response(text="Було додано до бази номерів: "+str(count)+"\nЩоб додати їх до бази розсилки потрібно увімкнути пошук по телеграм (у меню)", is_end=True, redirect="/menu")
        except:
            try:
                os.remove(src)
            except:
                pass
            return Response(text="Сталася помилка! Можливо ви скинули не той формат файлу", redirect="/menu")
