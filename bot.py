from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import os, asyncio, logging

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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None

def save_last_offset(offset_id):
    with open('last_offset.txt', 'w') as f:
        f.write(str(offset_id))

async def safe_forward(client, message_ids):
    try:
        await client.forward_messages(
            chat_id=TARGET_CHANNEL,
            from_chat_id=SOURCE_CHANNEL,
            message_ids=message_ids
        )
        return True
    except FloodWait as e:
        logging.warning(f"FloodWait detected: Sleeping {e.value} seconds")
        await asyncio.sleep(e.value)
        return await safe_forward(client, message_ids)
    except Exception as e:
        logging.error(f"Forwarding error: {str(e)}")
        return False

@app.on_message(filters.command(["forward"], ["/", "!"]))
async def handle_forward_command(client, message):
    await message.delete()
    offset_id = get_last_offset()
    
    while True:
        try:
            # Fetch message batch
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
                logging.info("All messages processed successfully")
                break

            # Prepare messages in chronological order
            messages.reverse()
            message_ids = [msg.id for msg in messages]

            # Forward with retry logic
            if await safe_forward(client, message_ids):
                # Update offset to oldest message in current batch
                offset_id = messages[-1].id
                save_last_offset(offset_id)
                
                # Wait before next batch
                logging.info(f"Processed {len(messages)} messages. Waiting {DELAY_BETWEEN_BATCHES} seconds...")
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)
            else:
                logging.error("Stopping due to forwarding errors")
                break

        except FloodWait as e:
            logging.warning(f"FloodWait during processing: Sleeping {e.value} seconds")
            await asyncio.sleep(e.value)
        except Exception as e:
            logging.error(f"Critical error: {str(e)}")
            break

app.run()
