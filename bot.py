from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import os, asyncio, logging

API_ID = os.getenv("API_ID", "28628607")
API_HASH = os.getenv("API_HASH", "6bd41297531e80866af2f7fcffca668d")
SESSION_STRING = os.getenv("SESSION_STRING", "BQG3smoAEvxBmumqB4J5HL5VoybZpYzBLBXOs7YCqEq1yggUY_wfJTpgaDJlnjSJg7Yzs8jKuWec0D08ys8bDZ3zLhbcNHtjAs7GxlxTay_3f2VBp-wNrQRemY3fPk9ISUxmyU7RTa7ZCxic38Yc516XqlM_mSWLFXoVPMrPDFDSe7-yBUKjflzeZUGgCx9Wj9YBDF3L6Vat-T1CSAM_dtLLZAuMiKBmTIFXFdg5CojO16UvyPtka9_pvAFLTUIZNfKP05DuNIyceuWQpOywHpVL4g9KDLvUq38VratsZHLdKrW-XviNh6f-vZxeVjSOGQ3WVuMr5cGIeyub8vqOvmynYCAf9wAAAAHOKJRtAA")
SOURCE_CHANNEL = -1002347041324  # Channel to forward FROM
TARGET_CHANNEL = -1001234567890  # Channel to forward TO

app = Client(
    "ForwardBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def forward_with_retry(client, message_ids):
    try:
        await client.forward_messages(
            chat_id=TARGET_CHANNEL,
            from_chat_id=SOURCE_CHANNEL,
            message_ids=message_ids
        )
    except FloodWait as e:
        logging.warning(f"FloodWait: Sleeping {e.value} seconds")
        await asyncio.sleep(e.value)
        await forward_with_retry(client, message_ids)

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

        # Forward in one batch (Telegram allows up to 100 messages)
        await forward_with_retry(client, messages)
        
        await client.send_message(
            chat_id=message.chat.id,
            text=f"✅ Successfully forwarded {len(messages)} messages"
        )
    except Exception as e:
        logging.error(f"Forward error: {e}")
        await client.send_message(
            chat_id=message.chat.id,
            text=f"❌ Error: {str(e)}"
        )

app.run()
