from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import os, asyncio, logging

API_ID = os.getenv("API_ID", "28628607")
API_HASH = os.getenv("API_HASH", "6bd41297531e80866af2f7fcffca668d")
SESSION_STRING = os.getenv("SESSION_STRING", "BQG3smoAEvxBmumqB4J5HL5VoybZpYzBLBXOs7YCqEq1yggUY_wfJTpgaDJlnjSJg7Yzs8jKuWec0D08ys8bDZ3zLhbcNHtjAs7GxlxTay_3f2VBp-wNrQRemY3fPk9ISUxmyU7RTa7ZCxic38Yc516XqlM_mSWLFXoVPMrPDFDSe7-yBUKjflzeZUGgCx9Wj9YBDF3L6Vat-T1CSAM_dtLLZAuMiKBmTIFXFdg5CojO16UvyPtka9_pvAFLTUIZNfKP05DuNIyceuWQpOywHpVL4g9KDLvUq38VratsZHLdKrW-XviNh6f-vZxeVjSOGQ3WVuMr5cGIeyub8vqOvmynYCAf9wAAAAHOKJRtAA")
SOURCE_CHANNEL = -1002135471903  # Channel to forward FROM
TARGET_CHANNEL = -1002659050639  # Channel to forward TO


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Client(
    "ForwardBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def forward_with_retry(client, message_ids, retry_count=0):
    max_retries = 5
    try:
        await client.forward_messages(
            chat_id=TARGET_CHANNEL,
            from_chat_id=SOURCE_CHANNEL,
            message_ids=message_ids
        )
        return True
    except FloodWait as e:
        wait_time = e.value
        logging.warning(f"Rate limited. Waiting {wait_time} seconds...")
        await asyncio.sleep(wait_time)
        if retry_count < max_retries:
            return await forward_with_retry(client, message_ids, retry_count + 1)
        return False
    except Exception as e:
        logging.error(f"Forward error: {str(e)}")
        return False

@app.on_message(filters.command(["forward"], ["/", "!"]))
async def forward_command(client, message):
    await message.delete()
    try:
        # Get last 100 messages (newest first)
        messages = []
        async for msg in client.get_chat_history(SOURCE_CHANNEL, limit=100):
            messages.append(msg.id)
        
        # Reverse to maintain chronological order
        messages.reverse()

        # Split into smaller batches (10 messages per batch)
        batch_size = 10
        total_messages = len(messages)
        success_count = 0

        for i in range(0, total_messages, batch_size):
            batch = messages[i:i + batch_size]
            if await forward_with_retry(client, batch):
                success_count += len(batch)
                logging.info(f"Forwarded {len(batch)} messages ({success_count}/{total_messages})")
                await asyncio.sleep(5)  # Add delay between batches

        await client.send_message(
            chat_id=message.chat.id,
            text=f"✅ Successfully forwarded {success_count}/{total_messages} messages"
        )
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        await client.send_message(
            chat_id=message.chat.id,
            text=f"❌ Critical error: {str(e)}"
        )

app.run()
