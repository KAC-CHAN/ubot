from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

# Replace these with your own values
API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
BOT_TOKEN = 'your_bot_token'
CHANNEL_ID = 'your_channel_id'  # Replace with your channel's ID

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.ChatAction)
async def handle_chat_action(event):
    if event.user_joined or event.user_added:
        user_id = event.user.id
        await client.approve_chat_join_request(CHANNEL_ID, user_id)
        await client.send_message(user_id, "Welcome to the channel! We are glad to have you here.")

print("Bot is running...")
client.run_until_disconnected()
