#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @trojanzhex


import re
import asyncio

from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from plugins import VERIFY, LOGGER 
from bot import Bot
from config import AUTH_USERS, DOC_SEARCH, VID_SEARCH, MUSIC_SEARCH
from database.mdb import (
    savefiles,
    deletefiles,
    deletegroupcol,
    channelgroup,
    ifexists,
    deletealldetails,
    findgroupid,
    channeldetails,
    countfilters
)



@Client.on_message(filters.group & filters.command(["addd"]))
async def addchannel(client: Bot, message: Message):

    if message.from_user.id not in AUTH_USERS:
        return

    try:
        cmd, text = message.text.split(" ", 1)
    except:
        await message.reply_text(
            "<i>Enter in correct format!\n\n<code>/addd channelid</code>  or\n"
            "<code>/addd @channelusername</code></i>"
            "\n\nGet Channel id from @MT_ID_BOT",
            parse_mode=enums.ParseMode.HTML
        )
        return
    try:
        if not text.startswith("@"):
            chid = int(text)
            if not len(text) == 14:
                await message.reply_text(
                    "Enter valid channel ID",
                    parse_mode=enums.ParseMode.HTML
                )
                return
        elif text.startswith("@"):
            chid = text
            if not len(chid) > 2:
                await message.reply_text(
                    "Enter valid channel username",
                    parse_mode=enums.ParseMode.HTML
                )
                return
    except Exception:
        await message.reply_text(
            "Enter a valid ID\n"
            "ID will be in <b>-100xxxxxxxxxx</b> format\n"
            "You can also use username of channel with @ symbol",
            parse_mode=enums.ParseMode.HTML
        )
        return

    try:
        invitelink = await client.export_chat_invite_link(chid)
    except:
        await message.reply_text(
            "<i>ကျွန်ုပ်ကို သင့်ချန်နယ်တွင် စီမံခန့်ခွဲသူအဖြစ် ထည့်ပါ - 'လင့်ခ်မှတစ်ဆင့် အသုံးပြုသူများကို ဖိတ်ကြားပါ' ထပ်စမ်းကြည့်ပါ။</i>", parse_mode=enums.ParseMode.HTML
        )
        return

    try:
        user = await client.USER.get_me()
    except:
        user.first_name =  " "

    try:
        await client.USER.join_chat(invitelink)
    except UserAlreadyParticipant:
        pass
    except Exception as e:
        print(e)
        await message.reply_text(
            f"<i>User {user.first_name} သင့်ချန်နယ်တွင် မပါဝင်နိုင်ခဲ့ပါ။ အသုံးပြုသူကို ချန်နယ်တွင် ပိတ်ပင်ထားခြင်း မရှိကြောင်း သေချာပါစေ။"
            "\n\nသို့မဟုတ် အသုံးပြုသူကို သင့်ချန်နယ်သို့ ကိုယ်တိုင်ထည့်ကာ ထပ်စမ်းကြည့်ပါ။</i>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    try:
        chatdetails = await client.USER.get_chat(chid)
    except:
        await message.reply_text(
            "<i>Send a message to your channel and try again</i>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    intmsg = await message.reply_text(
        "<i>မင်းရဲ့ချန်နယ်ဖိုင်တွေကို DB မှာထည့်နေချိန်မှာ ခဏစောင့်ပါ။"
        "\n\nIt may take some time if you have more files in channel!!"
        "\nDon't give any other commands now!</i>",
        parse_mode=enums.ParseMode.HTML
    )

    channel_id = chatdetails.id
    channel_name = chatdetails.title
    group_id = message.chat.id
    group_name = message.chat.title

    already_added = await ifexists(channel_id, group_id)
    if already_added:
        await intmsg.edit_text("Channel already added to db!")
        return

    docs = []

    if DOC_SEARCH == "yes":
        try:
            async for msg in client.USER.search_messages(channel_id,filter='document'):
                try:
                    file_name = msg.document.file_name
                    file_id = msg.document.file_id
                    file_size = msg.document.file_size                   
                    link = msg.link
                    data = {
                        '_id': file_id,
                        'channel_id' : channel_id,
                        'file_name': file_name,
                        'file_size': file_size,
                        'link': link
                    }
                    docs.append(data)
                except:
                    pass
        except:
            pass

        await asyncio.sleep(5)

    if VID_SEARCH == "yes":
        try:
            async for msg in client.USER.search_messages(channel_id,filter='video'):
                try:
                    file_name = msg.video.file_name
                    file_id = msg.video.file_id   
                    file_size = msg.video.file_size              
                    link = msg.link
                    data = {
                        '_id': file_id,
                        'channel_id' : channel_id,
                        'file_name': file_name,
                        'file_size': file_size,
                        'link': link
                    }
                    docs.append(data)
                except:
                    pass
        except:
            pass

        await asyncio.sleep(5)

    if MUSIC_SEARCH == "yes":
        try:
            async for msg in client.USER.search_messages(channel_id,filter='audio'):
                try:
                    file_name = msg.audio.file_name
                    file_id = msg.audio.file_id   
                    file_size = msg.audio.file_size                 
                    link = msg.link
                    data = {
                        '_id': file_id,
                        'channel_id' : channel_id,
                        'file_name': file_name,
                        'file_size': file_size,
                        'link': link
                    }
                    docs.append(data)
                except:
                    pass
        except:
            pass

    if docs:
        await savefiles(docs, group_id)
    else:
        await intmsg.edit_text("ချန်နယ်ကို ထည့်၍မရပါ။ အချိန်တစ်ခုပြီးမှ ကြိုးစားပါ။!", parse_mode=enums.ParseMode.HTML)
        return

    await channelgroup(channel_id, channel_name, group_id, group_name)

    await intmsg.edit_text("ချန်နယ်ကို အောင်မြင်စွာ ထည့်သွင်းခဲ့သည်။!", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.group & filters.command(["dell"]))
async def deletechannelfilters(client: Bot, message: Message):

    if message.from_user.id not in AUTH_USERS:
        return

    try:
        cmd, text = message.text.split(" ", 1)
    except:
        await message.reply_text(
            "<i>Enter in correct format!\n\n<code>/del channelid</code>  or\n"
            "<code>/del @channelusername</code></i>"
            "\n\nrun /filterstats to see connected channels",
            parse_mode=enums.ParseMode.HTML
        )
        return
    try:
        if not text.startswith("@"):
            chid = int(text)
            if not len(text) == 14:
                await message.reply_text(
                    "Enter valid channel ID\n\nrun /filterstats to see connected channels",
                    parse_mode=enums.ParseMode.HTML
                )
                return
        elif text.startswith("@"):
            chid = text
            if not len(chid) > 2:
                await message.reply_text(
                    "Enter valid channel username",
                    parse_mode=enums.ParseMode.HTML
                )
                return
    except Exception:
        await message.reply_text(
            "Enter a valid ID\n"
            "run /filterstats to see connected channels\n"
            "You can also use username of channel with @ symbol",
            parse_mode=enums.ParseMode.HTML
        )
        return

    try:
        chatdetails = await client.USER.get_chat(chid)
    except:
        await message.reply_text(
            "<i>အသုံးပြုသူသည် ပေးထားသောချန်နယ်တွင် ရှိနေရပါမည်။.\n\n"
            "အသုံးပြုသူရှိနေပါက၊ သင့်ချန်နယ်သို့ စာတိုတစ်စောင်ပေးပို့ပြီး ထပ်စမ်းကြည့်ပါ။</i>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    intmsg = await message.reply_text(
        "<i>သင့်ချန်နယ်ကို ဖျက်နေစဉ် ကျေးဇူးပြု၍ စောင့်ပါ။"
        "\n\nDon't give any other commands now!</i>",
        parse_mode=enums.ParseMode.HTML
    )

    channel_id = chatdetails.id
    channel_name = chatdetails.title
    group_id = message.chat.id
    group_name = message.chat.title

    already_added = await ifexists(channel_id, group_id)
    if not already_added:
        await intmsg.edit_text("That channel is not currently added in db!", parse_mode=enums.ParseMode.HTML)
        return

    delete_files = await deletefiles(channel_id, channel_name, group_id, group_name)
    
    if delete_files:
        await intmsg.edit_text(
            "Channel deleted successfully!"
        )
    else:
        await intmsg.edit_text(
            "Couldn't delete Channel"
        )


@Client.on_message(filters.group & filters.command(["delalll"]))
async def delallconfirm(client: Bot, message: Message):
    await message.reply_text(
        "သေချာလား??ချိတ်ဆက်ထားသော ချန်နယ်များအားလုံးကို ချိတ်ဆက်မှုဖြတ်တောက်ပြီး Group အတွင်းရှိ Filter များအားလုံးကို ဖျက်ပါမည်။",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="YES",callback_data="delallconfirm")],
            [InlineKeyboardButton(text="CANCEL",callback_data="delallcancel")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


async def deleteallfilters(client: Bot, message: Message):

    if message.reply_to_message.from_user.id not in AUTH_USERS:
        return

    intmsg = await message.reply_to_message.reply_text(
        "<i>သင့်ချန်နယ်ကို ဖျက်နေစဉ် ကျေးဇူးပြု၍ စောင့်ပါl.</i>"
        "\n\nDon't give any other commands now!</i>",
        parse_mode=enums.ParseMode.HTML
    )

    group_id = message.reply_to_message.chat.id

    await deletealldetails(group_id)

    delete_all = await deletegroupcol(group_id)

    if delete_all == 0:
        await intmsg.edit_text(
            "All filters from group deleted successfully!",
            parse_mode=enums.ParseMode.HTML
           
        )
    elif delete_all == 1:
        await intmsg.edit_text(
            "Nothing to delete!!",
            parse_mode=enums.ParseMode.HTML            
        )
    elif delete_all == 2:
        await intmsg.edit_text(
            "Couldn't delete filters. Try again after sometime..",
            parse_mode=enums.ParseMode.HTML
        )  


@Client.on_message(filters.group & filters.command(["filterstatss"]))
async def stats(client: Bot, message: Message):

    if message.from_user.id not in AUTH_USERS:
        return

    group_id = message.chat.id
    group_name = message.chat.title

    stats = f"Stats for Auto Filter Bot in {group_name}\n\n<b>Connected channels ;</b>"

    chdetails = await channeldetails(group_id)
    if chdetails:
        n = 0
        for eachdetail in chdetails:
            details = f"\n{n+1} : {eachdetail}"
            stats += details
            n = n + 1
    else:
        stats += "\nNo channels connected in current group!!"
        await message.reply_text(stats)
        return

    total = await countfilters(group_id)
    if total:
        stats += f"\n\n<b>Total number of filters</b> : {total}"

    await message.reply_text(stats)


@Client.on_message(filters.channel & (filters.document | filters.video | filters.audio))
async def addnewfiles(client: Bot, message: Message):

    media = message.document or message.video or message.audio

    channel_id = message.chat.id
    file_name = media.file_name
    file_size = media.file_size
    file_id = media.file_id
    link = message.link

    docs = []
    data = {
        '_id': file_id,
        'channel_id' : channel_id,
        'file_name': file_name,
        'file_size': file_size,
        'link': link
    }
    docs.append(data)

    groupids = await findgroupid(channel_id)
    if groupids:
        for group_id in groupids:
            await savefiles(docs, group_id)
