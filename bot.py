

from pyrogram import Client
from pyrogram.types import ChatJoinRequest

# Replace these with your own values
API_ID = '27620678'
API_HASH = 'cf05b46b4fc0f90a65731f8c96e66bfd'
BOT_TOKEN = '7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU'
CHANNEL_ID = -1002366680029  # Replace with your channel ID (including the -100 prefix)

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def process_pending_requests():
    async with app:
        # Get all pending join requests
        async for request in app.get_chat_join_requests(CHANNEL_ID):
            try:
                # Approve existing request
                await app.approve_chat_join_request(CHANNEL_ID, request.user.id)
                
                # Send welcome message
                await app.send_message(
                    request.user.id,
                    "🎉 Welcome to our channel! Your request was approved."
                )
                print(f"Approved and welcomed user: {request.user.id}")
                
            except Exception as e:
                print(f"Error processing {request.user.id}: {e}")

# Run the script
app.run(process_pending_requests())
