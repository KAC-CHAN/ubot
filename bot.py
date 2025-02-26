from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, ChatJoinRequestHandler

# Replace with your channel ID (e.g., -1001234567890)
CHANNEL_ID = "-1002366680029"

async def approve_join_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the command is sent in private chat
    if update.message.chat.type != "private":
        await update.message.reply_text("This command can only be used in private chat with the bot.")
        return

    # Fetch pending join requests for the channel
    try:
        join_requests = await context.bot.get_chat_join_requests(chat_id=CHANNEL_ID)
    except Exception as e:
        await update.message.reply_text(f"Failed to fetch join requests: {e}")
        return

    # Approve each pending join request
    approved_users = []
    for request in join_requests:
        try:
            await context.bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=request.user.id)
            approved_users.append(request.user.full_name)
            # Send welcome message
            await context.bot.send_message(
                chat_id=request.user.id,
                text="🎉 Welcome to our channel! Thank you for joining us."
            )
        except Exception as e:
            print(f"Failed to approve {request.user.full_name}: {e}")

    # Send confirmation to admin
    if approved_users:
        await update.message.reply_text(f"Approved {len(approved_users)} users: {', '.join(approved_users)}")
    else:
        await update.message.reply_text("No pending join requests to approve.")

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Automatically approve new join requests
    await update.chat_join_request.approve()
    await context.bot.send_message(
        chat_id=update.chat_join_request.from_user.id,
        text="🎉 Welcome to our channel! Thank you for joining us."
    )

if __name__ == "__main__":
    # Initialize bot with your token
    application = Application.builder().token("7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU").build()
    
    # Add command handler for /approve
    application.add_handler(CommandHandler("approve", approve_join_requests))
    
    # Add handler for new join requests
    application.add_handler(ChatJoinRequestHandler(handle_join_request))
    
    # Start the bot
    print("Bot is running...")
    application.run_polling()
