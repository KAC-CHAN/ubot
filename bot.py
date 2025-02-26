from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import os, asyncio, logging

API_ID = os.getenv("API_ID", "27620678")
API_HASH = os.getenv("API_HASH", "cf05b46b4fc0f90a65731f8c96e66bfd")
SESSION_STRING = os.getenv("SESSION_STRING", "BQGWoBcAhtPT-llLAXrQY_WT3TemM5DAk6jvf3aEU7hj_p7mYEr3qver4pgxwMcxe_qnBa3AsRh1PbeD2KcSabQx_WX1KfZHizU0Dcne_c5d_d_OLg-a4z6s_FA6Mz4PgYI7qMBaJFqjBx0kDv8NGVsx5F2cyVAhOK8xZeebsaZ2kvkNi2xgF7FieN2sRbKoIj6jSSLa1LRT8erJXFcjy2GCSO6hHnWfpMr8aUTU52JlOpYMEEDa8f8o7kU0S_o0LlUg_81ccYP-AYDso7BqEnH_sSsGKrh-EdpIJPnCV6X6rqkgHcYOsfkhkQeKlTO98FL_JN-KiCiKeOH2Owv3D1GCadJGtgAAAAG_UtceAA")
AUTH_GROUP = int(os.getenv("AUTH_GROUP", "-1002411849703"))
CHANNEL_ID = -1002347041324  # New channel ID to forward posts from

app = Client(
    "JoinAccepter",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def forward_channel_post(client, user):
    try:
        # Get the latest message from the channel
        async for message in client.get_chat_history(CHANNEL_ID, limit=1):
            # Forward the message to the user
            await client.forward_messages(
                chat_id=user.id,
                from_chat_id=CHANNEL_ID,
                message_ids=message.id
            )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await forward_channel_post(client, user)
    except Exception as e:
        logging.error(f"Couldn't forward message to {user.id}: {e}")

@app.on_message(filters.command(["run", "approve"], [".", "/"]))
async def approve_members(client, message):
    await message.delete()
    
    try:
        # Iterate through join requests
        async for join_request in client.get_chat_join_requests(AUTH_GROUP):
            try:
                # Approve the request
                await client.approve_chat_join_request(AUTH_GROUP, join_request.user.id)
                # Forward channel post to the user
                await forward_channel_post(client, join_request.user)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.approve_chat_join_request(AUTH_GROUP, join_request.user.id)
                await forward_channel_post(client, join_request.user)
                
            except Exception as e:
                logging.error(f"Error approving {join_request.user.id}: {e}")

    except Exception as e:
        logging.error(f"Join request error: {e}")

app.run()
