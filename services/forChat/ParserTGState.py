from telebot import types
import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller
from db import database as db
from telethon import TelegramClient
from telethon.tl.types import InputPhoneContact, InputUser
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.functions.contacts import DeleteContactsRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
import asyncio


class ParserTGState(UserState):
    async def start_msg(self):
        self.edit = None
        return Response(text="Виберіть акаунт, який буде використовуватись для перевірки номерів в телеграм:", buttons=markups.generate_tg_acc_menu2())

    async def pp(self):
        list_tmp = db.get_all_users()
        count = 0
        new_count = 0
        msg = await self.bot.send_message(chat_id=self.user_chat_id,
                                          text="Перевірка " + str(count) + " з " + str(len(list_tmp)))
        client = self.client
        for user in list_tmp:
            count += 1
            if count % 10 == 0:
                await self.bot.edit_message_text(text="Перевірено " + str(count) + " з " + str(
                    len(list_tmp)) + "\nДодано нових користувачів телеграм: " + str(new_count),
                                                 chat_id=msg.chat.id, message_id=msg.id)
            if db.is_in_user_verify(user.valid_phone):
                continue
            phones = user.valid_phone.split(",")
            for phone in phones:
                try:
                    contact = InputPhoneContact(client_id=0, phone=phone, first_name=user.name, last_name="")
                    result = await client(ImportContactsRequest([contact]))
                    db.create_verify_user(user.name, user.valid_phone, result.users[0].id, result.users[0].username)
                    new_count += 1
                    await asyncio.sleep(1)
                    await client(DeleteContactsRequest(id=[result.users[0].id]))
                except FloodWaitError as ex:
                    await self.bot.edit_message_text(text="Перевірено " + str(count) + " з " + str(
                        len(list_tmp)) + "\nДодано нових користувачів телеграм: " + str(new_count)+"\nЗатримка на 250 секунд (Анти-флуд)",
                                                     chat_id=msg.chat.id, message_id=msg.id)
                    time_sleep = int(str(ex).split("A wait of ")[1].split(" ")[0])
                    await asyncio.sleep(time_sleep + 5)
                    try:
                        contact = InputPhoneContact(client_id=0, phone=phone, first_name=user.name, last_name="")
                        result = await client(ImportContactsRequest([contact]))
                        db.create_verify_user(user.name, user.valid_phone, result.users[0].id, result.users[0].username)
                        new_count += 1
                        await asyncio.sleep(1)
                        await client(DeleteContactsRequest(id=[result.users[0].id]))
                    except:
                        pass
                except:
                    pass
        await self.bot.edit_message_text(text="Перевірено " + str(count) + " з " + str(len(list_tmp))+"\nДодано нових користувачів телеграм: "+str(new_count),
                                             chat_id=msg.chat.id, message_id=msg.id)

    async def next_msg(self, message: str):
        if self.edit == "code_enter":
            code = message.replace(".", "").replace("-", "").replace(" ", "")
            await self.client.sign_in(config_controller.LIST_TG_ACC[self.current_session]["phone"], code)
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(config_controller.LIST_TG_ACC[self.current_session]["phone"])
                self.edit = "code_enter"
                return Response(
                    text="Ви не правильно ввели код\nНа акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):")
            else:
                await self.pp()
                await self.client.disconnect()
                return Response(redirect="/menu")


    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/menu")
        elif data_btn in config_controller.LIST_TG_ACC:
            self.current_session = data_btn
            self.client = TelegramClient(session=self.current_session,
                                         api_id=config_controller.LIST_TG_ACC[self.current_session]["api_id"],
                                         api_hash=config_controller.LIST_TG_ACC[self.current_session]["api_hash"])
            await self.client.connect()
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(config_controller.LIST_TG_ACC[self.current_session]["phone"])
                self.edit = "code_enter"
                return Response(
                    text="На акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):")
            else:
                await self.pp()
                await self.client.disconnect()
                return Response(redirect="/menu")



