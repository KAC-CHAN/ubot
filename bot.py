from telethon import TelegramClient, functions, types
import asyncio

# Configuration
API_ID = '27620678'
API_HASH = 'cf05b46b4fc0f90a65731f8c96e66bfd'
BOT_TOKEN = '7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU'
CHANNEL_ID = -1002366680029 # Use channel ID or username (e.g., @channel_username)
WELCOME_MESSAGE = "Welcome to the channel! We're glad to have you here."


async def main():
    # Initialize the Telegram client
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)

    while True:
        try:
            # Retrieve pending join requests
            pending_requests = await client(functions.channels.GetParticipantsRequest(
                channel=CHANNEL_ID,
                filter=types.ChannelParticipantsRequests(),
                offset=0,
                limit=100
            ))

            # Process each pending request
            for participant in pending_requests.participants:
                try:
                    # Approve the join request
                    await client(functions.channels.ApproveChannelJoinerRequest(
                        channel=CHANNEL_ID,
                        user_id=participant.user_id
                    ))
                    print(f"Approved user {participant.user_id}")

                    # Send a welcome message (if possible)
                    try:
                        await client.send_message(
                            participant.user_id,
                            WELCOME_MESSAGE
                        )
                        print(f"Welcome message sent to {participant.user_id}")
                    except Exception as e:
                        print(f"Failed to send message to {participant.user_id}: {e}")
                except Exception as e:
                    print(f"Failed to approve user {participant.user_id}: {e}")

            # Wait 60 seconds before checking again
            await asyncio.sleep(60)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Retry in case of an error
            await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
