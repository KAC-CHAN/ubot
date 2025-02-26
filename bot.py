from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest

# Replace these values with your own
api_id = YOUR_API_ID
api_hash = "YOUR_API_HASH"
bot_token = "YOUR_BOT_TOKEN"
channel_id = -1001234567890  # Replace with your channel ID (must be negative)

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def approve_pending_requests():
    async with app:
        # Get all pending join requests
        async for request in app.get_chat_join_requests(channel_id):
            try:
                # Approve the request
                await app.approve_chat_join_request(channel_id, request.user.id)
                print(f"Approved user: {request.user.username or request.user.id}")

                # Send welcome message
                await app.send_message(
                    chat_id=request.user.id,
                    text="Welcome to the channel! 🎉\n\nThank you for joining our community!"
                )
            except Exception as e:
                print(f"Error processing user {request.user.id}: {e}")

@app.on_chat_join_request()
async def handle_approval(client, request: ChatJoinRequest):
    # Auto-approve new requests and send welcome message
    await request.approve()
    await client.send_message(
        chat_id=request.user_chat.id,
        text="Welcome to the channel! 🎉\n\nThank you for joining our community!"
    )

if __name__ == "__main__":
    print("Starting bot...")
    app.run(approve_pending_requests())
