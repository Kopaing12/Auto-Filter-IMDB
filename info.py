import re
from os import environ

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default
      
      
PICS = (environ.get('PICS', 'https://telegra.ph/file/14c978d31fb9372e79624.jpg https://telegra.ph/file/a5ee7fc4b2d89fe900321.jpg')).split()
PICS2 = (environ.get('PICS', 'https://telegra.ph/file/14c978d31fb9372e79624.jpg https://telegra.ph/file/a5ee7fc4b2d89fe900321.jpg')).split()




auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None


LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', 0))
