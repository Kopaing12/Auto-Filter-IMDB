
import time
import os
import logging
from logging.handlers import RotatingFileHandler


# Get a bot token from botfather
TG_BOT_TOKEN ="5476898127:AAES0EVnVgpxYC8WSc0gXlIaxAHdVvktP38"

# Get from my.telegram.org (or @UseTGXBot)
APP_ID =  "7051195"

# Get from my.telegram.org (or @UseTGXBot)
API_HASH = "a36d0269f12722e154f89ff5f0135f04"

# Generate a user session string 
TG_USER_SESSION = os.environ.get("TG_USER_SESSION", 'Media_search')

# Database URL from https://cloud.mongodb.com/
DATABASE_URI = os.environ.get("DATABASE_URI", "mongodb+srv://bot1:bot1@cluster0.fqzak9o.mongodb.net/?retryWrites=true&w=majority")

# Your database name from mongoDB
DATABASE_NAME = os.environ.get("DATABASE_NAME", "Cluster12")
DATABASE_NAME2 = str(os.environ.get("DATABASE_NAME2", "Unlimited2"))

# ID of users that can use the bot commands
AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "1113630298").split())
ADMINS = AUTH_USERS

# Should bot search for document files in channels
DOC_SEARCH = os.environ.get("DOC_SEARCH", "yes").lower()

# Should bot search for video files in channels
VID_SEARCH = os.environ.get("VID_SEARCH", "yes").lower()

# Should bot search for music files in channels
MUSIC_SEARCH = os.environ.get("MUSIC_SEARCH", "yes").lower()

# To save user details (Usefull for getting userinfo and total user counts)
# May reduce filter capacity :(
# Give yes or no
SAVE_USER = os.environ.get("SAVE_USER", "yes").lower()


# Go to https://dashboard.heroku.com/account, scroll down and press Reveal API
# To check dyno status
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", "False")




TG_BOT_SESSION = os.environ.get("TG_BOT_SESSION", "bot")
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))
LOG_FILE_NAME = "filterbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)




class Config(object):




    # OPTIONAL - To set alternate BOT COMMANDS
    ADD_FILTER_CMD = os.environ.get("ADD_FILTER_CMD", "add")
    DELETE_FILTER_CMD = os.environ.get("DELETE_FILTER_CMDD", "del")
    DELETE_ALL_CMD = os.environ.get("DELETE_ALL_CMDD", "delall")
    CONNECT_COMMAND = os.environ.get("CONNECT_COMMANDD", "connect")
    DISCONNECT_COMMAND = os.environ.get("DISCONNECT_COMMANDD", "disconnect")


    # To record start time of bot
    BOT_START_TIME = time.time()


IMDB_TEXT = """**Hey [{user}](https://t.me/{un}) Your ~~{query} movie~~ is Ready** 🍁

__📺 **Movie** : **{title}**
📆 **Year** : {year}
🎙️ **Audio** : {languages}
🏃 **Time** : {runtime} Minutes
🌟 **Rating** : {rating}/10
🔖 **Genres** : {genres}__

**🙋🏼 Request by : [{user}](https://t.me/{un})** """



