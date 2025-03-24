from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
import os
import asyncio
import logging
import math

API_ID = os.getenv("API_ID", "28628607")
API_HASH = os.getenv("API_HASH", "6bd41297531e80866af2f7fcffca668d")
SESSION_STRING = os.getenv("SESSION_STRING", "BQG3smoAEvxBmumqB4J5HL5VoybZpYzBLBXOs7YCqEq1yggUY_wfJTpgaDJlnjSJg7Yzs8jKuWec0D08ys8bDZ3zLhbcNHtjAs7GxlxTay_3f2VBp-wNrQRemY3fPk9ISUxmyU7RTa7ZCxic38Yc516XqlM_mSWLFXoVPMrPDFDSe7-yBUKjflzeZUGgCx9Wj9YBDF3L6Vat-T1CSAM_dtLLZAuMiKBmTIFXFdg5CojO16UvyPtka9_pvAFLTUIZNfKP05DuNIyceuWQpOywHpVL4g9KDLvUq38VratsZHLdKrW-XviNh6f-vZxeVjSOGQ3WVuMr5cGIeyub8vqOvmynYCAf9wAAAAHOKJRtAA")
SOURCE_CHANNEL = -1002135471903  # Channel to forward FROM
TARGET_CHANNEL = -1002659050639  # Channel to forward TO
BATCH_SIZE = 2  # Messages per batch
DELAY_BETWEEN_BATCHES = 4  # Seconds between batches (4s * 30 batches = 120s)
MAX_RETRIES = 5  # Max retries for server errors


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forward.log'),
        logging.StreamHandler()
    ]
)

app = Client(
    "FixedForwardBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

def get_last_offset():
    try:
        with open('last_offset.txt', 'r') as f:
            offset = int(f.read().strip())
            logging.info(f"Resuming from offset ID: {offset}")
            return offset
    except FileNotFoundError:
        logging.info("Starting from latest messages")
        return 0  # Start from first message
    except Exception as e:
        logging.error(f"Offset error: {str(e)}")
        return 0

def save_last_offset(offset_id):
    try:
        with open('last_offset.txt', 'w') as f:
            f.write(str(offset_id))
    except Exception as e:
        logging.error(f"Offset save failed: {str(e)}")

async def forward_batch_with_retry(client, message_ids):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            await client.forward_messages(
                chat_id=TARGET_CHANNEL,
                from_chat_id=SOURCE_CHANNEL,
                message_ids=message_ids
            )
            return True
        except RPCError as e:
            if "WORKER_BUSY_TOO_LONG_RETRY" in str(e):
                wait_time = math.pow(2, retry_count)
                logging.warning(f"Server busy, retry {retry_count+1}/{MAX_RETRIES} in {wait_time}s")
                await asyncio.sleep(wait_time)
                retry_count += 1
            else:
                logging.error(f"RPC Error: {str(e)}")
                return False
        except FloodWait as e:
            logging.warning(f"FloodWait: Sleeping {e.value}s")
            await asyncio.sleep(e.value)
        except Exception as e:
            logging.error(f"Forward error: {str(e)}")
            return False
    return False

@app.on_message(filters.command(["forward"], ["/", "!"]))
async def start_forwarding(client, message):
    await message.delete()
    
    offset_id = get_last_offset()
    total_forwarded = 0
    batch_count = 0

    while True:
        try:
            # Get message batch with proper offset handling
            messages = []
            async for msg in app.get_chat_history(
                chat_id=SOURCE_CHANNEL,
                limit=BATCH_SIZE,
                offset_id=offset_id if offset_id > 0 else None
            ):
                messages.append(msg)
                if len(messages) >= BATCH_SIZE:
                    break

            if not messages:
                logging.info("No more messages to forward")
                break

            # Store IDs in reverse chronological order
            messages.reverse()
            message_ids = [msg.id for msg in messages]
            new_offset = messages[-1].id - 1  # Ensure proper pagination

            if await forward_batch_with_retry(client, message_ids):
                total_forwarded += len(messages)
                save_last_offset(new_offset)
                logging.info(f"Forwarded {len(messages)} messages (Total: {total_forwarded})")
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)
                offset_id = new_offset
            else:
                logging.error("Stopping due to persistent errors")
                break

        except Exception as e:
            logging.error(f"Critical error: {str(e)}")
            break

    logging.info(f"Finished forwarding. Total messages: {total_forwarded}")

app.run()
