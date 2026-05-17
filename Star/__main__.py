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
from Star.bot import StreamBot
from pyrogram.raw.all import layer
from datetime import date, datetime
from Star.server import web_server
from Star.database import db1
from pyrogram import Client, __version__
from Star.bot.clients import initialize_clients

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

try:
    StreamBot.start()
except Exception as e:
    logging.error(f"Failed to start StreamBot: {e}", exc_info=True)
    raise

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def start_services():
    try:
        bot_info = await StreamBot.get_me()
        StreamBot.username = bot_info.username
        await initialize_clients()
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = Var.BIND_ADRESS
        await web.TCPSite(app, bind_address, Var.PORT).start()
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        time = curr.strftime('%I:%M:%S %p')
        await StreamBot.send_message(Var.LOG_CHANNEL, f"<b>{bot_info.mention} ɪs ʀᴇsᴛᴀʀᴛᴇᴅ !!\n\n<blockquote>⏰ ᴅᴀᴛᴇ : `{date}`\n📅 ᴛɪᴍᴇ : `{time}`\n🌐 ᴛɪᴍᴇᴢᴏɴᴇ : `Aisa/Kolkata`\n\n🉐 ᴘʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ : `V{__version__}`\n📌 ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ : `V3.13.1`</blockquote></b>")  
        print(f"Vortex Stream Bot Started......⚡️⚡️⚡️")
        await idle()
    except Exception as e:
        logging.error(f"Error in start_services: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info('Received interrupt signal, shutting down gracefully...')
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
    finally:
        try:
            # Close database connection
            loop.run_until_complete(db1.close())
            logging.info("Database connection closed")
        except Exception as e:
            logging.error(f"Error closing database: {e}")
        
        # Close bot
        try:
            loop.run_until_complete(StreamBot.stop())
            logging.info("Bot stopped")
        except Exception as e:
            logging.error(f"Error stopping bot: {e}")
        
        logging.info('----------------------- Service Stopped -----------------------')
