import time

LOGGER_LIST = []


def add_log(ex):
    global LOGGER_LIST

    if len(LOGGER_LIST) > 1000:
        LOGGER_LIST.pop(0)

    t = time.localtime(time.time())
    text = str(t.tm_hour) +":"+str(t.tm_min)+":"+str(t.tm_sec)+"\t [LOG] \t"+ str(ex)
    LOGGER_LIST.append(text)

def get_log():
    with open("log.txt", 'w') as file:
        for i in LOGGER_LIST:
            file.write(i+"\n")
    return "log.txt"