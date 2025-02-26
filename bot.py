from telethon import TelegramClient, functions
from telethon.tl.functions.channels import GetParticipantRequest
import asyncio

# Configuration
API_ID = '27620678'
API_HASH = 'cf05b46b4fc0f90a65731f8c96e66bfd'
BOT_TOKEN = '7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU'
CHANNEL_ID = -1002366680029 # Use channel ID or username (e.g., @channel_username)
WELCOME_MESSAGE = "Welcome to the channel! We're glad to have you here."

async def main():
    # Initialize the client
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)

    while True:
        try:
            # Fetch pending join requests
            pending_requests = await client(functions.channels.GetRequestsRequest(
                channel=CHANNEL_ID
            ))

            # Process each pending request
            for user in pending_requests.users:
                # Approve the user's join request
                try:
                    await client(functions.channels.ApproveChannelJoinerRequest(
                        channel=CHANNEL_ID,
                        user_id=user.id
                    ))
                    print(f"Approved user {user.id}")

                    # Send welcome message (if user allows bot to message them)
                    try:
                        await client.send_message(
                            user.id,
                            WELCOME_MESSAGE
                        )
                        print(f"Welcome message sent to {user.id}")
                    except Exception as e:
                        print(f"Failed to send message to {user.id}: {e}")
                except Exception as e:
                    print(f"Failed to approve user {user.id}: {e}")

            # Check every 60 seconds
            await asyncio.sleep(60)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Retry in 10 seconds in case of error
            await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
