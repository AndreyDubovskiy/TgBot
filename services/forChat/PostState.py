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
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError, UserDeletedError, UserInvalidError, UserDeactivatedError, UsernameInvalidError
import random
class PostState(UserState):
    def __init__(self, user_id: str, user_chat_id: str, bot: AsyncTeleBot, user_name: str):
        super().__init__(user_id, user_chat_id, bot, user_name)
        self.random_diap = 120
        self.current_page = 0
        self.max_on_page = 7
        self.edit = None
        self.current_name = None
        self.current_session = None
        self.client: TelegramClient = None
        self.clients = []
        self.clients_names = []
        self.clients_index = 0
        self.current_page_acc = 0
        self.newname = None
        self.newurls = None
        self.newphotos = None
        self.newvideos = None
        self.newtext = None
        self.newlistposts = []
        self.is_test = False
        self.is_other = False
        self.hash_phone = None
        self.list_chats_other = db.get_other_user_chats()
        self.cooldoun_msg = config_controller.TIME_MSG_COOLDOWN

    def get_cool_down(self):
        diap = round(self.random_diap/2)
        return random.randint(-diap, diap)
    async def start_msg(self):
        if self.user_id in config_controller.list_is_loggin_admins:
            return Response(text="Список постів", buttons=markups.generate_post_menu(self.current_page, self.max_on_page))
        else:
            return Response(text="У вас недостатньо прав!", is_end=True)

    async def multiple_user_send(self, clients_list, user_chat_id, count_send: int, list_users: list, current_post_name, is_add_other = False):
        lists_user_list = []
        for c in clients_list:
            lists_user_list.append([])

        index = 0
        size_c = len(clients_list)

        for user in list_users:
            lists_user_list[index % size_c].append(user)
            index+=1
            if index == count_send or index > count_send:
                break

        tasks = []
        index = 0
        for c in clients_list:
            tasks.append(asyncio.create_task(self.messages_to_users(user_chat_id, len(lists_user_list[index]), lists_user_list[index], current_post_name, c, is_add_other)))
            index+=1
        for task in tasks:
            await task

    async def test_message_to_me(self, user_chat_id, current_post_name, user_name, client):
        try:
            msg = await self.bot.send_message(chat_id=user_chat_id,
                                        text="Розсилка розпочата, очікуйте повідомлення про завершення...")
            count = 0
            error = 0
            if config_controller.LIST_POSTS[current_post_name].get('list_posts', None) != None and len(
                    config_controller.LIST_POSTS[current_post_name].get('list_posts', [])) != 0:
                post = random.choice(config_controller.LIST_POSTS[current_post_name]['list_posts'])
            else:
                post = config_controller.LIST_POSTS[current_post_name]
            text_post = post['text']
            list_photos = post['photos']
            list_videos = post['videos']
            entity = await client.get_entity(user_name)
            name_user = entity.first_name
            if entity.last_name:
                name_user += " " + entity.last_name
            text_post = text_post.replace("%name%", name_user)
            text_post = text_post.replace("%name_k%", name_user)
            if list_photos and len(list_photos) == 1 and text_post:
                with open(list_photos[0], 'rb') as photo_file:
                    await client.send_file(entity, photo_file, caption=text_post,
                                                silent=True)
            elif list_photos and len(list_photos) == 1:
                with open(list_photos[0], 'rb') as photo_file:
                    await client.send_file(entity, photo_file, silent=True)
            elif list_photos and len(list_photos) > 1 and text_post:
                error += 1
            elif list_videos and len(list_videos) == 1 and text_post:
                with open(list_videos[0], 'rb') as video_file:
                    await client.send_file(entity, video_file, caption=text_post,
                                                silent=True)
            elif list_videos and len(list_videos) == 1:
                with open(list_videos[0], 'rb') as video_file:
                    await client.send_file(entity, video_file, silent=True)
            elif text_post:
                await client.send_message(entity, text_post, silent=True)
            count += 1
            await client.disconnect()
            try:
                await self.bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
            except:
                pass
            await self.bot.send_message(chat_id=self.user_chat_id, text="Розсилка закінчена!\nРозіслано людям: " + str(count) + "\nПомилок: " + str(error))
        except Exception as ex:
            print(ex)
            await client.disconnect()
            try:
                await self.bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
            except:
                pass
            await self.bot.send_message(chat_id=self.user_chat_id, text="Сталася помилка!")

    async def messages_to_users(self, user_chat_id, count_send: int, list_users: list, current_post_name, client, is_add_other = False):
        await asyncio.sleep(random.randint(1, 30))
        try:
            count = 0
            error = 0
            tmp_error = 0
            current_user = None
            msg = await self.bot.send_message(chat_id=user_chat_id,
                                              text="Статус "+self.clients_names[self.clients.index(client)]+" ["+config_controller.LIST_TG_ACC[self.clients_names[self.clients.index(client)]]['phone']+"]"+":\nВідправлено: " + str(count) + " з " + str(
                                                  count_send) + "\nПомилок: " + str(error))
            for user in list_users:
                current_user = user
                if count >= count_send:
                    break
                try:
                    chat_id = user.tg_id
                    if config_controller.LIST_POSTS[current_post_name].get('list_posts', None) != None and len(
                            config_controller.LIST_POSTS[current_post_name].get('list_posts', [])) != 0:
                        post = random.choice(config_controller.LIST_POSTS[current_post_name]['list_posts'])
                    else:
                        post = config_controller.LIST_POSTS[current_post_name]
                    text_post = post['text']
                    list_photos = post['photos']
                    list_videos = post['videos']
                    if text_post.count("%name_k%") != 0:
                        if user.name_k == None or user.name_k == "":
                            continue
                        text_post = text_post.replace("%name_k%", user.name_k)

                    if user.tg_name != None:
                        entity = await client.get_entity(user.tg_name)
                    else:
                        entity = await client.get_entity(user.phone.split(",")[0])

                    name_user = entity.first_name
                    if entity.last_name:
                        name_user += " " + entity.last_name
                    text_post = text_post.replace("%name%", name_user)
                    if list_photos and len(list_photos) == 1 and text_post:
                        with open(list_photos[0], 'rb') as photo_file:
                            await client.send_file(entity, photo_file, caption=text_post, silent=True)
                    elif list_photos and len(list_photos) == 1:
                        with open(list_photos[0], 'rb') as photo_file:
                            await client.send_file(entity, photo_file, silent=True)
                    elif list_photos and len(list_photos) > 1 and text_post:
                        error += 1
                        tmp_error += 1
                        if tmp_error > 5:
                            return
                        continue
                    elif list_videos and len(list_videos) == 1 and text_post:
                        with open(list_videos[0], 'rb') as video_file:
                            await client.send_file(entity, video_file, caption=text_post, silent=True)
                    elif list_videos and len(list_videos) == 1:
                        with open(list_videos[0], 'rb') as video_file:
                            await client.send_file(entity, video_file, silent=True)
                    elif text_post:
                        await client.send_message(entity, text_post, silent=True)
                    count += 1
                    if not is_add_other:
                        db.add_count_by_tg_id(str(chat_id))
                    else:
                        db.add_count_otheruser_by_tg_id(str(chat_id))
                    tmp_error = 0
                    await self.bot.edit_message_text(
                        text="Статус "+self.clients_names[self.clients.index(client)]+" ["+config_controller.LIST_TG_ACC[self.clients_names[self.clients.index(client)]]['phone']+"]"+":\nВідправлено: " + str(count) + " з " + str(count_send) + "\nПомилок: " + str(
                            error), chat_id=msg.chat.id, message_id=msg.id)
                    if count != count_send:
                        await asyncio.sleep(self.cooldoun_msg + self.get_cool_down())
                except (UserDeletedError, UserInvalidError, UserDeactivatedError, UsernameInvalidError) as ex:
                    print("DELETE USER", current_user, ex)
                    db.delete_userother_by_tg_id(current_user.tg_id)
                    await self.bot.edit_message_text(
                        text="[Знайдено видалений акаунт]\nСтатус " + self.clients_names[self.clients.index(client)] + " [" +
                             config_controller.LIST_TG_ACC[self.clients_names[self.clients.index(client)]][
                                 'phone'] + "]" + ":\nВідправлено: " + str(count) + " з " + str(
                            count_send) + "\nПомилок: " + str(
                            error), chat_id=msg.chat.id, message_id=msg.id)
                    if count != count_send:
                        await asyncio.sleep(self.cooldoun_msg + self.get_cool_down())
                except FloodWaitError as ex:
                    time_sleep = int(str(ex).split("A wait of ")[1].split(" ")[0])
                    print(self.clients_names[self.clients.index(client)], ex)
                    print("WAIT", time_sleep)

                    if time_sleep > 1000:
                        await self.bot.edit_message_text(
                            text="[Примусово закінчено] Статус"+self.clients_names[self.clients.index(client)]+" ["+config_controller.LIST_TG_ACC[self.clients_names[self.clients.index(client)]]['phone']+"]"+":\nВідправлено: " + str(
                                count) + " з " + str(
                                count_send) + "\nПомилок: " + str(error) + "\n(Анти флуд, очікування " + str(
                                time_sleep) + "секунд", chat_id=msg.chat.id, message_id=msg.id)
                        return
                    else:
                        await self.bot.edit_message_text(
                            text="Статус "+self.clients_names[self.clients.index(client)]+" ["+config_controller.LIST_TG_ACC[self.clients_names[self.clients.index(client)]]['phone']+"]"+":\nВідправлено: " + str(
                                count) + " з " + str(
                                count_send) + "\nПомилок: " + str(error) + "\n(Анти флуд, очікування " + str(
                                time_sleep) + "секунд", chat_id=msg.chat.id, message_id=msg.id)
                    await asyncio.sleep(time_sleep)
                    try:
                        chat_id = user.tg_id
                        if config_controller.LIST_POSTS[current_post_name].get('list_posts', None) != None and len(config_controller.LIST_POSTS[current_post_name].get('list_posts', [])) != 0:
                            post = random.choice(config_controller.LIST_POSTS[current_post_name]['list_posts'])
                        else:
                            post = config_controller.LIST_POSTS[current_post_name]
                        text_post = post['text']
                        list_photos = post['photos']
                        list_videos = post['videos']
                        if text_post.count("%name_k%") != 0:
                            if user.name_k == None or user.name_k == "":
                                continue
                            text_post = text_post.replace("%name_k%", user.name_k)

                        if user.tg_name != None:
                            entity = await client.get_entity(user.tg_name)
                        else:
                            entity = await client.get_entity(user.phone.split(",")[0])

                        name_user = entity.first_name
                        if entity.last_name:
                            name_user += " " + entity.last_name
                        text_post = text_post.replace("%name%", name_user)
                        if list_photos and len(list_photos) == 1 and text_post:
                            with open(list_photos[0], 'rb') as photo_file:
                                await client.send_file(entity, photo_file, caption=text_post, silent=True)
                        elif list_photos and len(list_photos) == 1:
                            with open(list_photos[0], 'rb') as photo_file:
                                await client.send_file(entity, photo_file, silent=True)
                        elif list_photos and len(list_photos) > 1 and text_post:
                            error += 1
                            tmp_error += 1
                            if tmp_error > 5:
                                return
                            continue
                        elif list_videos and len(list_videos) == 1 and text_post:
                            with open(list_videos[0], 'rb') as video_file:
                                await client.send_file(entity, video_file, caption=text_post, silent=True)
                        elif list_videos and len(list_videos) == 1:
                            with open(list_videos[0], 'rb') as video_file:
                                await client.send_file(entity, video_file, silent=True)
                        elif text_post:
                            await client.send_message(entity, text_post, silent=True)
                        count += 1
                        if not is_add_other:
                            db.add_count_by_tg_id(str(chat_id))
                        else:
                            db.add_count_otheruser_by_tg_id(str(chat_id))
                        tmp_error = 0
                        await self.bot.edit_message_text(text="Статус "+self.clients_names[self.clients.index(client)]+" ["+config_controller.LIST_TG_ACC[self.clients_names[self.clients.index(client)]]['phone']+"]"+":\nВідправлено: " + str(count) + " з " + str(
                            count_send) + "\nПомилок: " + str(error), chat_id=msg.chat.id, message_id=msg.id)
                        if count != count_send:
                            await asyncio.sleep(self.cooldoun_msg + self.get_cool_down())
                    except Exception as ex:
                        print(self.clients_names[self.clients.index(client)], ex)
                        if str(ex).startswith("No user has"):
                            print("DELETE USER", current_user, ex)
                            db.delete_userother_by_tg_id(current_user.tg_id)
                            await self.bot.edit_message_text(
                                text="[Знайдено видалений акаунт]\nСтатус " + self.clients_names[
                                    self.clients.index(client)] + " [" +
                                     config_controller.LIST_TG_ACC[self.clients_names[self.clients.index(client)]][
                                         'phone'] + "]" + ":\nВідправлено: " + str(count) + " з " + str(
                                    count_send) + "\nПомилок: " + str(
                                    error), chat_id=msg.chat.id, message_id=msg.id)
                            if count != count_send:
                                await asyncio.sleep(self.cooldoun_msg + self.get_cool_down())
                        error += 1
                        tmp_error += 1
                        if tmp_error > 5:
                            return
                        if not str(ex).startswith("No user has"):
                            await asyncio.sleep(random.randint(5, 30))
                except Exception as ex:
                    print(self.clients_names[self.clients.index(client)], ex)
                    if str(ex).startswith("No user has"):
                        print("DELETE USER", current_user, ex)
                        db.delete_userother_by_tg_id(current_user.tg_id)
                        await self.bot.edit_message_text(
                            text="[Знайдено видалений акаунт]\nСтатус " + self.clients_names[
                                self.clients.index(client)] + " [" +
                                 config_controller.LIST_TG_ACC[self.clients_names[self.clients.index(client)]][
                                     'phone'] + "]" + ":\nВідправлено: " + str(count) + " з " + str(
                                count_send) + "\nПомилок: " + str(
                                error), chat_id=msg.chat.id, message_id=msg.id)
                        if count != count_send:
                            await asyncio.sleep(self.cooldoun_msg + self.get_cool_down())
                    error += 1
                    tmp_error += 1
                    if tmp_error > 5:
                        return
                    if not str(ex).startswith("No user has"):
                        await asyncio.sleep(random.randint(5, 30))
            #await self.bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
            await client.disconnect()
            await self.bot.edit_message_text(
                text="[Закінчено]\nСтатус "+self.clients_names[self.clients.index(client)]+" ["+config_controller.LIST_TG_ACC[self.clients_names[self.clients.index(client)]]['phone']+"]"+":\nВідправлено: " + str(
                    count) + " з " + str(
                    count_send) + "\nПомилок: " + str(error), chat_id=msg.chat.id, message_id=msg.id)
        except Exception as ex:
            print(self.clients_names[self.clients.index(client)], ex)
            await client.disconnect()
            await self.bot.send_message(chat_id=self.user_chat_id, text=self.clients_names[self.clients.index(client)] + " Помилка!\n\n"+str(ex))

    async def next_msg(self, message: str):
        if not (self.user_id in config_controller.list_is_loggin_admins):
            return Response(text="У вас недостатньо прав!", is_end=True)
        if self.edit == "addname":
            if len(message) > 50:
                return Response(text="Ваша назва більша за 50 символів! Введіть меншу назву: ", buttons=markups.generate_cancel())
            self.newname = message
            self.edit = "addpost"
            return Response(text="Відправляйте постів скільки потрібно. Буде обиратись один випадковим чином та відправлятись.\n\nВідправте пост одним повідомленням (можна з фото або відео, та текстом, але одним повідомленням):", buttons=markups.generate_ready_exit())
        elif self.edit == "addpost":
            self.newtext = message
            self.edit = "addpost"
            self.newlistposts.append({'text': self.newtext,
                                      'urls': self.newurls,
                                      'photos': self.newphotos,
                                      'videos': self.newvideos})
            return Response(
                text="Відправляйте постів скільки потрібно. Буде обиратись один випадковим чином та відправлятись.\n\nВідправте пост одним повідомленням (можна з фото або відео, та текстом, але одним повідомленням):",
                buttons=markups.generate_ready_exit())
        elif self.edit == "code_enter":
            code = message.replace(".", "").replace("-", "").replace(" ", "")
            try:
                await self.clients[self.clients_names.index(self.unauth_clients_name[0])].sign_in(config_controller.LIST_TG_ACC[self.unauth_clients_name[0]]["phone"], code)
            except SessionPasswordNeededError:
                if config_controller.LIST_TG_ACC[self.unauth_clients_name[0]].get("password", None) != None:
                    await self.clients[self.clients_names.index(self.unauth_clients_name[0])].sign_in(password=config_controller.LIST_TG_ACC[self.unauth_clients_name[0]]["password"])
                else:
                    return Response(text="Потрібен пароль до цього акаунту! Видаліть його та створіть новий з паролем", redirect="/menu")
            if not await self.clients[self.clients_names.index(self.unauth_clients_name[0])].is_user_authorized():
                self.hash_phone = await self.clients[self.clients_names.index(self.unauth_clients_name[0])].send_code_request(config_controller.LIST_TG_ACC[self.unauth_clients_name[0]]["phone"])
                self.edit = "code_enter"
                return Response(
                    text="Ви не правильно ввели код\n"+self.unauth_clients_name[
                                         0]+" ["+config_controller.LIST_TG_ACC[self.unauth_clients_name[
                                         0]]['phone']+"]" + "\nНа акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):", buttons=markups.generate_cancel())
            else:
                self.unauth_clients_name.pop(0)
                if len(self.unauth_clients_name) == 0:
                    if not self.is_test:
                        self.edit = "count_send"
                        list_users = db.get_all_verify_users()
                        list_other = db.get_user_other_order()
                        return Response(text="Введіть кількість людей, котрим буде розсилатись пост:\n" + str(
                            len(list_users)) + " людей на даний момент в базі (Ваші люди, які парсились з таблиці ексель)\n" + str(
                            len(list_other)) + " людей з інших чатів у базі", buttons=markups.generate_cancel())
                    else:
                        await self.test_message_to_me(self.user_chat_id, self.current_name, self.user_name, self.clients[0])
                        return Response(redirect="/menu")
                else:
                    return Response(text=self.unauth_clients_name[
                                         0]+" ["+config_controller.LIST_TG_ACC[self.unauth_clients_name[
                                         0]]['phone']+"]" + "\nНа акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):")
        elif self.edit == "count_send":
            if self.is_other:
                try:
                    self.count_send = int(message)
                except:
                    return Response(text="Ви впевненні, що ввели число правильно? Спробуйте ще раз:",
                                buttons=markups.generate_cancel())
                self.current_page_chat = 0
                return Response(text="Людям з якого чату робити розсилку?", buttons=markups.generate_db_chats_menu(0, self.max_on_page))
            try:
                self.count_send = int(message)
                text_post: str = config_controller.LIST_POSTS[self.current_name]['text']
                list_users = db.get_user_verify_order((text_post.count("%name_k%") > 0))
                count_new = db.count_to_new_verify_user_by_chat((text_post.count("%name_k%") > 0))
                if self.count_send > count_new:
                    self.list_users_tmp = list_users
                    self.is_add_other = False
                    return Response(text="Ви хочете розіслати " + str(self.count_send) + " людям.\nДо закінчення черги та повернення до початку залишилось " +str(count_new) + " людини.\nМожливе повторне відсилання повідомлення!\n\nВи впевненні що хочете продовжити?", buttons=markups.generate_yes_no())
                else:
                    await self.multiple_user_send(self.clients, self.user_chat_id, self.count_send, list_users, self.current_name)
                    return Response(text="Розсилка закінчена!", redirect="/menu")
            except:
                return Response(text="Ви впевненні, що ввели число правильно? Спробуйте ще раз:", buttons=markups.generate_cancel())

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            if self.current_name == None:
                return Response(is_end=True, redirect="/menu")
            else:
                return Response(is_end=True, redirect="/postlist")
        elif data_btn == "/yes_ready":
            self.edit = None
            if config_controller.add_or_edit_post(self.newname,
                                                  self.newlistposts[0]['text'],
                                                  self.newlistposts[0]['urls'],
                                                  self.newlistposts[0]['photos'],
                                                  self.newlistposts[0]['videos'],
                                                  self.newlistposts):
                return Response(text="Успішно додані пости!", redirect="/postlist")
            else:
                return Response(text="Помилка при додаванні!", redirect="/postlist")
        elif data_btn == "/yes":
            await self.multiple_user_send(self.clients, self.user_chat_id, self.count_send, self.list_users_tmp, self.current_name, self.is_add_other)
            return Response(text="Розсилка закінчена!", redirect="/menu")
        elif data_btn == "/accnext":
            if len(config_controller.LIST_TG_ACC)-((self.current_page_acc+1)*self.max_on_page) > 0:
                self.current_page_acc+=1
            return Response(text="Оберіть акаунт чи акаунти:", buttons=markups.generate_tg_acc_menu(self.current_page_acc*self.max_on_page, self.max_on_page, with_ready=True, list_check=self.clients_names))
        elif data_btn =="/accprev":
            if self.current_page_acc > 0:
                self.current_page_acc-=1
            return Response(text="Оберіть акаунт чи акаунти:", buttons=markups.generate_tg_acc_menu(self.current_page_acc*self.max_on_page, self.max_on_page, with_ready=True, list_check=self.clients_names))
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
            text += "\nКількість варіацій поста: " + str(
                len(config_controller.LIST_POSTS[self.current_name].get('list_posts', []))) + "\n"
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
            return Response(text="Виберіть акаунт для розсилки:", buttons=markups.generate_tg_acc_menu(self.current_page_acc*self.max_on_page, self.max_on_page, with_ready=True))
        elif data_btn == "/sendme":
            self.is_test = True
            return Response(text="Виберіть акаунт для розсилки:", buttons=markups.generate_tg_acc_menu(self.current_page_acc*self.max_on_page, self.max_on_page, with_ready=True))
        elif data_btn == "/send":
            return Response(text="Виберіть акаунт для розсилки:", buttons=markups.generate_tg_acc_menu(self.current_page_acc*self.max_on_page, self.max_on_page, with_ready=True))
        elif data_btn in config_controller.LIST_TG_ACC:
            if not (data_btn in self.clients_names):
                self.clients_names.append(data_btn)
            else:
                self.clients_names.remove(data_btn)
            if not self.is_test:
                return Response(text="Виберіть акаунт для розсилки:",
                            buttons=markups.generate_tg_acc_menu(self.current_page_acc * self.max_on_page,
                                                                 self.max_on_page, list_check=self.clients_names, with_ready=True))
            else:
                await self.init_clients(self.clients_names)
                if len(self.unauth_clients_name) == 0:
                    await self.test_message_to_me(self.user_chat_id, self.current_name, self.user_name, self.clients[0])
                    return Response(redirect="/menu")
                else:
                    return Response(text=self.unauth_clients_name[
                                         0]+" ["+config_controller.LIST_TG_ACC[self.unauth_clients_name[
                                         0]]['phone']+"]" + "\nНа акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):")
        elif data_btn == "/ready":
            await self.init_clients(self.clients_names)
            if len(self.unauth_clients_name) == 0:
                self.edit = "count_send"
                list_users = db.get_all_verify_users()
                list_other = db.get_user_other_order()
                return Response(text="Введіть кількість людей, котрим буде розсилатись пост:\n" + str(
                            len(list_users)) + " людей на даний момент в базі (Ваші люди, які парсились з таблиці ексель)\n" + str(len(list_other)) + " людей з інших чатів у базі", buttons=markups.generate_cancel())
            else:
                return Response(text=self.unauth_clients_name[
                                         0]+" ["+config_controller.LIST_TG_ACC[self.unauth_clients_name[
                                         0]]['phone']+"]" + "\nНа акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):")
        elif data_btn == "/any":
            try:
                text_post: str = config_controller.LIST_POSTS[self.current_name]['text']
                list_users = db.get_user_other_order((text_post.count("%name_k%") > 0))
                count_new = db.count_to_new_user_other((text_post.count("%name_k%") > 0))
                if self.count_send > count_new:
                    self.list_users_tmp = list_users
                    self.is_add_other = True
                    return Response(text="Ви хочете розіслати " + str(
                        self.count_send) + " людям.\nДо закінчення черги та повернення до початку залишилось " + str(
                        count_new) + " людини.\nМожливе повторне відсилання повідомлення!\n\nВи впевненні що хочете продовжити?",
                                    buttons=markups.generate_yes_no())
                else:
                    await self.multiple_user_send(self.clients, self.user_chat_id, self.count_send, list_users,
                                                  self.current_name, is_add_other=True)
                    return Response(text="Розсилка закінчена!", redirect="/menu")
            except Exception as ex:
                print(ex)
                return Response(text="Сталася помилка!", redirect="/menu")

        elif data_btn in db.get_other_user_chats():
            self.chat_send = data_btn
            try:
                text_post: str = config_controller.LIST_POSTS[self.current_name]['text']
                list_users = db.get_user_other_order_by_chats(self.chat_send, (text_post.count("%name_k%") > 0))
                count_new = db.count_to_new_user_other_by_chat(self.chat_send, (text_post.count("%name_k%") > 0))
                if self.count_send > count_new:
                    self.list_users_tmp = list_users
                    self.is_add_other = True
                    return Response(text="Ви хочете розіслати " + str(
                        self.count_send) + " людям.\nДо закінчення черги та повернення до початку залишилось " + str(
                        count_new) + " людини.\nМожливе повторне відсилання повідомлення!\n\nВи впевненні що хочете продовжити?",
                                    buttons=markups.generate_yes_no())
                else:
                    await self.multiple_user_send(self.clients, self.user_chat_id, self.count_send, list_users,
                                                  self.current_name, is_add_other=True)
                    return Response(text="Розсилка закінчена!", redirect="/menu")
            except Exception as ex:
                print(ex)
                return Response(text="Сталася помилка!", redirect="/menu")

    async def init_clients(self, clients_names):
        self.unauth_clients_name = []
        self.clients = []
        for acc in clients_names:
            if config_controller.LIST_TG_ACC[acc].get("proxy", None) != None:
                ipport = config_controller.LIST_TG_ACC[acc].get("proxy", None)
                proxy_obj = db.get_proxy_by_ip_port(ipport.split(":")[0], ipport.split(":")[1])[0]
                proxy = (proxy_obj.type_proxy, proxy_obj.ip, int(proxy_obj.port), True, proxy_obj.login, proxy_obj.password)
                self.current_session = acc
                self.clients.append(TelegramClient(session=self.current_session, api_id=config_controller.LIST_TG_ACC[self.current_session]["api_id"], api_hash=config_controller.LIST_TG_ACC[self.current_session]["api_hash"], proxy=proxy))
            else:
                self.current_session = acc
                self.clients.append(TelegramClient(session=self.current_session,
                                                   api_id=config_controller.LIST_TG_ACC[self.current_session]["api_id"],
                                                   api_hash=config_controller.LIST_TG_ACC[self.current_session][
                                                       "api_hash"]))
            await self.clients[-1].connect()
            if not await self.clients[-1].is_user_authorized():
                await self.clients[-1].send_code_request(config_controller.LIST_TG_ACC[self.current_session]["phone"])
                self.unauth_clients_name.append(acc)
        if len(self.unauth_clients_name) != 0:
            self.edit = "code_enter"


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
            self.edit = "addpost"

            self.newlistposts.append({'text': self.newtext,
                                      'urls': self.newurls,
                                      'photos': self.newphotos,
                                      'videos': self.newvideos})

            return Response(
                text="Відправляйте постів скільки потрібно. Буде обиратись один випадковим чином та відправлятись.\n\nВідправте пост одним повідомленням (можна з фото або відео, та текстом, але одним повідомленням):",
                buttons=markups.generate_ready_exit())