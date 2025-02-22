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

@app.on_message(filters.command(["run", "approve"], [".", "/"]))                     
async def approve(client, message):
    await message.delete()
    
    try:
        offset = 0
        limit = 200
        while True:
            try:
                response = await client.get_chat_join_requests(
                    chat_id=AUTH_GROUP,
                    offset=offset,
                    limit=limit
                )
            except FloodWait as e:
                await asyncio.sleep(e.value)
                continue
            except Exception as e:
                logging.error(str(e))
                break

            if not response.users:
                break

            for user in response.users:
                try:
                    # Approve join request
                    await client.approve_chat_join_request(
                        chat_id=AUTH_GROUP,
                        user_id=user.id
                    )
                    # Send welcome message
                    welcome_msg = f"🌟 Welcome {user.mention()} to the group!\n\nPlease read the rules and enjoy your stay!"
                    await client.send_message(
                        chat_id=AUTH_GROUP,
                        text=welcome_msg
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    # Retry after waiting
                    await client.approve_chat_join_request(AUTH_GROUP, user.id)
                    await client.send_message(AUTH_GROUP, welcome_msg)
                except Exception as e:
                    logging.error(f"Error processing {user.id}: {e}")

            offset += len(response.users)

    except Exception as e:
        logging.error(str(e))

app.run()
