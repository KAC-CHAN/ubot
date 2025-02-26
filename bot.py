
from telegram import Update
from telegram.ext import Application, ContextTypes, ChatJoinRequestHandler

async def approve_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Approve the join request
    await update.chat_join_request.approve()
    
    # Send welcome message to the user
    user = update.chat_join_request.from_user
    welcome_message = "🎉 Welcome to our channel! Thank you for joining us."
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=welcome_message
        )
    except Exception as e:
        print(f"Couldn't send message to {user.full_name}: {e}")

if __name__ == "__main__":
    # Initialize bot with your token
    application = Application.builder().token("7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU").build()
    
    # Add handler for join requests
    application.add_handler(ChatJoinRequestHandler(approve_join_request))
    
    # Start the bot
    print("Bot is running...")
    application.run_polling()
