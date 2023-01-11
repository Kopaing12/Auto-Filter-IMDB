#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @trojanzhex


import re
import pyrogram
import os
import re
import io
import pyrogram
import random

from info import PICS, PICS2

from pyrogram import (
    filters,
    Client, 
    enums
)

from pyrogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    Message,
    CallbackQuery
)

from bot import Bot
from script import script
from database.mdb import searchquery
from plugins.channel import deleteallfilters
from config import AUTH_USERS, IMDB_TEXT
from Omdb import get_posters
from database.connections_mdb import active_connection
from database.users_mdb import add_user, all_users
from plugins.helpers import parser,split_quotes
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from database.filters_mdb import(
   add_filter,
   find_filter,
   get_filters,
   delete_filter,
   count_filters
)

BUTTONS = {}


@Client.on_message(filters.command(Config.ADD_FILTER_CMD))
async def addfilter(client, message):
      
    userid = message.from_user.id
    chat_type = message.chat.type
    args = message.text.html.split(None, 1)

    if chat_type == "private":
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if not ((st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS)):
        return
        

    if len(args) < 2:
        await message.reply_text("Command Incomplete :(", quote=True)
        return
    
    extracted = split_quotes(args[1])
    text = extracted[0].lower()
   
    if not message.reply_to_message and len(extracted) < 2:
        await message.reply_text("Add some content to save your filter!", quote=True)
        return

    if (len(extracted) >= 2) and not message.reply_to_message:
        reply_text, btn, alert = parser(extracted[1], text)
        fileid = None
        if not reply_text:
            await message.reply_text("You cannot have buttons alone, give some text to go with it!", quote=True)
            return

    elif message.reply_to_message and message.reply_to_message.reply_markup:
        try:
            rm = message.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            msg = message.reply_to_message.document or\
                  message.reply_to_message.video or\
                  message.reply_to_message.photo or\
                  message.reply_to_message.audio or\
                  message.reply_to_message.animation or\
                  message.reply_to_message.sticker
            if msg:
                fileid = msg.file_id
                reply_text = message.reply_to_message.caption.html
            else:
                reply_text = message.reply_to_message.text.html
                fileid = None
            alert = None
        except:
            reply_text = ""
            btn = "[]" 
            fileid = None
            alert = None

    elif message.reply_to_message and message.reply_to_message.photo:
        try:
            fileid = message.reply_to_message.photo.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.video:
        try:
            fileid = message.reply_to_message.video.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.audio:
        try:
            fileid = message.reply_to_message.audio.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
   
    elif message.reply_to_message and message.reply_to_message.document:
        try:
            fileid = message.reply_to_message.document.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.animation:
        try:
            fileid = message.reply_to_message.animation.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.sticker:
        try:
            fileid = message.reply_to_message.sticker.file_id
            reply_text, btn, alert =  parser(extracted[1], text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.text:
        try:
            fileid = None
            reply_text, btn, alert = parser(message.reply_to_message.text.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    else:
        return
    
    await add_filter(grp_id, text, reply_text, btn, fileid, alert)

    await message.reply_text(
        f"Filter for  `{text}`  added in  **{title}**",
        quote=True,
        parse_mode="md"
    )


@Client.on_message(filters.command('viewfilters'))
async def get_all(client, message):
    
    chat_type = message.chat.type
    userid = message.from_user.id
    if chat_type == "private":
        
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if not ((st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS)):
        return

    texts = await get_filters(grp_id)
    count = await count_filters(grp_id)
    if count:
        filterlist = f"Total number of filters in **{title}** : {count}\n\n"

        for text in texts:
            keywords = " ×  `{}`\n".format(text)
            
            filterlist += keywords

        if len(filterlist) > 4096:
            with io.BytesIO(str.encode(filterlist.replace("`", ""))) as keyword_file:
                keyword_file.name = "keywords.txt"
                await message.reply_document(
                    document=keyword_file,
                    quote=True
                )
            return
    else:
        filterlist = f"There are no active filters in **{title}**"

    await message.reply_text(
        text=filterlist,
        quote=True,
        parse_mode="md"
    )
        
@Client.on_message(filters.command(Config.DELETE_FILTER_CMD))
async def deletefilter(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        grpid  = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)

    elif (chat_type == "group") or (chat_type == "supergroup"):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if not ((st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS)):
        return

    try:
        cmd, text = message.text.split(" ", 1)
    except:
        await message.reply_text(
            "<i>Mention the filtername which you wanna delete!</i>\n\n"
            "<code>/del filtername</code>\n\n"
            "Use /viewfilters to view all available filters",
            quote=True
        )
        return

    query = text.lower()

    await delete_filter(message, query, grp_id)
        

@Client.on_message(filters.command(Config.DELETE_ALL_CMD))
async def delallconfirm(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        grpid  = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (st.status == "creator") or (str(userid) in Config.AUTH_USERS):
        await message.reply_text(
            f"This will delete all filters from '{title}'.\nDo you want to continue??",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="YES",callback_data="delallconfirm")],
                [InlineKeyboardButton(text="CANCEL",callback_data="delallcancel")]
            ]),
            quote=True
        )



 
