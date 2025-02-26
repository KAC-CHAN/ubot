
import telebot

# Replace with your bot token
BOT_TOKEN = '7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU'

# Replace with your channel username or ID
CHANNEL_USERNAME = '-1002366680029'

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Function to approve join requests and send welcome message
def approve_join_requests():
    # Get the list of pending join requests
    pending_requests = bot.get_chat_join_requests(CHANNEL_USERNAME)

    for request in pending_requests:
        user_id = request.user.id
        username = request.user.username

        # Approve the join request
        bot.approve_chat_join_request(CHANNEL_USERNAME, user_id)

        # Send a welcome message to the user
        welcome_message = f"Welcome to the channel, @{username}! We're glad to have you here."
        bot.send_message(user_id, welcome_message)

        print(f"Approved join request for user: @{username}")

# Run the function to approve join requests
approve_join_requests()

# Start polling (this is necessary to keep the bot running)
bot.polling()
