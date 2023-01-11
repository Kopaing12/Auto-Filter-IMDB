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


@Client.on_message(filters.command(["add1"]) & filters.group, group=1)
async def connect(bot: Bot, update):
    """
    A Funtion To Handle Incoming /add Command TO COnnect A Chat With Group
    """
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None
    target_chat = update.text.split(None, 1)
    global VERIFY
    
    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.get_chat_members(chat_id=chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)):
        return
    
    try:
        if target_chat[1].startswith("@"):
            if len(target_chat[1]) < 5:
                await update.reply_text("Invalid Username...!!!")
                return
            target = target_chat[1]
            
        elif not target_chat[1].startswith("@"):
            if len(target_chat[1]) < 14:
                await update.reply_text("Invalid Chat Id...\nChat ID Should Be Something Like This: <code>-100xxxxxxxxxx</code>")
                return
            target = int(target_chat[1])
                
    except Exception:
        await update.reply_text("Invalid Input...\nYou Should Specify Valid <code>chat_id(-100xxxxxxxxxx)</code> or <code>@username</code>")
        return
    
    # Exports invite link from target channel for user to join
    try:
        join_link = await bot.export_chat_invite_link(target)
        join_link = join_link.replace('+', 'joinchat/')
    except Exception as e:
        logger.exception(e, exc_info=True)
        await update.reply_text(f"Make Sure Im Admin At <code>{target}</code> And Have Permission For <i>Inviting Users via Link</i> And Try Again.....!!!\n\n<i><b>Error Logged:</b></i> <code>{e}</code>", parse_mode='html')
        return
    
    userbot_info = await bot.USER.get_me()
    
    # Joins to targeted chat using above exported invite link
    # If aldready joined, code just pass on to next code
    try:
        await bot.USER.join_chat(join_link)
    except UserAlreadyParticipant:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)
        await update.reply_text(f"{userbot_info.mention} Couldnt Join The Channel <code>{target}</code> Make Sure Userbot Is Not Banned There Or Add It Manually And Try Again....!!\n\n<i><b>Error Logged:</b></i> <code>{e}</code>", parse_mode='html')
        return
    
    try:
        c_chat = await bot.get_chat(target)
        channel_id = c_chat.id
        channel_name = c_chat.title
        
    except Exception as e:
        await update.reply_text("Encountered Some Issue..Please Check Logs..!!")
        raise e
        
        
    in_db = await db.in_db(chat_id, channel_id)
    
    if in_db:
        await update.reply_text("Channel Aldready In Db...!!!")
        return
    
    wait_msg = await update.reply_text("Please Wait Till I Add All Your Files From Channel To Db\n\n<i>This May Take 10 or 15 Mins Depending On Your No. Of Files In Channel.....</i>\n\nUntil Then Please Dont Sent Any Other Command Or This Operation May Be Intrupted....")
    
    try:
        mf = enums.MessagesFilter
        type_list = [mf.VIDEO, mf.DOCUMENT, mf.AUDIO]
        data = []
        skipCT = 0
        
        for typ in type_list:

            async for msgs in bot.USER.search_messages(channel_id, filter=typ): #Thanks To @PrgOfficial For Suggesting
                
                # Using 'if elif' instead of 'or' to determine 'file_type'
                # Better Way? Make A PR
                try:
                    try:
                        file_id = await bot.get_messages(channel_id, message_ids=msgs.id)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        file_id = await bot.get_messages(channel_id, message_ids=msgs.id)
                    except Exception as e:
                        print(e)
                        continue

                    if msgs.video:
                        file_id = file_id.video.file_id
                        file_name = msgs.video.file_name[0:-4]
                        file_caption  = msgs.caption if msgs.caption else ""
                        file_size = msgs.video.file_size
                        file_type = "video"
                    
                    elif msgs.audio:
                        file_id = file_id.audio.file_id
                        file_name = msgs.audio.file_name[0:-4]
                        file_caption  = msgs.caption if msgs.caption else ""
                        file_size = msgs.audio.file_size
                        file_type = "audio"
                    
                    elif msgs.document:
                        file_id = file_id.document.file_id
                        file_name = msgs.document.file_name[0:-4]
                        file_caption  = msgs.caption if msgs.caption else ""
                        file_size = msgs.document.file_size
                        file_type = "document"
                    
                    else:
                        return
                    
                    for i in ["_", "|", "-", "."]: # Work Around
                        try:
                            file_name = file_name.replace(i, " ")
                        except Exception:
                            pass
                    
                    file_link = msgs.link
                    group_id = chat_id
                    unique_id = ''.join(
                        random.choice(
                            string.ascii_lowercase + 
                            string.ascii_uppercase + 
                            string.digits
                        ) for _ in range(15)
                    )
                    
                    dicted = dict(
                        file_id=file_id, # Done
                        unique_id=unique_id,
                        file_name=file_name,
                        file_caption=file_caption,
                        file_size=file_size,
                        file_type=file_type,
                        file_link=file_link,
                        chat_id=channel_id,
                        group_id=group_id,
                    )
                    
                    data.append(dicted)
                except Exception as e:
                    if 'NoneType' in str(e): # For Some Unknown Reason Some File Names are NoneType
                        skipCT +=1
                        continue
                    print(e)

        print(f"{skipCT} Files Been Skipped Due To File Name Been None..... #BlameTG")
    except Exception as e:
        await wait_msg.edit_text("Couldnt Fetch Files From Channel... Please look Into Logs For More Details")
        raise e
    
    await db.add_filters(data)
    await db.add_chat(chat_id, channel_id, channel_name)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text(f"Channel Was Sucessfully Added With <code>{len(data)}</code> Files..")

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
