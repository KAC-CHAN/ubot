from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import os, asyncio, logging

API_ID = os.getenv("API_ID", "28628607")
API_HASH = os.getenv("API_HASH", "6bd41297531e80866af2f7fcffca668d")
SESSION_STRING = os.getenv("SESSION_STRING", "BQG3smoAEvxBmumqB4J5HL5VoybZpYzBLBXOs7YCqEq1yggUY_wfJTpgaDJlnjSJg7Yzs8jKuWec0D08ys8bDZ3zLhbcNHtjAs7GxlxTay_3f2VBp-wNrQRemY3fPk9ISUxmyU7RTa7ZCxic38Yc516XqlM_mSWLFXoVPMrPDFDSe7-yBUKjflzeZUGgCx9Wj9YBDF3L6Vat-T1CSAM_dtLLZAuMiKBmTIFXFdg5CojO16UvyPtka9_pvAFLTUIZNfKP05DuNIyceuWQpOywHpVL4g9KDLvUq38VratsZHLdKrW-XviNh6f-vZxeVjSOGQ3WVuMr5cGIeyub8vqOvmynYCAf9wAAAAHOKJRtAA")
CHANNEL_ID = -1001895897717  # Replace with your channel ID

app = Client(
    "MessageDeleter",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def delete_batch(client, message_ids):
    try:
        await client.delete_messages(
            chat_id=CHANNEL_ID,
            message_ids=message_ids
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await delete_batch(client, message_ids)
    except Exception as e:
        logging.error(f"Deletion failed: {e}")

@app.on_message(filters.command(["delete"], ["/", "."]))
async def delete_messages_handler(client, message):
    await message.delete()
    try:
        count = 0
        while True:
            batch = []
            async for msg in client.get_chat_history(CHANNEL_ID, limit=100):
                batch.append(msg.id)
                if len(batch) >= 100:
                    break

            if not batch:
                break

            await delete_batch(client, batch)
            count += len(batch)
            await asyncio.sleep(2)  # Basic anti-flood delay

        await client.send_message(
            chat_id=message.chat.id,
            text=f"✅ Successfully deleted {count} messages"
        )
    except Exception as e:
        logging.error(f"/delete error: {e}")
        await client.send_message(
            chat_id=message.chat.id,
            text=f"❌ Error: {str(e)}"
        )

app.run()
