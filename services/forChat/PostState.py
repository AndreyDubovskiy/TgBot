import datetime
from telethon.errors import SessionPasswordNeededError
from services.forChat.UserState import UserState
from services.forChat.Response import Response
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import markups
import config_controller
import db.database as db
from telethon import TelegramClient
import asyncio
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError

class PostState(UserState):
    def __init__(self, user_id: str, user_chat_id: str, bot: AsyncTeleBot, user_name: str):
        super().__init__(user_id, user_chat_id, bot, user_name)
        self.current_page = 0
        self.max_on_page = 7
        self.edit = None
        self.current_name = None
        self.current_session = None
        self.client: TelegramClient = None
        self.newname = None
        self.newurls = None
        self.newphotos = None
        self.newvideos = None
        self.newtext = None
        self.is_test = False
        self.is_other = False
        self.hash_phone = None
        self.list_chats_other = db.get_other_user_chats()
        self.cooldoun_msg = config_controller.TIME_MSG_COOLDOWN
    async def start_msg(self):
        if self.user_id in config_controller.list_is_loggin_admins:
            return Response(text="Список постів", buttons=markups.generate_post_menu(self.current_page, self.max_on_page))
        else:
            return Response(text="У вас недостатньо прав!", is_end=True)

    async def next_msg(self, message: str):
        if not (self.user_id in config_controller.list_is_loggin_admins):
            return Response(text="У вас недостатньо прав!", is_end=True)
        if self.edit == "addname":
            self.newname = message
            self.edit = "addpost"
            return Response(text="Відправте пост одним повідомленням (можна з фото або відео, та текстом, але одним повідомленням):")
        elif self.edit == "addpost":
            self.newtext = message
            self.edit = None
            if config_controller.add_or_edit_post(self.newname, text=self.newtext, urls=self.newurls,
                                                  photos=self.newphotos, videos=self.newvideos):
                return Response(text="Успішно додано!", is_end=True, redirect="/postlist")
            else:
                return Response(text="Помилка!", is_end=True, redirect="/postlist")
        elif self.edit == "code_enter":
            code = message.replace(".", "").replace("-", "").replace(" ", "")
            try:
                await self.client.sign_in(config_controller.LIST_TG_ACC[self.current_session]["phone"], code)
            except SessionPasswordNeededError:
                if config_controller.LIST_TG_ACC[self.current_session].get("password", None) != None:
                    await self.client.sign_in(password=config_controller.LIST_TG_ACC[self.current_session]["password"])
                else:
                    return Response(text="Потрібен пароль до цього акаунту! Видаліть його та створіть новий з паролем", redirect="/menu")
            if not await self.client.is_user_authorized():
                self.hash_phone = await self.client.send_code_request(config_controller.LIST_TG_ACC[self.current_session]["phone"])
                self.edit = "code_enter"
                return Response(
                    text="Ви не правильно ввели код\nНа акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):")
            else:
                if not self.is_test:
                    self.edit = "count_send"
                    list_users = db.get_all_verify_users()
                    list_other = db.get_user_other_order()
                    return Response(text="Введіть кількість людей, котрим буде розсилатись пост:\n" + str(
                        len(list_users)) + " людей на даний момент в базі (Ваші люди, які парсились з таблиці ексель)\n" + str(
                        len(list_other)) + " людей з інших чатів у базі", buttons=markups.generate_cancel())
                else:
                    try:
                        await self.bot.send_message(chat_id=self.user_chat_id,
                                                    text="Розсилка розпочата, очікуйте повідомлення про завершення...")
                        count = 0
                        error = 0
                        chat_id = self.user_chat_id
                        text_post = config_controller.LIST_POSTS[self.current_name]['text']
                        list_photos = config_controller.LIST_POSTS[self.current_name]['photos']
                        list_videos = config_controller.LIST_POSTS[self.current_name]['videos']
                        entity = await self.client.get_entity(self.user_name)
                        if list_photos and len(list_photos) == 1 and text_post:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, caption=text_post,
                                                            silent=True)
                        elif list_photos and len(list_photos) == 1:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, silent=True)
                        elif list_photos and len(list_photos) > 1 and text_post:
                            error += 1
                        elif list_videos and len(list_videos) == 1 and text_post:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, caption=text_post,
                                                            silent=True)
                        elif list_videos and len(list_videos) == 1:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, silent=True)
                        elif text_post:
                            await self.client.send_message(entity, text_post, silent=True)
                        count += 1
                        await self.client.disconnect()
                        return Response(
                            text="Розсилка закінчена!\nРозіслано людям: " + str(count) + "\nПомилок: " + str(error),
                            is_end=True, redirect="/postlist")
                    except Exception as ex:
                        print(ex)
                        await self.client.disconnect()
                        return Response(text="Сталася помилка!",
                                        redirect="/menu")
        elif self.edit == "count_send":
            if self.is_other:
                self.count_send = int(message)
                self.current_page_chat = 0
                return Response(text="Людям з якого чату робити розсилку?", buttons=markups.generate_db_chats_menu(0, self.max_on_page))
            try:
                self.count_send = int(message)
                await self.bot.send_message(chat_id=self.user_chat_id, text="Розсилка розпочата, очікуйте повідомлення про завершення...")
                count = 0
                error = 0
                msg = await self.bot.send_message(chat_id=self.user_chat_id, text="Статус:\nВідправлено: "+str(count)+" з "+str(self.count_send)+"\nПомилок: " + str(error))
                list_users = db.get_user_verify_order()
                for user in list_users:
                    if count >= self.count_send:
                        break
                    try:
                        chat_id = user.tg_id
                        text_post = config_controller.LIST_POSTS[self.current_name]['text']
                        list_photos = config_controller.LIST_POSTS[self.current_name]['photos']
                        list_videos = config_controller.LIST_POSTS[self.current_name]['videos']
                        if user.tg_name != None:
                            entity = await self.client.get_entity(user.tg_name)
                        else:
                            entity = await self.client.get_entity(user.phone.split(",")[0])
                        if list_photos and len(list_photos) == 1 and text_post:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, caption=text_post, silent=True)
                        elif list_photos and len(list_photos) == 1:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, silent=True)
                        elif list_photos and len(list_photos) > 1 and text_post:
                            error+=1
                            continue
                        elif list_videos and len(list_videos) == 1 and text_post:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, caption=text_post, silent=True)
                        elif list_videos and len(list_videos) == 1:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, silent=True)
                        elif text_post:
                            await self.client.send_message(entity, text_post, silent=True)
                        count += 1
                        db.add_count_by_tg_id(str(chat_id))
                        await self.bot.edit_message_text(text="Статус:\nВідправлено: "+str(count)+" з "+str(self.count_send)+"\nПомилок: " + str(error), chat_id=msg.chat.id, message_id=msg.id)
                        await asyncio.sleep(self.cooldoun_msg)
                    except FloodWaitError as ex:
                        time_sleep = int(str(ex).split("A wait of ")[1].split(" ")[0])
                        print("WAIT", time_sleep)
                        await self.bot.edit_message_text(text="Статус:\nВідправлено: " + str(count) + " з " + str(
                            self.count_send) + "\nПомилок: " + str(error) + "\n(Анти флуд, очікування " + str(time_sleep) + "секунд", chat_id=msg.chat.id, message_id=msg.id)
                        await asyncio.sleep(time_sleep)
                        try:
                            chat_id = user.tg_id
                            text_post = config_controller.LIST_POSTS[self.current_name]['text']
                            list_photos = config_controller.LIST_POSTS[self.current_name]['photos']
                            list_videos = config_controller.LIST_POSTS[self.current_name]['videos']
                            if user.tg_name != None:
                                entity = await self.client.get_entity(user.tg_name)
                            else:
                                entity = await self.client.get_entity(user.phone.split(",")[0])
                            if list_photos and len(list_photos) == 1 and text_post:
                                with open(list_photos[0], 'rb') as photo_file:
                                    await self.client.send_file(entity, photo_file, caption=text_post, silent=True)
                            elif list_photos and len(list_photos) == 1:
                                with open(list_photos[0], 'rb') as photo_file:
                                    await self.client.send_file(entity, photo_file, silent=True)
                            elif list_photos and len(list_photos) > 1 and text_post:
                                error += 1
                                continue
                            elif list_videos and len(list_videos) == 1 and text_post:
                                with open(list_videos[0], 'rb') as video_file:
                                    await self.client.send_file(entity, video_file, caption=text_post, silent=True)
                            elif list_videos and len(list_videos) == 1:
                                with open(list_videos[0], 'rb') as video_file:
                                    await self.client.send_file(entity, video_file, silent=True)
                            elif text_post:
                                await self.client.send_message(entity, text_post, silent=True)
                            count += 1
                            db.add_count_by_tg_id(str(chat_id))
                            await self.bot.edit_message_text(text="Статус:\nВідправлено: " + str(count) + " з " + str(
                                self.count_send) + "\nПомилок: " + str(error), chat_id=msg.chat.id, message_id=msg.id)
                            await asyncio.sleep(self.cooldoun_msg)
                        except Exception as ex:
                            print(ex)
                            error += 1
                await self.bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
                await self.client.disconnect()
                return Response(text="Розсилка закінчена!\nРозіслано людям: " + str(count) + "\nПомилок: " + str(error),
                                is_end=True, redirect="/postlist")
            except:
                return Response(text="Ви впевненні, що ввели число правильно? Спробуйте ще раз:", buttons=markups.generate_cancel())

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            if self.current_name == None:
                return Response(is_end=True, redirect="/menu")
            else:
                return Response(is_end=True, redirect="/postlist")
        elif data_btn == "/cnext":
            if len(self.list_chats_other)-((self.current_page_chat+1)*self.max_on_page) > 0:
                self.current_page_chat+=1
            return Response(text="Список чатів", buttons=markups.generate_db_chats_menu(self.current_page_chat*self.max_on_page, self.max_on_page))
        elif data_btn =="/cprev":
            if self.current_page_chat > 0:
                self.current_page_chat-=1
            return Response(text="Список чатів", buttons=markups.generate_db_chats_menu(self.current_page_chat*self.max_on_page, self.max_on_page))
        elif data_btn == "/next":
            if len(config_controller.LIST_POSTS)-((self.current_page+1)*self.max_on_page) > 0:
                self.current_page+=1
            return Response(text="Список постів", buttons=markups.generate_post_menu(self.current_page*self.max_on_page, self.max_on_page))
        elif data_btn =="/prev":
            if self.current_page > 0:
                self.current_page-=1
            return Response(text="Список постів", buttons=markups.generate_post_menu(self.current_page*self.max_on_page, self.max_on_page))
        elif data_btn in config_controller.LIST_POSTS:
            self.current_name = data_btn
            print(config_controller.LIST_POSTS[self.current_name])
            text = ""
            if config_controller.LIST_POSTS[self.current_name]['photos'] != None:
                text+= "\nКількість прикріплених фото: " + str(len(config_controller.LIST_POSTS[self.current_name]['photos'])) + "\n"
            if config_controller.LIST_POSTS[self.current_name]['videos'] != None:
                text+= "\nКількість прикріплених відео: " + str(len(config_controller.LIST_POSTS[self.current_name]['videos'])) + "\n"
            if config_controller.LIST_POSTS[self.current_name]['text'] != None:
                text+="\nТекст поста:\n" + config_controller.LIST_POSTS[self.current_name]['text']
            return Response(text="Назва поста: " + self.current_name + text, buttons=markups.generate_post_semimenu())
        elif data_btn == "/add":
            self.edit = "addname"
            return Response(text="Напишіть назву поста наступним повідомленням (для себе, користувачам не надсилається):", buttons=markups.generate_cancel())
        elif data_btn == "/delete":
            if config_controller.del_post(self.current_name):
                return Response(text="Успішно видалено!", is_end=True, redirect="/postlist")
            else:
                return Response(text="Помилка!", is_end=True, redirect="/postlist")
        elif data_btn == "/csend":
            self.is_other = True
            return Response(text="Виберіть акаунт для розсилки:", buttons=markups.generate_tg_acc_menu2())
        elif data_btn == "/sendme":
            self.is_test = True
            return Response(text="Виберіть акаунт для розсилки:", buttons=markups.generate_tg_acc_menu2())
        elif data_btn == "/send":
            return Response(text="Виберіть акаунт для розсилки:", buttons=markups.generate_tg_acc_menu2())
        elif data_btn in config_controller.LIST_TG_ACC:
            self.current_session = data_btn
            self.client = TelegramClient(session=self.current_session, api_id=config_controller.LIST_TG_ACC[self.current_session]["api_id"], api_hash=config_controller.LIST_TG_ACC[self.current_session]["api_hash"])
            await self.client.connect()
            if not await self.client.is_user_authorized():
                self.hash_phone = await self.client.send_code_request(config_controller.LIST_TG_ACC[self.current_session]["phone"])
                self.edit = "code_enter"
                return Response(text="На акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):")
            else:
                if not self.is_test:
                    self.edit = "count_send"
                    list_users = db.get_all_verify_users()
                    list_other = db.get_user_other_order()
                    return Response(text="Введіть кількість людей, котрим буде розсилатись пост:\n" + str(
                        len(list_users)) + " людей на даний момент в базі (Ваші люди, які парсились з таблиці ексель)\n" + str(len(list_other)) + " людей з інших чатів у базі", buttons=markups.generate_cancel())
                else:
                    try:
                        await self.bot.send_message(chat_id=self.user_chat_id,
                                                    text="Розсилка розпочата, очікуйте повідомлення про завершення...")
                        count = 0
                        error = 0
                        chat_id = self.user_chat_id
                        text_post = config_controller.LIST_POSTS[self.current_name]['text']
                        list_photos = config_controller.LIST_POSTS[self.current_name]['photos']
                        list_videos = config_controller.LIST_POSTS[self.current_name]['videos']
                        entity = await self.client.get_entity(self.user_name)
                        if list_photos and len(list_photos) == 1 and text_post:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, caption=text_post,
                                                            silent=True)
                        elif list_photos and len(list_photos) == 1:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, silent=True)
                        elif list_photos and len(list_photos) > 1 and text_post:
                            error += 1
                        elif list_videos and len(list_videos) == 1 and text_post:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, caption=text_post,
                                                            silent=True)
                        elif list_videos and len(list_videos) == 1:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, silent=True)
                        elif text_post:
                            await self.client.send_message(entity, text_post, silent=True)
                        count += 1
                        await self.client.disconnect()
                        return Response(
                            text="Розсилка закінчена!\nРозіслано людям: " + str(count) + "\nПомилок: " + str(error),
                            is_end=True, redirect="/postlist")
                    except Exception as ex:
                        print(ex)
                        await self.client.disconnect()
                        return Response(text="Сталася помилка!",
                                        redirect="/menu")
        elif data_btn == "/any":
            try:
                await self.bot.send_message(chat_id=self.user_chat_id, text="Розсилка розпочата, очікуйте повідомлення про завершення...")
                count = 0
                error = 0
                msg = await self.bot.send_message(chat_id=self.user_chat_id, text="Статус:\nВідправлено: "+str(count)+" з "+str(self.count_send)+"\nПомилок: " + str(error))
                list_users = db.get_user_other_order()
                for user in list_users:
                    if count >= self.count_send:
                        break
                    try:
                        chat_id = user.tg_id
                        text_post = config_controller.LIST_POSTS[self.current_name]['text']
                        list_photos = config_controller.LIST_POSTS[self.current_name]['photos']
                        list_videos = config_controller.LIST_POSTS[self.current_name]['videos']
                        if user.tg_name != None:
                            entity = await self.client.get_entity(user.tg_name)
                        else:
                            entity = await self.client.get_entity(user.phone.split(",")[0])
                        if list_photos and len(list_photos) == 1 and text_post:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, caption=text_post, silent=True)
                        elif list_photos and len(list_photos) == 1:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, silent=True)
                        elif list_photos and len(list_photos) > 1 and text_post:
                            error+=1
                            continue
                        elif list_videos and len(list_videos) == 1 and text_post:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, caption=text_post, silent=True)
                        elif list_videos and len(list_videos) == 1:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, silent=True)
                        elif text_post:
                            await self.client.send_message(entity, text_post, silent=True)
                        count += 1
                        db.add_count_otheruser_by_tg_id(str(chat_id))
                        await self.bot.edit_message_text(text="Статус:\nВідправлено: "+str(count)+" з "+str(self.count_send)+"\nПомилок: " + str(error), chat_id=msg.chat.id, message_id=msg.id)
                        if count < self.count_send:
                            await asyncio.sleep(self.cooldoun_msg)
                    except FloodWaitError as ex:
                        time_sleep = int(str(ex).split("A wait of ")[1].split(" ")[0])
                        print("WAIT", time_sleep)
                        await self.bot.edit_message_text(text="Статус:\nВідправлено: " + str(count) + " з " + str(
                            self.count_send) + "\nПомилок: " + str(error) + "\n(Анти флуд, очікування " + str(time_sleep) + "секунд", chat_id=msg.chat.id, message_id=msg.id)
                        await asyncio.sleep(time_sleep)
                        try:
                            chat_id = user.tg_id
                            text_post = config_controller.LIST_POSTS[self.current_name]['text']
                            list_photos = config_controller.LIST_POSTS[self.current_name]['photos']
                            list_videos = config_controller.LIST_POSTS[self.current_name]['videos']
                            if user.tg_name != None:
                                entity = await self.client.get_entity(user.tg_name)
                            else:
                                entity = await self.client.get_entity(user.phone.split(",")[0])
                            if list_photos and len(list_photos) == 1 and text_post:
                                with open(list_photos[0], 'rb') as photo_file:
                                    await self.client.send_file(entity, photo_file, caption=text_post, silent=True)
                            elif list_photos and len(list_photos) == 1:
                                with open(list_photos[0], 'rb') as photo_file:
                                    await self.client.send_file(entity, photo_file, silent=True)
                            elif list_photos and len(list_photos) > 1 and text_post:
                                error += 1
                                continue
                            elif list_videos and len(list_videos) == 1 and text_post:
                                with open(list_videos[0], 'rb') as video_file:
                                    await self.client.send_file(entity, video_file, caption=text_post, silent=True)
                            elif list_videos and len(list_videos) == 1:
                                with open(list_videos[0], 'rb') as video_file:
                                    await self.client.send_file(entity, video_file, silent=True)
                            elif text_post:
                                await self.client.send_message(entity, text_post, silent=True)
                            count += 1
                            db.add_count_otheruser_by_tg_id(str(chat_id))
                            await self.bot.edit_message_text(text="Статус:\nВідправлено: " + str(count) + " з " + str(
                                self.count_send) + "\nПомилок: " + str(error), chat_id=msg.chat.id, message_id=msg.id)
                            if count < self.count_send:
                                await asyncio.sleep(self.cooldoun_msg)
                        except Exception as ex:
                            print(ex)
                            error += 1
                await self.bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
                await self.client.disconnect()
                return Response(text="Розсилка закінчена!\nРозіслано людям: " + str(count) + "\nПомилок: " + str(error),
                                is_end=True, redirect="/postlist")
            except:
                await self.client.disconnect()
                return Response(text="Сталася помилка!", redirect="/menu")

        elif data_btn in db.get_other_user_chats():
            self.chat_send = data_btn
            try:
                await self.bot.send_message(chat_id=self.user_chat_id, text="Розсилка розпочата, очікуйте повідомлення про завершення...")
                count = 0
                error = 0
                msg = await self.bot.send_message(chat_id=self.user_chat_id, text="Статус:\nВідправлено: "+str(count)+" з "+str(self.count_send)+"\nПомилок: " + str(error))
                list_users = db.get_user_other_order_by_chats(self.chat_send)
                for user in list_users:
                    if count >= self.count_send:
                        break
                    try:
                        chat_id = user.tg_id
                        text_post = config_controller.LIST_POSTS[self.current_name]['text']
                        list_photos = config_controller.LIST_POSTS[self.current_name]['photos']
                        list_videos = config_controller.LIST_POSTS[self.current_name]['videos']
                        if user.tg_name != None:
                            entity = await self.client.get_entity(user.tg_name)
                        else:
                            entity = await self.client.get_entity(user.phone.split(",")[0])
                        if list_photos and len(list_photos) == 1 and text_post:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, caption=text_post, silent=True)
                        elif list_photos and len(list_photos) == 1:
                            with open(list_photos[0], 'rb') as photo_file:
                                await self.client.send_file(entity, photo_file, silent=True)
                        elif list_photos and len(list_photos) > 1 and text_post:
                            error+=1
                            continue
                        elif list_videos and len(list_videos) == 1 and text_post:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, caption=text_post, silent=True)
                        elif list_videos and len(list_videos) == 1:
                            with open(list_videos[0], 'rb') as video_file:
                                await self.client.send_file(entity, video_file, silent=True)
                        elif text_post:
                            await self.client.send_message(entity, text_post, silent=True)
                        count += 1
                        db.add_count_otheruser_by_tg_id(str(chat_id))
                        await self.bot.edit_message_text(text="Статус:\nВідправлено: "+str(count)+" з "+str(self.count_send)+"\nПомилок: " + str(error), chat_id=msg.chat.id, message_id=msg.id)
                        if count < self.count_send:
                            await asyncio.sleep(self.cooldoun_msg)
                    except FloodWaitError as ex:
                        time_sleep = int(str(ex).split("A wait of ")[1].split(" ")[0])
                        print("WAIT", time_sleep)
                        await self.bot.edit_message_text(text="Статус:\nВідправлено: " + str(count) + " з " + str(
                            self.count_send) + "\nПомилок: " + str(error) + "\n(Анти флуд, очікування " + str(time_sleep) + "секунд", chat_id=msg.chat.id, message_id=msg.id)
                        await asyncio.sleep(time_sleep)
                        try:
                            chat_id = user.tg_id
                            text_post = config_controller.LIST_POSTS[self.current_name]['text']
                            list_photos = config_controller.LIST_POSTS[self.current_name]['photos']
                            list_videos = config_controller.LIST_POSTS[self.current_name]['videos']
                            if user.tg_name != None:
                                entity = await self.client.get_entity(user.tg_name)
                            else:
                                entity = await self.client.get_entity(user.phone.split(",")[0])
                            if list_photos and len(list_photos) == 1 and text_post:
                                with open(list_photos[0], 'rb') as photo_file:
                                    await self.client.send_file(entity, photo_file, caption=text_post, silent=True)
                            elif list_photos and len(list_photos) == 1:
                                with open(list_photos[0], 'rb') as photo_file:
                                    await self.client.send_file(entity, photo_file, silent=True)
                            elif list_photos and len(list_photos) > 1 and text_post:
                                error += 1
                                continue
                            elif list_videos and len(list_videos) == 1 and text_post:
                                with open(list_videos[0], 'rb') as video_file:
                                    await self.client.send_file(entity, video_file, caption=text_post, silent=True)
                            elif list_videos and len(list_videos) == 1:
                                with open(list_videos[0], 'rb') as video_file:
                                    await self.client.send_file(entity, video_file, silent=True)
                            elif text_post:
                                await self.client.send_message(entity, text_post, silent=True)
                            count += 1
                            db.add_count_otheruser_by_tg_id(str(chat_id))
                            await self.bot.edit_message_text(text="Статус:\nВідправлено: " + str(count) + " з " + str(
                                self.count_send) + "\nПомилок: " + str(error), chat_id=msg.chat.id, message_id=msg.id)
                            if count < self.count_send:
                                await asyncio.sleep(self.cooldoun_msg)
                        except Exception as ex:
                            print(ex)
                            error += 1
                await self.bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
                await self.client.disconnect()
                return Response(text="Розсилка закінчена!\nРозіслано людям: " + str(count) + "\nПомилок: " + str(error),
                                is_end=True, redirect="/postlist")
            except:
                await self.client.disconnect()
                return Response(text="Сталася помилка!", redirect="/menu")








    async def next_msg_photo_and_video(self, message: types.Message):
        if self.edit == "addpost":
            self.newtext = message.caption
            if message.photo:
                self.newphotos = []
                i = message.photo[-1]
                file_info = await self.bot.get_file(i.file_id)
                file_path = file_info.file_path
                bytess = await self.bot.download_file(file_path)
                with open(f'post_tmp/{str(config_controller.get_id_post())}_{i.file_id}.jpg', 'wb') as file:
                    file.write(bytess)
                self.newphotos.append(f'post_tmp/{str(config_controller.get_id_post())}_{i.file_id}.jpg')
            if message.video:
                self.newvideos = []
                i = message.video
                file_info = await self.bot.get_file(i.file_id)
                file_path = file_info.file_path
                bytess = await self.bot.download_file(file_path)
                with open(f'post_tmp/{str(config_controller.get_id_post())}_{i.file_id}.mp4', 'wb') as file:
                    file.write(bytess)
                self.newvideos.append(f'post_tmp/{str(config_controller.get_id_post())}_{i.file_id}.mp4')
            self.edit = None
            if config_controller.add_or_edit_post(self.newname, text=self.newtext, urls=self.newurls,
                                                  photos=self.newphotos, videos=self.newvideos):
                return Response(text="Успішно додано!", is_end=True, redirect="/postlist")
            else:
                return Response(text="Помилка!", is_end=True, redirect="/postlist")