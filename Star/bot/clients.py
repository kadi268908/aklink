import asyncio
import logging
from config import Var
from pyrogram import Client
from . import multi_clients, work_loads, StreamBot

async def initialize_clients():
    if Var.MULTI_CLIENT:
        all_tokens = {
            1: Var.MULTI_TOKEN1,
            2: Var.MULTI_TOKEN2,
            3: Var.MULTI_TOKEN3,
            4: Var.MULTI_TOKEN4,
            5: Var.MULTI_TOKEN5,
            6: Var.MULTI_TOKEN6,
            7: Var.MULTI_TOKEN7,
            8: Var.MULTI_TOKEN8,
            9: Var.MULTI_TOKEN9,
            10: Var.MULTI_TOKEN10,
            11: Var.MULTI_TOKEN11,
            12: Var.MULTI_TOKEN12,
        }
        if not any(all_tokens.values()):
            multi_clients[0] = StreamBot
            work_loads[0] = 0
            print("No additional clients found, using default client")
            return
    else:
        multi_clients[0] = StreamBot
        work_loads[0] = 0
        print("Multi-client is off, continuing with default client")
        return

    valid_tokens = {i: t for i, t in all_tokens.items() if t}

    async def start_client(client_id, token, max_retries=3):
        for attempt in range(1, max_retries + 1):
            try:
                print(f"Starting - Client {client_id} (Attempt {attempt}/{max_retries})")
                if client_id == len(valid_tokens):
                    await asyncio.sleep(2)
                    print("This will take some time, please wait...")
                client = await Client(
                    name=str(client_id),
                    api_id=Var.API_ID,
                    api_hash=Var.API_HASH,
                    bot_token=token,
                    sleep_threshold=Var.SLEEP_THRESHOLD,
                    no_updates=True,
                    in_memory=True
                ).start()
                work_loads[client_id] = 0
                print(f"✓ Client {client_id} started successfully")
                return client_id, client
            except Exception as e:
                logging.error(f"Client {client_id} startup attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    wait_time = 5 * attempt  # Exponential backoff: 5s, 10s, 15s
                    logging.info(f"Retrying Client {client_id} in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logging.error(f"Client {client_id} failed after {max_retries} attempts")
                    return None

    if not valid_tokens:
        multi_clients[0] = StreamBot
        work_loads[0] = 0
        print("No valid multi-client tokens, using default client")
        return

    clients = await asyncio.gather(*[start_client(i, token, max_retries=3) for i, token in valid_tokens.items()])
    clients = [c for c in clients if c]
    if clients:
        multi_clients.update(dict(clients))
    if len(multi_clients) != 1:
        Var.MULTI_CLIENT = True
        print(f"Multi-Client Mode Enabled with {len(multi_clients)} active clients")
    else:
        print("No additional clients were initialized, using default client")
