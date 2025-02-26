from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights


# Replace these with your own values
API_ID = '27620678'
API_HASH = 'cf05b46b4fc0f90a65731f8c96e66bfd'
BOT_TOKEN = '7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU'
CHANNEL_ID = -1002366680029 

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.ChatAction)
async def handle_chat_action(event):
    if event.user_joined or event.user_added:
        user_id = event.user.id
        await client.approve_chat_join_request(CHANNEL_ID, user_id)
        await client.send_message(user_id, "Welcome to the channel! We are glad to have you here.")

print("Bot is running...")
client.run_until_disconnected()
