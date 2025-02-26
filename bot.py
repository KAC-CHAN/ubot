from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import os, asyncio, logging, random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_ID = os.getenv("API_ID", "")
API_HASH = os.getenv("API_HASH", "")

from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, Message

# Replace these with your own values
API_ID = '27620678'
API_HASH = 'cf05b46b4fc0f90a65731f8c96e66bfd'
BOT_TOKEN = '7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU'
CHANNEL_ID = -1002366680029  # Replace with your channel ID (including the -100 prefix)

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to approve join requests and send a welcome message
@app.on_chat_join_request()
async def approve_join_request(client: Client, chat_join_request: ChatJoinRequest):
    # Approve the join request
    await client.approve_chat_join_request(chat_join_request.chat.id, chat_join_request.from_user.id)
    
    # Send a welcome message to the user
    welcome_message = f"Welcome {chat_join_request.from_user.mention} to the channel!"
    await client.send_message(chat_join_request.from_user.id, welcome_message)

# Start the bot
app.run()
