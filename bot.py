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
    "FinalForwardBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

def get_last_offset():
    try:
        with open('last_offset.txt', 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return None
    except Exception as e:
        logging.error(f"Offset error: {str(e)}")
        return None

def save_last_offset(offset_id):
    try:
        with open('last_offset.txt', 'w') as f:
            f.write(str(offset_id))
    except Exception as e:
        logging.error(f"Offset save failed: {str(e)}")

async def get_initial_offset():
    try:
        async for msg in app.get_chat_history(SOURCE_CHANNEL, limit=1):
            return msg.id + 1  # Start from latest message
    except Exception as e:
        logging.error(f"Initial offset error: {str(e)}")
        return None

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
                await asyncio.sleep(wait_time)
                retry_count += 1
            else:
                return False
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            return False
    return False

@app.on_message(filters.command(["forward"], ["/", "!"]))
async def start_forwarding(client, message):
    await message.delete()
    
    offset_id = get_last_offset() or await get_initial_offset()
    if not offset_id:
        logging.error("Failed to initialize offset")
        return

    total_forwarded = 0

    while True:
        try:
            # Fetch messages older than current offset
            messages = []
            async for msg in app.get_chat_history(
                chat_id=SOURCE_CHANNEL,
                limit=BATCH_SIZE,
                offset_id=offset_id
            ):
                messages.append(msg)
                if len(messages) >= BATCH_SIZE:
                    break

            if not messages:
                logging.info("Finished forwarding all messages")
                break

            # Process messages in chronological order
            messages.reverse()
            message_ids = [msg.id for msg in messages]
            new_offset = messages[0].id  # Oldest message in batch

            if await forward_batch_with_retry(client, message_ids):
                total_forwarded += len(messages)
                save_last_offset(new_offset)
                logging.info(f"Forwarded {len(messages)} messages | Total: {total_forwarded}")
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)
                offset_id = new_offset
            else:
                logging.warning("Saving progress and exiting due to errors")
                save_last_offset(offset_id)
                break

        except Exception as e:
            logging.error(f"Critical error: {str(e)}")
            save_last_offset(offset_id)
            break

    logging.info(f"Total messages forwarded: {total_forwarded}")

app.run()