@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        key = f"{message.message_id}_{message.chat.id}"
        if message.text.startswith("/"):
            return 
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return

    if 2 < len(message.text) < 100:    
        
        btn = []

        group_id = message.chat.id
        name = message.text
        search = message.text
      
        filenames, links = await searchquery(group_id, name)
        if filenames and links:
            for filename, link in zip(filenames, links):
                btn.append(
                    [InlineKeyboardButton(text=f" 🇲🇲 {filename}",url=f"{link}")]
                )
        else:
            return

        if not btn:
            return

        if len(btn) > 6: 
            btns = list(split_list(btn, 6)) 
            
            keyword = f" 🇲🇲 {message.chat.id}-{message.message_id}"
            BUTTONS[keyword] = {
                "total" : len(btns),
                "buttons" : btns
            }
        else:
            buttons = btn
            buttons.append(
                [InlineKeyboardButton("🙅‍♂️ ဝင်မရရင် ဒီမှာလေ့လာပါ 🙅‍♂️", url="https://t.me/Movie_Zone_KP/3")]
            )
            buttons.append(
                [InlineKeyboardButton(text="🔰 𝗣𝗔𝗚𝗘  1/1 🔰",callback_data="pages")]
            )
            
            imdb=await get_posters(name)
            if imdb:
                cap = IMDB_TEXT.format(un=message.from_user.username, user=message.from_user.first_name, query=name, title=imdb['title'], trailer=imdb["trailer"], runtime=imdb["runtime"], languages=imdb["languages"], genres=imdb['genres'], year=imdb['year'], rating=imdb['rating'], url=imdb['url'])                                                  
            else:
                cap = f"Your ~~{message.text} ~~ is Ready** 🍁 \nRequest by :[{message.from_user.first_name}]({message.from_user.username})\nTotal Results : {len(btn)}\n\n<i><b>🔰 {message.chat.title} 🔰</b></a>"    

            if imdb and imdb.get('poster'):
                try:                   
                    await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="md")                               
                except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                    pic = imdb.get('poster')
                    poster = pic.replace('.jpg', "._V1_UX360.jpg")
                    await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(buttons), parse_mode="md")
                except Exception as e:
                    logger.exception(e)
                    await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="md") 
            else: 
                await message.reply_text(
                    text=f"Your ~~{message.text} ~~ is Ready** 🍁 \nRequest by :[{message.from_user.first_name}]({message.from_user.username})\nTotal Results : {len(btn)}\n\n🔰 {message.chat.title} 🔰",         
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode="md"
                )
            return

             
        data = BUTTONS[keyword]
        buttons = data['buttons'][0].copy()
        
        buttons.append(
            [InlineKeyboardButton("🙅‍♂️ ဝင်မရရင် ဒီမှာလေ့လာပါ 🙅‍♂️", url="https://t.me/Movie_Zone_KP/3")]
        )    
        buttons.append(
            [InlineKeyboardButton(text=f"🔰 𝗣𝗔𝗚𝗘 1/{data['total']} 🔰",callback_data="pages"),InlineKeyboardButton(text="𝐍𝐞𝐱𝐭 𝐏𝐚𝐠𝐞 ⏩",callback_data=f"next_0_{keyword}")]
        )
        

        imdb=await get_posters(name)
        if imdb:
            cap = IMDB_TEXT.format(un=message.from_user.username, user=message.from_user.first_name, query=name, title=imdb['title'], trailer=imdb["trailer"], runtime=imdb["runtime"], languages=imdb["languages"], genres=imdb['genres'], year=imdb['year'], rating=imdb['rating'], url=imdb['url'])                                                  
        else:
            cap = f"Your ~~{message.text} ~~ is Ready** 🍁 \nRequest by : [{message.from_user.first_name}]({message.from_user.username})\nTotal Results : {len(btn)}\n\n🔰 {message.chat.title} 🔰"    

        if imdb and imdb.get('poster'):
            try:                   
                await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="md")                               
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(buttons), parse_mode="md")
            except Exception as e:
                logger.exception(e)
                await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="md") 
        else: 
            await message.reply_text(
                text=f"Your ~~{message.text} ~~ is Ready** 🍁 \nRequest by : [{message.from_user.first_name}]({message.from_user.username})\nTotal Results : {len(btn)}\n\n🔰 {message.chat.title} 🔰",         
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="md"
            )

