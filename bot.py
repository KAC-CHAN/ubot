from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import os, asyncio, logging

API_ID = os.getenv("API_ID", "27620678")
API_HASH = os.getenv("API_HASH", "cf05b46b4fc0f90a65731f8c96e66bfd")
SESSION_STRING = os.getenv("SESSION_STRING", "AQGldUYANCUECmeJpf8zs7LE-HZYLJkU9IyBbvNGB3J1d8oTJl7iZlVOWzV144vKdQYoBCT_KSLSxAtgoX3OfizcHzfnMk7PxW2Xs-2xK6JMTblQ3kIFs3c5i6LiNm6R1HRTnjBQNSkRPhCNUXj05GZXKYmjsf_v2jbVrL4hU4-LUTqbHZnJIzwISeKRgVEWoz1y-Auh6gGDyAqX7vVgIQF6QJFmORucSFLlEkGcdU0ILDkcTiqJeby_o_9NLtLlZMdsMUsxWYD4XvL4NEd_MQuJsnFNHhqlCPGyHQfgjiaGejbFIk56n_-VxfJtS1ZxAaIyXJ3teetG0vgFvB3EGxAsqa0KgAAAAAGbt_pPAA")
AUTH_GROUP = int(os.getenv("AUTH_GROUP", "-1002417831745"))

app = Client(
    "JoinAccepter",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def send_welcome(client, user):
    try:
        welcome_msg = f"👋 Hello {user.first_name}!\n\nWelcome to our community! Please read the rules and enjoy your stay."
        await client.send_message(
            chat_id=user.id,
            text=welcome_msg
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_welcome(client, user)
    except Exception as e:
        logging.error(f"Couldn't send welcome message to {user.id}: {e}")

@app.on_message(filters.command(["run", "approve"], [".", "/"]))
async def approve_members(client, message):
    await message.delete()
    
    try:
        # Iterate through join requests
        async for join_request in client.get_chat_join_requests(AUTH_GROUP):
            try:
                # Approve the request using user_id from ChatJoinRequest object
                await client.approve_chat_join_request(AUTH_GROUP, join_request.user.id)
                # Send welcome message to the user
                await send_welcome(client, join_request.user)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.approve_chat_join_request(AUTH_GROUP, join_request.user.id)
                await send_welcome(client, join_request.user)
                
            except Exception as e:
                logging.error(f"Error approving {join_request.user.id}: {e}")

    except Exception as e:
        logging.error(f"Join request error: {e}")

app.run()
