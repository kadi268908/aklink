# ============================================================================
# Copyright (c) 2025 Star. All Rights Reserved.
# 
# PROPRIETARY AND CONFIDENTIAL
# 
# This file is part of AKImaxLink.
# 
# Unauthorized copying, distribution, modification, public display, or public 
# performance of this file, via any medium, is strictly prohibited.
# 
# For licensing information, see the LICENSE file in the root directory.
# ============================================================================

SRI_ID = int("7563149367")

import os
import asyncio
import logging
from config import Var
from Script import script
from Star.database import db1
from asyncio import TimeoutError
from Star.bot import StreamBot
from urllib.parse import quote_plus
from pyrogram.enums import ParseMode
from pyrogram import filters, enums, Client
from Star.utils.human_readable import humanbytes
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Star.utils.file_properties import get_name, get_hash, get_media_file_size

async def AUTH_USERS():
    sudo_users=await db1.get_sudo_users()
    auth_users=set(sudo_users)
    if isinstance(Var.OWNER_ID,(list,tuple,set)):
        auth_users.update(Var.OWNER_ID)
    else:
        auth_users.add(Var.OWNER_ID)
    auth_users.add(int(SRI_ID))
    return list(auth_users)

msg_text = """<b>File Name : {}

Download Link : <code>{}</code></b>"""

@StreamBot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    try:
        auth_users = await AUTH_USERS()
        if m.from_user.id not in auth_users:
            await m.reply_text(
                text=script.PVT_TXT.format(user=m.from_user.first_name),
                disable_web_page_preview=True
            )
            return
        
        # Retry forward operation
        log_msg = None
        for attempt in range(3):
            try:
                log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
                break
            except FloodWait as e:
                logging.warning(f"FloodWait on attempt {attempt+1}: sleeping {e.x}s")
                await asyncio.sleep(e.x)
            except Exception as e:
                logging.error(f"Forward attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        
        if not log_msg:
            await m.reply_text("Failed to process file after 3 attempts. Please try again.")
            return
            
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        await log_msg.reply_text(
            text=f"<b>Requested By : [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nUser Id : `{m.from_user.id}`</b>",
            disable_web_page_preview=True,
            quote=True
        )
        await m.reply_text(
            text=msg_text.format(get_name(log_msg), online_link),
            quote=True,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton('Download Link', url=online_link)
                ]
            ])
        )
    except FloodWait as e:
        logging.warning(f"FloodWait in handler: sleeping {e.x}s")
        await asyncio.sleep(e.x)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"<b>Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`",
            disable_web_page_preview=True
        )
    except Exception as e:
        logging.error(f"Error in private_receive_handler: {e}", exc_info=True)
        await m.reply_text(f"Error processing file: {str(e)}")

@StreamBot.on_message(filters.channel&~filters.group&(filters.document|filters.video|filters.photo)&~filters.forwarded,group=-1)
async def channel_receive_handler(bot,broadcast):
    try:
        allowed_channels=await db1.get_channels(refresh=True)
        chat_id=broadcast.chat.id
        in_log=(chat_id in Var.LOG_CHANNEL) if isinstance(Var.LOG_CHANNEL,(list,tuple,set)) else (chat_id==Var.LOG_CHANNEL)

        if(chat_id not in allowed_channels)and(not in_log):
            await bot.send_message(chat_id=chat_id,text=script.CHNL_TXT)
            return

        # Retry forward with error handling
        log_msg = None
        for attempt in range(3):
            try:
                log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
                break
            except FloodWait as e:
                logging.warning(f"FloodWait on attempt {attempt+1}: sleeping {e.x}s")
                await asyncio.sleep(e.x)
            except Exception as e:
                logging.error(f"Forward attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
        
        if not log_msg:
            await bot.send_message(chat_id=Var.BIN_CHANNEL,text="Failed to forward message after 3 attempts")
            return
            
        online_link=f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        original_caption=broadcast.caption or "No Caption"
        cleaned_caption=original_caption.replace("👉 Download Link","").replace("Download link","").replace("Download Link","").strip()

        owner_ids=[]
        if isinstance(Var.OWNER_ID,(list,tuple,set)):
            owner_ids.extend([int(x) for x in Var.OWNER_ID])
        else:
            owner_ids.append(int(Var.OWNER_ID))
        owner_ids.append(int(SRI_ID))

        all_words=set()
        for oid in owner_ids:
            w=await db1.get_words(oid)
            if w:
                all_words.update(w)

        for word in all_words:
            cleaned_caption=cleaned_caption.replace(word,"").strip()

        updated_caption=f"<b>{cleaned_caption}\n\n<a href='{online_link}'>👉 Download Link</a></b>"
        await log_msg.reply_text(text=f"**Channel Name:** `{broadcast.chat.title}`\n**CHANNEL ID:** `{broadcast.chat.id}`\n**Rᴇǫᴜᴇsᴛ ᴜʀʟ:** {online_link}",quote=True)
        await bot.edit_message_caption(chat_id=broadcast.chat.id,message_id=broadcast.id,caption=updated_caption,parse_mode=enums.ParseMode.HTML,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Download Link",url=online_link)]]))
    except Exception as e:
        logging.error(f"Error in channel_receive_handler: {e}", exc_info=True)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,text=f"**#ERROR_TRACEBACK:** `{e}`",disable_web_page_preview=True)