@Client.on_callback_query()
async def cb_handler(client: Bot, message):
    clicked = query.from_user.id
    typed = message.reply_to_message.id if message.reply_to_message else message.id
    
    if (clicked == typed) or (clicked in AUTH_USERS):

        if message.data.startswith("next"):
            await query.answer()
            ident, index, keyword = query.data.split("_")
            try:
                data = BUTTONS[keyword]
            except KeyError:
                await query.answer("You are using this for one of my old message, please send the request again.",show_alert=True)
                return

            if int(index) == int(data["total"]) - 2:
                buttons = data['buttons'][int(index)+1].copy()

                buttons.append(
                    [InlineKeyboardButton("🙅‍♂️ ဝင်မရရင် ဒီမှာလေ့လာပါ 🙅‍♂️", url="https://t.me/Movie_Zone_KP/3")]
                )
                buttons.append(
                    [InlineKeyboardButton("⏪ 𝗕𝗔𝗖𝗞 𝗣𝗔𝗚𝗘", callback_data=f"back_{int(index)+1}_{keyword}"),InlineKeyboardButton(f"🔰 𝗣𝗔𝗚𝗘 {int(index)+2}/{data['total']} 🔰", callback_data="pages")]
                )

                await query.edit_message_reply_markup( 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
            else:
                buttons = data['buttons'][int(index)+1].copy()

                buttons.append(
                    [InlineKeyboardButton("🙅‍♂️ ဝင်မရရင် ဒီမှာလေ့လာပါ 🙅‍♂️", url="https://t.me/Movie_Zone_KP/3")]
                )
                buttons.append(
                    [InlineKeyboardButton("⏪ 𝗕𝗔𝗖𝗞", callback_data=f"back_{int(index)+1}_{keyword}"),InlineKeyboardButton(f"𝗣𝗔𝗚𝗘 {int(index)+2}/{data['total']}", callback_data="pages"),InlineKeyboardButton("𝐍𝐞𝐱𝐭 ⏩", callback_data=f"next_{int(index)+1}_{keyword}")]
                )

                await query.edit_message_reply_markup( 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return


        elif query.data.startswith("back"):
            await query.answer()
            ident, index, keyword = query.data.split("_")
            try:
                data = BUTTONS[keyword]
            except KeyError:
                await query.answer("Search Expired\nPlease send movie name again.\n\nရှာဖွေမှု သက်တမ်းကုန်သွားပါပြီ။\nကျေးဇူးပြု၍ ရုပ်ရှင်အမည်ကို \nGroup ထဲ‌တွင် ထပ်မံပေးပို့ပါ။\n\n**@Movie_Zone_KP**",show_alert=True)
                return

            if int(index) == 1:
                buttons = data['buttons'][int(index)-1].copy()

                buttons.append(
                    [InlineKeyboardButton("🙅‍♂️ ဝင်မရရင် ဒီမှာလေ့လာပါ 🙅‍♂️", url="https://t.me/Movie_Zone_KP/3")]
                )
                buttons.append(
                    [InlineKeyboardButton(f"🔰 𝗣𝗔𝗚𝗘 {int(index)}/{data['total']} 🔰", callback_data="pages"),InlineKeyboardButton("𝐍𝐞𝐱𝐭 𝐏𝐚𝐠𝐞 ⏩", callback_data=f"next_{int(index)-1}_{keyword}")]
                )               
                
  
                await query.edit_message_reply_markup( 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return   
            else:
                buttons = data['buttons'][int(index)-1].copy()

                buttons.append(
                    [InlineKeyboardButton("🙅‍♂️ ဝင်မရရင် ဒီမှာလေ့လာပါ 🙅‍♂️", url="https://t.me/Movie_Zone_KP/3")]
                )
                buttons.append(
                    [InlineKeyboardButton("⏪ 𝗕𝗔𝗖𝗞", callback_data=f"back_{int(index)-1}_{keyword}"),InlineKeyboardButton(f"𝗣𝗔𝗚𝗘 {int(index)}/{data['total']}", callback_data="pages"),InlineKeyboardButton("𝐍𝐞𝐱𝐭 ⏩", callback_data=f"next_{int(index)-1}_{keyword}")]
                )
              
               
                await query.edit_message_reply_markup( 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return



        elif query.data == "pages":
            await query.answer()


        elif query.data == "start_data":
            await query.answer()
            keyboard = InlineKeyboardMarkup([                
                [InlineKeyboardButton("❣️ My Channel ❣️ ", url="https://t.me/MKSVIPLINK"),
                    InlineKeyboardButton("⭕️ My Group ⭕️", url="https://t.me/Movie_Zone_KP/3")],
                [InlineKeyboardButton("ℹ️ Features", callback_data="help_data"),
                    InlineKeyboardButton("👨🏻‍💻 DEVS ", callback_data="about_data")]                                  
            ])

            await query.message.edit_text(
                script.START_MSG.format(query.from_user.mention),
                reply_markup=keyboard,
                disable_web_page_preview=True
            )


        elif query.data == "help_data":
            await query.answer()
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("BACK", callback_data="start_data"),
                    InlineKeyboardButton("👨🏻‍💻 DEVS ", callback_data="about_data")],
                [InlineKeyboardButton("❣️ My Channel ❣️ ", url="https://t.me/MKSVIPLINK"),
                    InlineKeyboardButton("⭕️ My Group ⭕️", url="https://t.me/Movie_Zone_KP/3")]                
            ])

            await query.message.edit_text(
                script.HELP_MSG,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )


        elif query.data == "about_data":
            await query.answer()
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("BACK", callback_data="help_data"),
                    InlineKeyboardButton("START", callback_data="start_data")],
                [InlineKeyboardButton("❣️ My Channel ❣️ ", url="https://t.me/MKSVIPLINK"),
                    InlineKeyboardButton("⭕️ My Group ⭕️", url="https://t.me/Movie_Zone_KP/3")]
            ])

            await query.message.edit_text(
                script.ABOUT_MSG,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )


        elif query.data == "delallconfirm":
            await query.message.delete()
            await deleteallfilters(client, query.message)
        
        elif query.data == "delallcancel":
            await query.message.reply_to_message.delete()
            await query.message.delete()

    else:
        await query.answer("🙄 ဟင်းဟင်း သူများရိုက်ထားတာလေ \n\n😎  နှိပ်ချင်ရင် ဂရုထဲ ကွကိုရိုက်ပါ 😎!!\n\nUploaded By :Ko Paing ❣️!",show_alert=True)


def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]  




async def manual_filters(client, message, text=False):
    #settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await message.reply_text(f"Your {message.text} is Ready** 💡\nRequest by :{message.from_user.mention}\nResults : {reply_text}\n\n<i><b>🏅 {message.chat.title} 🏅</b></a>", disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await message.reply_text(
                                f"Your {message.text} is Ready** 💡\nRequest by :{message.from_user.mention}\nResults : {reply_text}\n\n<i><b>🏅 {message.chat.title} 🏅</b></a>",
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                    else:
                        if btn == "[]":
                            await message.reply_cached_media(
                                fileid,
                                caption=f"Your {message.text}  is Ready** 💡\nRequest by :{message.from_user.mention}\nResults : {reply_text}\n\n<i><b>🏅 {message.chat.title} 🏅</b></a>" or ""
                            )
                        else:
                            button = eval(btn) 
                            await message.reply_cached_media(
                                fileid,
                                caption=f"Your {message.text}  is Ready** 💡\nRequest by :{message.from_user.mention}\nResults : {reply_text}\n\n<i><b>🏅 {message.chat.title} 🏅</b></a>" or "",
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                except Exception as e:
                    print(e)
                    pass
                break 
                


