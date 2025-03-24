from pyrogram import Client, filters
from pyrogram.errors import FloodWait, ChannelInvalid, ChannelPrivate
import os
import asyncio
import logging

API_ID = os.getenv("API_ID", "28628607")
API_HASH = os.getenv("API_HASH", "6bd41297531e80866af2f7fcffca668d")
SESSION_STRING = os.getenv("SESSION_STRING", "BQG3smoAEvxBmumqB4J5HL5VoybZpYzBLBXOs7YCqEq1yggUY_wfJTpgaDJlnjSJg7Yzs8jKuWec0D08ys8bDZ3zLhbcNHtjAs7GxlxTay_3f2VBp-wNrQRemY3fPk9ISUxmyU7RTa7ZCxic38Yc516XqlM_mSWLFXoVPMrPDFDSe7-yBUKjflzeZUGgCx9Wj9YBDF3L6Vat-T1CSAM_dtLLZAuMiKBmTIFXFdg5CojO16UvyPtka9_pvAFLTUIZNfKP05DuNIyceuWQpOywHpVL4g9KDLvUq38VratsZHLdKrW-XviNh6f-vZxeVjSOGQ3WVuMr5cGIeyub8vqOvmynYCAf9wAAAAHOKJRtAA")
SOURCE_CHANNEL = -1002135471903  # Channel to forward FROM
TARGET_CHANNEL = -1002659050639  # Channel to forward TO
BATCH_SIZE = 90
DELAY_BETWEEN_BATCHES = 120  # 2 minutes in seconds


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
    "SmartForwardBot",
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
        logging.info("No offset file found, starting from latest messages")
        return None  # Will fetch from newest messages
    except Exception as e:
        logging.error(f"Error reading offset: {str(e)}")
        return None

def save_last_offset(offset_id):
    try:
        with open('last_offset.txt', 'w') as f:
            f.write(str(offset_id))
        logging.info(f"Saved new offset: {offset_id}")
    except Exception as e:
        logging.error(f"Failed to save offset: {str(e)}")

async def verify_channel_access():
    try:
        await app.get_chat(SOURCE_CHANNEL)
        await app.get_chat(TARGET_CHANNEL)
        logging.info("Channel access verified")
        return True
    except (ChannelInvalid, ChannelPrivate) as e:
        logging.error(f"Channel access error: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected channel error: {str(e)}")
        return False

async def safe_forward(client, message_ids):
    try:
        await client.forward_messages(
            chat_id=TARGET_CHANNEL,
            from_chat_id=SOURCE_CHANNEL,
            message_ids=message_ids
        )
        return True
    except FloodWait as e:
        logging.warning(f"FloodWait: Sleeping {e.value}s")
        await asyncio.sleep(e.value)
        return await safe_forward(client, message_ids)
    except Exception as e:
        logging.error(f"Forward error: {str(e)}")
        return False

@app.on_message(filters.command(["forward"], ["/", "!"]))
async def handle_forward_command(client, message):
    await message.delete()
    
    if not await verify_channel_access():
        return

    offset_id = get_last_offset()
    total_forwarded = 0

    while True:
        try:
            # Get chat history parameters
            params = {
                'chat_id': SOURCE_CHANNEL,
                'limit': BATCH_SIZE
            }
            if offset_id is not None:
                params['offset_id'] = offset_id

            messages = []
            async for msg in app.get_chat_history(**params):
                messages.append(msg)
                if len(messages) >= BATCH_SIZE:
                    break

            if not messages:
                logging.info("No more messages to process")
                break

            # Store oldest message ID for next offset
            new_offset = messages[-1].id

            # Forward in chronological order
            messages.reverse()
            message_ids = [msg.id for msg in messages]

            if await safe_forward(client, message_ids):
                total_forwarded += len(message_ids)
                save_last_offset(new_offset)
                logging.info(f"Processed {len(message_ids)} messages. Total: {total_forwarded}")
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)
            else:
                logging.error("Stopping due to forwarding failure")
                break

        except Exception as e:
            logging.error(f"Processing error: {str(e)}")
            break

    logging.info(f"Final total messages forwarded: {total_forwarded}")

app.run()
