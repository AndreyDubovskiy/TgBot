from telebot import types
import db.database as db
import config_controller


def generate_db_chats_menu(offset: int=0, max:int = 5):
    chats_list = db.get_other_user_chats()
    if offset > len(chats_list):
        offset = 0
    current_elem = 0
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in chats_list:
        current_elem+=1
        if current_elem > offset and current_elem-offset <= max:
            markup.add(types.InlineKeyboardButton(text=i, callback_data=i))
        else:
            pass
    if len(chats_list) > max:
        markup.add(types.InlineKeyboardButton(text="-->", callback_data="/cnext"))
        markup.add(types.InlineKeyboardButton(text="<--", callback_data="/cprev"))
    markup.add(types.InlineKeyboardButton(text="Всім", callback_data="/any"))
    markup.add(types.InlineKeyboardButton(text="Відмінити", callback_data="/cancel"))
    return markup

def generate_post_menu(offset: int=0, max:int = 5):
    if offset > len(config_controller.LIST_POSTS):
        offset = 0
    current_elem = 0
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in config_controller.LIST_POSTS:
        current_elem+=1
        if current_elem > offset and current_elem-offset <= max:
            markup.add(types.InlineKeyboardButton(text=i, callback_data=i))
        else:
            pass
    if len(config_controller.LIST_POSTS) >= max:
        markup.add(types.InlineKeyboardButton(text="-->", callback_data="/next"))
        markup.add(types.InlineKeyboardButton(text="<--", callback_data="/prev"))
    markup.add(types.InlineKeyboardButton(text="Додати", callback_data="/add"))
    markup.add(types.InlineKeyboardButton(text="Відмінити", callback_data="/cancel"))
    return markup

def generate_post_semimenu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="Видалити", callback_data="/delete"))
    markup.add(types.InlineKeyboardButton(text="Розіслати вашим людям", callback_data="/send"))
    markup.add(types.InlineKeyboardButton(text="Розіслати людям з чатів", callback_data="/csend"))
    markup.add(types.InlineKeyboardButton(text="Тест (Відправити мені)", callback_data="/sendme"))
    markup.add(types.InlineKeyboardButton(text="Відмінити", callback_data="/cancel"))
    return markup

def generate_tg_acc_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in config_controller.LIST_TG_ACC:
        markup.add(types.InlineKeyboardButton(text=i, callback_data=i))
    markup.add(types.InlineKeyboardButton(text="Додати", callback_data="/add"))
    markup.add(types.InlineKeyboardButton(text="Відмінити", callback_data="/cancel"))
    return markup

def generate_tg_acc_menu2():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in config_controller.LIST_TG_ACC:
        markup.add(types.InlineKeyboardButton(text=i, callback_data=i))
    markup.add(types.InlineKeyboardButton(text="Відмінити", callback_data="/cancel"))
    return markup

def generate_tg_acc_semimenu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="Видалити", callback_data="/delete"))
    markup.add(types.InlineKeyboardButton(text="Розіслати", callback_data="/send"))
    markup.add(types.InlineKeyboardButton(text="Відмінити", callback_data="/cancel"))
    return markup


def generate_cancel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="Відмінити", callback_data="/cancel"))
    return markup

def generate_markup_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="Ввести пароль", callback_data="/log"))
    markup.add(types.InlineKeyboardButton(text="Змінити пароль адміна", callback_data="/passwordadmin"))
    markup.add(types.InlineKeyboardButton(text="Список постів", callback_data="/postlist"))
    markup.add(types.InlineKeyboardButton(text="Список акаунтів", callback_data="/tgacc"))
    markup.add(types.InlineKeyboardButton(text="Парсинг з файлу", callback_data="/parse"))
    markup.add(types.InlineKeyboardButton(text="Перевірка в телеграм", callback_data="/parsetg"))
    markup.add(types.InlineKeyboardButton(text="Зміна часу затримки", callback_data="/time"))
    markup.add(types.InlineKeyboardButton(text="Парсинг чатів на акаунті", callback_data="/parsechats"))
    markup.add(types.InlineKeyboardButton(text="Генерація таблиці Exel", callback_data="/exel"))
    markup.add(types.InlineKeyboardButton(text="Зміна імен у кличному", callback_data="/exelinput"))
    return markup