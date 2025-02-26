
from telethon import TelegramClient, events
import os

# Get your API credentials from my.telegram.org
api_id = int(os.environ.get('API_ID', 27620678))
api_hash = os.environ.get('API_HASH', 'cf05b46b4fc0f90a65731f8c96e66bfd')
bot_token = os.environ.get('BOT_TOKEN', '7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU')

# Create the client and connect
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def send_welcome(event):
    """Send welcome message to new channel members"""
    for user in event.users:
        try:
            # Send welcome message to the user's private messages
            await client.send_message(
                entity=user.id,
                message="🎉 Welcome to our channel!\n\n"
                        "We're excited to have you here. "
                        "Feel free to explore our content and "
                        "don't hesitate to reach out if you have any questions!"
            )
            print(f"Welcome message sent to {user.id}")
        except Exception as e:
            print(f"Couldn't send message to {user.id}: {e}")

# Register the event handler for new channel members
@client.on(events.ChatAction)
async def handler(event):
    # Check if the event is a user joining the channel
    if event.user_joined:
        await send_welcome(event)

# Start the bot
print("Bot is running...")
client.run_until_disconnected()
