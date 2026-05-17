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

import logging
import asyncio
import aiohttp
import jinja2
import aiofiles
import urllib.parse
from config import Var
from Star.bot import StreamBot
from Star.utils.human_readable import humanbytes
from Star.utils.file_properties import get_file_ids
from Star.server.exceptions import InvalidHash

async def render_page(id, secure_hash, src=None):
    try:
        file = await asyncio.wait_for(StreamBot.get_messages(int(Var.BIN_CHANNEL), int(id)), timeout=30)
    except asyncio.TimeoutError:
        logging.error(f"Timeout getting message {id} from Telegram")
        raise
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    src = urllib.parse.urljoin(
        Var.URL,
        f"{id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}",
    )

    tag = file_data.mime_type.split("/")[0].strip()
    file_size = humanbytes(file_data.file_size)
    if tag in ["video", "audio"]:
        template_file = "Star/template/dl.html"
    else:
        template_file = "Star/template/dl.html"
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as s:
                async with s.get(src) as u:
                    file_size = humanbytes(int(u.headers.get("Content-Length", 0)))
        except asyncio.TimeoutError:
            logging.warning(f"Timeout getting file size from {src}")
        except Exception as e:
            logging.warning(f"Error getting file size: {e}")

    try:
        with open(template_file) as f:
            template = jinja2.Template(f.read())
    except FileNotFoundError:
        logging.error(f"Template not found: {template_file}")
        raise

    file_name = (file_data.file_name or "file").replace("_", " ")

    return template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        file_unique_id=file_data.unique_id,
    )
