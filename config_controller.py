import os
import pickle

PASSWORD_ADMIN = "admin"

TIME_MSG_COOLDOWN = 180

LIST_POSTS = {}
# {"name":{"text": str,
#          "urls": [str],
#          "photos": [str],
#           "videos": [str]
#          }}

LIST_TG_ACC = {}
# {"name": {"session": session,
#           "phone": phone,
#           "api_id": api_id,
#           "api_hash": api_hash}}


list_is_loggin_admins = []

def preload_config():
    if os.path.exists("config.bin"):
        read_ini()
    else:
        write_ini()
def write_ini():
    config = {}
    config["PASSWORD_ADMIN"] = PASSWORD_ADMIN
    config["LIST_POSTS"] = LIST_POSTS
    config["LIST_TG_ACC"] = LIST_TG_ACC
    config["TIME_MSG_COOLDOWN"] = TIME_MSG_COOLDOWN
    with open('config.bin', 'wb') as configfile:
        pickle.dump(config, configfile)

def set_proxy_acc(name: str, ipport:str = None):
    LIST_TG_ACC[name]["proxy"] = ipport
    write_ini()

def get_proxy_acc(name: str):
    return LIST_TG_ACC[name].get("proxy", None)

def read_ini():
    global PASSWORD_ADMIN, LIST_POSTS, LIST_TG_ACC, TIME_MSG_COOLDOWN
    with open('config.bin', 'rb') as configfile:
        config = pickle.load(configfile)
        PASSWORD_ADMIN = str(config["PASSWORD_ADMIN"])
        LIST_POSTS = config.get("LIST_POSTS", LIST_POSTS)
        LIST_TG_ACC = config.get("LIST_TG_ACC", LIST_TG_ACC)
        TIME_MSG_COOLDOWN = config.get("TIME_MSG_COOLDOWN", TIME_MSG_COOLDOWN)


def del_post(key):
    global LIST_POSTS
    if LIST_POSTS.get(key, None) != None:
        if LIST_POSTS[key]['photos'] != None:
            for i in LIST_POSTS[key]['photos']:
                try:
                    os.remove(i)
                except Exception as ex:
                    pass
        if LIST_POSTS[key]['videos'] != None:
            for i in LIST_POSTS[key]['videos']:
                try:
                    os.remove(i)
                except Exception as ex:
                    pass
        LIST_POSTS.__delitem__(key)
        write_ini()
        return True
    else:
        return False

def is_id_post(id:int):
    for i in LIST_POSTS:
        if LIST_POSTS[i]['id'] == id:
            return False
    return True

def get_id_post():
    id = 0
    while(not is_id_post(id)):
        id+=1
    return id


def add_or_edit_post(key: str, text: str = None, urls: list = None, photos: list = None, videos: list = None):
    global LIST_POSTS
    try:
        v_key = key
        v_text = text
        v_urls = urls
        v_photos = photos
        v_videos = videos
        id = get_id_post()
        LIST_POSTS[v_key] = {'text': v_text,
                                 'urls': v_urls,
                             'photos': v_photos,
                             'videos': v_videos,
                             'id': id}
        write_ini()
        return True
    except Exception as ex:
        print(ex)
        return False

def log(chat_id, password):
    global list_is_loggin_admins
    if password == PASSWORD_ADMIN and (not chat_id in list_is_loggin_admins):
        list_is_loggin_admins.append(chat_id)
        return True
    elif chat_id in list_is_loggin_admins:
        return True
    return False

def change_password_admin(chat_id, password):
    global PASSWORD_ADMIN, list_is_loggin_admins
    if chat_id in list_is_loggin_admins:
        PASSWORD_ADMIN = password
        write_ini()
        list_is_loggin_admins = []
        return True
    else:
        return False

def add_or_edit_tg_acc(session: str, api_id: str, api_hash: str, phone: str, password: str = None):
    global LIST_TG_ACC
    LIST_TG_ACC[session] = {"api_id": api_id,
                            "api_hash": api_hash,
                            "phone": phone,
                            "password": password}
    write_ini()

def del_tg_acc(session: str):
    global LIST_TG_ACC
    if session in LIST_TG_ACC:
        LIST_TG_ACC.pop(session)
        write_ini()
        try:
            os.remove(session+".session")
        except:
            pass
        return True
    return False

def change_time_cooldown(new: int):
    global TIME_MSG_COOLDOWN
    TIME_MSG_COOLDOWN = new
    write_ini()