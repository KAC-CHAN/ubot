from pyrogram import Client, filters
import os

# Set environment variables or replace with actual values
API_ID = '27620678'
API_HASH = 'cf05b46b4fc0f90a65731f8c96e66bfd'
BOT_TOKEN = '7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU'
CHANNEL_ID = -1002366680029 # Use channel ID or username (e.g., @channel_username)

app = Client("welcome_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.chat(CHANNEL_ID) & filters.new_chat_members)
async def send_welcome_message(_, message):
    for user in message.new_chat_members:
        try:
            await app.send_message(user.id, "Welcome to our channel! Thank you for joining.")
        except Exception as e:
            print(f"Error sending message to {user.id}: {e}")

if __name__ == "__main__":
    app.run()
