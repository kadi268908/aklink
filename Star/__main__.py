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

import os
import sys
import time
import pytz
import glob
import asyncio
import logging
import importlib
from config import Var
from aiohttp import web
from pathlib import Path
from pytz import timezone
from pyrogram import idle
from pyrogram import filters
from pyrogram.raw.all import layer
from pyrogram.handlers import MessageHandler
from pyrogram.errors import FloodWait
from datetime import date, datetime
from Star.server import web_server
from Star.database import db1
from pyrogram import Client, __version__
from Script import script

# Configure logging FIRST, before any other operations
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

# Ensure Pyrogram clients created at import-time bind to this loop.
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from Star.bot import StreamBot
from Star.bot.clients import initialize_clients

# Import plugins with explicit error handling to ensure handlers are registered
try:
    from Star.bot.plugins import commands as _commands_plugin
    logging.info("✓ Commands plugin loaded successfully")
except Exception as e:
    logging.error(f"Failed to load commands plugin: {e}", exc_info=True)

try:
    from Star.bot.plugins import stream as _stream_plugin
    logging.info("✓ Stream plugin loaded successfully")
except Exception as e:
    logging.error(f"Failed to load stream plugin: {e}", exc_info=True)


def register_fallback_handlers():
    """Register critical handlers explicitly if decorator/plugin loading fails."""

    async def fallback_private_handler(client, message):
        text = message.text or ""
        if text.startswith("/start"):
            await message.reply_text(
                text=script.START_TXT.format(user=message.from_user.first_name),
                disable_web_page_preview=True,
            )
            return

        if text.startswith("/"):
            await message.reply_text(
                "<b>Bot is online, but command handlers are not active yet.</b>",
                disable_web_page_preview=True,
            )
            return

        await message.reply_text(
            "<b>Bot is online. Send me a file or use /start.</b>",
            disable_web_page_preview=True,
        )

    StreamBot.add_handler(
        MessageHandler(
            fallback_private_handler,
            filters.private & filters.text,
        ),
        group=-100,
    )
    StreamBot.add_handler(
        MessageHandler(
            _stream_plugin.private_receive_handler,
            filters.private & (filters.document | filters.video | filters.audio | filters.photo),
        ),
        group=4,
    )
    StreamBot.add_handler(
        MessageHandler(
            _stream_plugin.channel_receive_handler,
            filters.channel
            & ~filters.group
            & (filters.document | filters.video | filters.photo)
            & ~filters.forwarded,
        ),
        group=-1,
    )

async def start_services():
    app = None
    bot_started = False
    try:
        logging.info("Starting StreamBot client...")
        while True:
            try:
                await StreamBot.start()
                break
            except FloodWait as flood_error:
                wait_seconds = int(getattr(flood_error, "value", 0) or getattr(flood_error, "x", 0) or 0)
                wait_seconds = max(wait_seconds, 1)
                logging.warning(f"Telegram asked to wait {wait_seconds}s before bot authorization; sleeping then retrying")
                await asyncio.sleep(wait_seconds + 5)
        bot_started = True
        logging.info("StreamBot client started")
        
        # Count handlers - try multiple methods to ensure accuracy
        try:
            handler_count = sum(len(v) for v in StreamBot.dispatcher.groups.values())
        except (AttributeError, TypeError):
            # Fallback: check if handlers were registered at all
            handler_count = 0
        
        logging.info(f"Registered handlers: {handler_count}")
        logging.info(f"Dispatcher groups keys: {list(StreamBot.dispatcher.groups.keys()) if hasattr(StreamBot.dispatcher, 'groups') and StreamBot.dispatcher.groups else 'empty'}")
        
        if handler_count == 0:
            logging.warning("No handlers registered from plugins; enabling fallback manual handlers")
            register_fallback_handlers()
            try:
                handler_count = sum(len(v) for v in StreamBot.dispatcher.groups.values())
            except (AttributeError, TypeError):
                handler_count = 0
            logging.info(f"Registered handlers after fallback: {handler_count}")
            logging.info(f"Dispatcher groups after fallback: {list(StreamBot.dispatcher.groups.keys()) if hasattr(StreamBot.dispatcher, 'groups') and StreamBot.dispatcher.groups else 'empty'}")

        logging.info("Fetching bot profile...")
        bot_info = await StreamBot.get_me()
        StreamBot.username = bot_info.username

        logging.info("Initializing extra clients...")
        await initialize_clients()

        logging.info("Starting web server...")
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = Var.BIND_ADRESS
        await web.TCPSite(app, bind_address, Var.PORT).start()
        logging.info(f"Web server started on {bind_address}:{Var.PORT}")
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        time = curr.strftime('%I:%M:%S %p')
        try:
            await StreamBot.send_message(Var.LOG_CHANNEL, f"<b>{bot_info.mention} ɪs ʀᴇsᴛᴀʀᴛᴇᴅ !!\n\n<blockquote>⏰ ᴅᴀᴛᴇ : `{date}`\n📅 ᴛɪᴍᴇ : `{time}`\n🌐 ᴛɪᴍᴇᴢᴏɴᴇ : `Aisa/Kolkata`\n\n🉐 ᴘʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ : `V{__version__}`\n📌 ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ : `V3.13.1`</blockquote></b>")
        except Exception as notify_error:
            logging.warning(f"Startup notification failed: {notify_error}")
        print(f"Vortex Stream Bot Started......⚡️⚡️⚡️")
        await idle()
    except asyncio.TimeoutError:
        logging.error("Timed out while starting StreamBot. Check Telegram connectivity and BOT_TOKEN.", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Error in start_services: {e}", exc_info=True)
        raise
    finally:
        try:
            await db1.close()
            logging.info("Database connection closed")
        except Exception as e:
            logging.error(f"Error closing database: {e}")

        if app is not None:
            try:
                await app.cleanup()
                logging.info("Web server stopped")
            except Exception as e:
                logging.error(f"Error stopping web server: {e}")

        if bot_started:
            try:
                await StreamBot.stop()
                logging.info("Bot stopped")
            except Exception as e:
                logging.error(f"Error stopping bot: {e}")

if __name__ == '__main__':
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info('Received interrupt signal, shutting down gracefully...')
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
    finally:
        loop.close()
        logging.info('----------------------- Service Stopped -----------------------')
