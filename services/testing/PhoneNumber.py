import re
import db.database as db


def validate_phone_number(phone_number: str):
    pattern = r'^\+380\d{9}$'
    if re.match(pattern, phone_number):
        return True
    else:
        return False

def clr_str(text: str):
    return text.replace("?", "").replace(".", "").replace(" ", "").replace("-", "").replace("_", "").replace(" ", "")

def ending_prepare(text: str):
    if text.startswith("+380"):
        return text
    if text.startswith("0"):
        text = "+38" + text
        return text
    elif text.startswith("380"):
        text = "+"+text
        return text
    else:
        text = "+380" + text
        return text

def str_to_phone_list(phone: str):
    phones = []
    if validate_phone_number(phone):
        print(phone, "--->", [phone])
        return [phone]
    if phone.count(",") != 0:
        l = phone.split(",")
        for i in l:
            if len(i) > 8:
                tmp = clr_str(i)
                tmp = ending_prepare(tmp)
                phones.append(tmp)
    elif phone.count(";") != 0:
        l = phone.split(";")
        for i in l:
            if len(i) > 8:
                tmp = clr_str(i)
                tmp = ending_prepare(tmp)
                phones.append(tmp)
    elif phone.count("  ") != 0:
        l = phone.split("  ")
        for i in l:
            if len(i) > 8:
                tmp = clr_str(i)
                tmp = ending_prepare(tmp)
                phones.append(tmp)
    elif phone.count("  ") != 0:
        l = phone.split("  ")
        for i in l:
            if len(i) > 8:
                tmp = clr_str(i)
                tmp = ending_prepare(tmp)
                phones.append(tmp)
    else:
        tmp = clr_str(phone)
        tmp = ending_prepare(tmp)
        phones.append(tmp)
    validated = []
    for i in phones:
        if validate_phone_number(i):
            validated.append(i)
    print(phone, "--->", validated)
    return validated

def test():
    pp = db.get_all_users()
    for i in pp:
        list_phone = str_to_phone_list(i.phone)
        if len(list_phone) != 0:
            i.valid_phone = ",".join(list_phone)
            db.session_commit(i)
