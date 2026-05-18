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
from pyrogram.raw.all import layer
from datetime import date, datetime
from Star.server import web_server
from Star.database import db1
from pyrogram import Client, __version__

# Ensure Pyrogram clients created at import-time bind to this loop.
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from Star.bot import StreamBot
from Star.bot.clients import initialize_clients

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

async def start_services():
    app = None
    bot_started = False
    try:
        logging.info("Starting StreamBot client...")
        await asyncio.wait_for(StreamBot.start(), timeout=120)
        bot_started = True
        logging.info("StreamBot client started")

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
