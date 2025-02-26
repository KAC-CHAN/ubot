import requests
import time

# Configuration
BOT_TOKEN = "7715898810:AAFeqS1E2esqeM93R3esP8hPUsXRGxyttQU"
CHANNEL_ID = "-1002366680029"  # Must be string with -100 prefix
WELCOME_MESSAGE = "Welcome to our channel! 🎉"

def get_pending_requests():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatJoinRequests"
    params = {
        "chat_id": CHANNEL_ID,
        "limit": 200
    }
    response = requests.get(url, params=params).json()
    return response.get('result', {}).get('join_requests', [])

def approve_user(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/approveChatJoinRequest"
    params = {
        "chat_id": CHANNEL_ID,
        "user_id": user_id
    }
    return requests.post(url, params=params).json()

def send_welcome(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": user_id,
        "text": WELCOME_MESSAGE
    }
    return requests.post(url, params=params).json()

def process_requests():
    pending_requests = get_pending_requests()
    
    for request in pending_requests:
        user_id = request['user_chat']['id']
        print(f"Processing user: {user_id}")
        
        # Approve request
        approval_result = approve_user(user_id)
        if not approval_result.get('ok'):
            print(f"Failed to approve {user_id}: {approval_result}")
            continue
        
        # Send welcome message
        message_result = send_welcome(user_id)
        if not message_result.get('ok'):
            print(f"Failed to message {user_id}: {message_result}")
        
        # Add delay to avoid rate limits
        time.sleep(1)

if __name__ == "__main__":
    print("Starting approval process...")
    process_requests()
    print("Process completed!")
