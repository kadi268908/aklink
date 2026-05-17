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

from aiohttp import web
from .stream_routes import routes

async def web_server():
    web_app = web.Application(client_max_size=5242880)  # 5MB limit instead of 30MB
    web_app.add_routes(routes)
    return web_app
