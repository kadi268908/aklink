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

import re
import time
import math
import logging
import secrets
import mimetypes
from config import Var
from aiohttp import web
from Star import StartTime, __version__
from ..utils.custom_dl import ByteStreamer
from ..utils.time_format import get_readable_time
from aiohttp.http_exceptions import BadStatusLine
from Star.utils.render_template import render_page
from Star.bot import multi_clients, work_loads, StreamBot
from Star.server.exceptions import FIleNotFound, InvalidHash

routes = web.RouteTableDef()

ERROR_PAGE_PATH = "Star/template/error.html"
class_cache = {}

STATUS_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AKImaxLink Control Panel</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
:root {
    --bg:#05070f;
    --card:#0b1020;
    --card-soft:#0f162b;
    --accent:#3b82f6;
    --ok:#22c55e;
    --bad:#ef4444;
    --text:#e5e7eb;
    --soft:#9ca3af;
}
*{box-sizing:border-box;margin:0;padding:0}
body{
    min-height:100vh;
    background:radial-gradient(circle at top,#0a1025,#02040b 70%);
    color:var(--text);
    font-family:system-ui,Segoe UI,sans-serif;
}
.dashboard{
    max-width:1200px;
    margin:auto;
    padding:28px 20px 40px;
}
.header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:26px;
}
.title{
    font-size:1.8rem;
    letter-spacing:0.14em;
}
.status{
    display:flex;
    align-items:center;
    gap:10px;
    font-size:.8rem;
}
.dot{
    width:10px;
    height:10px;
    border-radius:50%;
    background:var(--ok);
    box-shadow:0 0 10px var(--ok);
    animation:pulse 1.5s infinite;
}
@keyframes pulse{
    0%{box-shadow:0 0 0 0 rgba(34,197,94,.7)}
    70%{box-shadow:0 0 0 12px rgba(34,197,94,0)}
    100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}
}
.stats{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
    gap:14px;
    margin-bottom:26px;
}
.stat{
    background:linear-gradient(145deg,var(--card),var(--card-soft));
    border-radius:14px;
    padding:16px;
    box-shadow:0 12px 30px rgba(0,0,0,.6);
    transition:.3s;
}
.stat:hover{transform:translateY(-4px)}
.stat span{
    display:block;
    font-size:.7rem;
    letter-spacing:.1em;
    color:var(--soft);
}
.stat strong{
    font-size:1.4rem;
}
.clients{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
    gap:16px;
}
.client{
    background:linear-gradient(145deg,var(--card),#020617);
    border-radius:16px;
    padding:14px 14px 16px;
    box-shadow:0 14px 40px rgba(0,0,0,.65);
    animation:slide .4s ease;
}
@keyframes slide{
    from{opacity:0;transform:translateY(10px)}
    to{opacity:1;transform:none}
}
.client-head{
    display:flex;
    justify-content:space-between;
    margin-bottom:8px;
}
.client-head span{
    font-size:.8rem;
    color:var(--soft);
}
.client-load{
    font-size:1.1rem;
}
.bar{
    height:8px;
    border-radius:999px;
    background:#020617;
    overflow:hidden;
}
.fill{
    height:100%;
    width:0%;
    background:linear-gradient(90deg,var(--accent),var(--ok));
    transition:width .6s cubic-bezier(.4,0,.2,1);
}
.footer{
    margin-top:28px;
    text-align:center;
    font-size:.7rem;
    color:var(--soft);
}
</style>
</head>
<body>
<div class="dashboard">
    <div class="header">
        <div class="title">AKIMAXLINK</div>
        <div class="status">
            <div class="dot" id="dot"></div>
            <span id="status">--</span>
        </div>
    </div>

    <div class="stats">
        <div class="stat"><span>UPTIME</span><strong id="uptime">--</strong></div>
        <div class="stat"><span>BOT</span><strong id="bot">--</strong></div>
        <div class="stat"><span>CLIENTS</span><strong id="bots">--</strong></div>
        <div class="stat"><span>VERSION</span><strong id="version">--</strong></div>
    </div>

    <div class="clients" id="clients"></div>

    <div class="footer">Auto refresh every 3 seconds • /status-json</div>
</div>

<script>
async function refresh(){
    try{
        const r=await fetch("/status-json");
        const d=await r.json();

        document.getElementById("status").textContent=d.server_status.toUpperCase();
        document.getElementById("uptime").textContent=d.uptime;
        document.getElementById("bot").textContent=d.telegram_bot;
        document.getElementById("bots").textContent=d.connected_bots;
        document.getElementById("version").textContent=d.version;

        const box=document.getElementById("clients");
        box.innerHTML="";

        const loads=d.loads||{};
        const max=Math.max(...Object.values(loads),1);

        Object.entries(loads).forEach(([k,v],i)=>{
            const el=document.createElement("div");
            el.className="client";
            el.innerHTML=
                "<div class='client-head'><span>Client "+(i+1)+"</span><span class='client-load'>"+v+"</span></div>"+
                "<div class='bar'><div class='fill'></div></div>";
            box.appendChild(el);
            setTimeout(()=>el.querySelector(".fill").style.width=((v/max)*100).toFixed(0)+"%",60);
        });
    }catch(e){}
}
refresh();
setInterval(refresh,3000);
</script>
</body>
</html>
"""

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.FileResponse("Star/template/home.html")

@routes.get("/status-json", allow_head=True)
async def status_json(_):
    try:
        bot_username = getattr(StreamBot, 'username', 'Unknown')
        if not bot_username or bot_username == 'Unknown':
            bot_username = "bot"
    except Exception as e:
        logging.warning(f"Error getting bot username: {e}")
        bot_username = "bot"
    
    return web.json_response(
        {
            "server_status": "running",
            "uptime": get_readable_time(time.time() - StartTime),
            "telegram_bot": "@" + bot_username,
            "connected_bots": len(multi_clients),
            "loads": dict(
                ("bot" + str(i + 1), l)
                for i, (_, l) in enumerate(
                    sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
                )
            ),
            "version": __version__,
        }
    )

@routes.get("/status", allow_head=True)
async def root_route_handler(_):
    return web.Response(content_type="text/html", text=STATUS_PAGE_HTML)

@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def watch_handler(request: web.Request):
    try:
        logging.info(f"/watch request from {request.remote} path={request.match_info['path']}")

        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            regex_match = re.search(r"(\d+)(?:\/\S+)?", path)
            if not regex_match:
                logging.error(f"Invalid path format: {path}")
                return web.FileResponse(ERROR_PAGE_PATH)
            id = int(regex_match.group(1))
            secure_hash = request.rel_url.query.get("hash")

        logging.info(f"Rendering page id={id} hash={secure_hash}")
        return web.Response(text=await render_page(id, secure_hash), content_type="text/html")

    except Exception as e:
        logging.exception(f"/watch failed from {request.remote}: {e}")
        return web.FileResponse(ERROR_PAGE_PATH)

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        logging.info(f"/stream request from {request.remote} path={request.match_info['path']}")

        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            regex_match = re.search(r"(\d+)(?:\/\S+)?", path)
            if not regex_match:
                logging.error(f"Invalid path format: {path}")
                return web.FileResponse(ERROR_PAGE_PATH)
            id = int(regex_match.group(1))
            secure_hash = request.rel_url.query.get("hash")

        logging.info(f"Streaming start id={id} hash={secure_hash}")
        return await media_streamer(request, id, secure_hash)

    except Exception as e:
        logging.exception(f"/stream failed before media_streamer: {e}")
        return web.FileResponse(ERROR_PAGE_PATH)

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    try:
        logging.info(f"media_streamer init id={id} client={request.remote}")

        range_header = request.headers.get("Range", 0)
        index = min(work_loads, key=work_loads.get)
        faster_client = multi_clients[index]

        logging.info(f"Client selected index={index} load={work_loads[index]}")

        if faster_client in class_cache:
            tg_connect = class_cache[faster_client]
            logging.info("Using cached ByteStreamer")
        else:
            tg_connect = ByteStreamer(faster_client)
            class_cache[faster_client] = tg_connect
            logging.info("Created new ByteStreamer")

        file_id = await tg_connect.get_file_properties(id)
        logging.info(f"File loaded size={file_id.file_size}")

        if file_id.unique_id[:6] != secure_hash:
            logging.error("Hash mismatch")
            raise InvalidHash

        file_size = file_id.file_size
        
        # Validate file size
        if not file_size or file_size <= 0:
            logging.error(f"Invalid file size: {file_size}")
            return web.Response(status=400, text="Invalid file size")

        if range_header:
            try:
                range_parts = range_header.replace("bytes=", "").split("-")
                if len(range_parts) != 2:
                    raise ValueError("Invalid range format")
                from_bytes = int(range_parts[0]) if range_parts[0] else 0
                until_bytes = int(range_parts[1]) if range_parts[1] else file_size - 1
            except (ValueError, IndexError) as e:
                logging.error(f"Invalid range header: {range_header}: {e}")
                from_bytes = 0
                until_bytes = file_size - 1
        else:
            from_bytes = 0
            until_bytes = file_size - 1
            if request.http_range is not None:
                from_bytes = request.http_range.start or 0
                until_bytes = (request.http_range.stop or file_size) - 1

        logging.info(f"Range bytes={from_bytes}-{until_bytes}")

        chunk_size = 1024 * 1024
        until_bytes = min(until_bytes, file_size - 1)

        offset = from_bytes - (from_bytes % chunk_size)
        first_part_cut = from_bytes - offset
        last_part_cut = until_bytes % chunk_size + 1

        req_length = until_bytes - from_bytes + 1
        part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

        logging.info(f"Streaming offset={offset} parts={part_count}")

        body = tg_connect.yield_file(file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size)

        mime_type = file_id.mime_type or "application/octet-stream"
        file_name = file_id.file_name or f"{secrets.token_hex(2)}.bin"

        return web.Response(
            status=206 if range_header else 200,
            body=body,
            headers={
                "Content-Type": mime_type,
                "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
                "Content-Length": str(req_length),
                "Content-Disposition": f'attachment; filename="{file_name}"',
                "Accept-Ranges": "bytes",
            },
        )

    except Exception as e:
        logging.exception(f"media_streamer crashed id={id}: {e}")
        return web.FileResponse(ERROR_PAGE_PATH)
