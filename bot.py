from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import os, asyncio, logging

API_ID = os.getenv("API_ID", "28628607")
API_HASH = os.getenv("API_HASH", "6bd41297531e80866af2f7fcffca668d")
SESSION_STRING = os.getenv("SESSION_STRING", "AQG01n8ATEucxytoxzD0vcqhjBetjNdR36Xer3Eq25fv5wL1FJXKJSCDhKQAS6O_tmIy5E0Gr7jsFXQQwj1_wDANjHqrTOARzTizITTozVrEIGxERPKH7mfw2YkqXuqip2CPN8gbrf2R1NBVp91uv08RwW-l-snfU3zuBuwpTfDKpGxvC97opRoUyq6GnOdln37RCxHLwwRw1DG6qDhQKtbNBfuhFGTFqN_QYhP1VsixH6mCQeyc5bgVt39WASclFOZ9PWdQVVqMB6F77RnOPHp4oMYmlf_uRFi_cR4OBSv2JEfzzyjfaESgfbLtxDp5V0VVpJzQKEJtyrdvQWq-hCAskvthLAAAAAGVIO1jAA")
AUTH_GROUP = int(os.getenv("AUTH_GROUP", "-1002471668046"))
CHANNEL_ID = -1002347041324  # New channel ID to forward posts from

app = Client(
    "JoinAccepter",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def forward_channel_post(client, user):
    try:
        async for message in client.get_chat_history(CHANNEL_ID, limit=1):
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
            
            # Add 15-second delay after processing each user
            await asyncio.sleep(20)

    except Exception as e:
        logging.error(f"Join request error: {e}")

app.run()
