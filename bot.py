from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import os, asyncio, logging, random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_ID = os.getenv("API_ID", "27620678")
API_HASH = os.getenv("API_HASH", "cf05b46b4fc0f90a65731f8c96e66bfd")
SESSION_STRING = os.getenv("SESSION_STRING", "BQGWoBcAhtPT-llLAXrQY_WT3TemM5DAk6jvf3aEU7hj_p7mYEr3qver4pgxwMcxe_qnBa3AsRh1PbeD2KcSabQx_WX1KfZHizU0Dcne_c5d_d_OLg-a4z6s_FA6Mz4PgYI7qMBaJFqjBx0kDv8NGVsx5F2cyVAhOK8xZeebsaZ2kvkNi2xgF7FieN2sRbKoIj6jSSLa1LRT8erJXFcjy2GCSO6hHnWfpMr8aUTU52JlOpYMEEDa8f8o7kU0S_o0LlUg_81ccYP-AYDso7BqEnH_sSsGKrh-EdpIJPnCV6X6rqkgHcYOsfkhkQeKlTO98FL_JN-KiCiKeOH2Owv3D1GCadJGtgAAAAG_UtceAA")
AUTH_GROUP = int(os.getenv("AUTH_GROUP", "-1002456518234"))
CHANNEL_ID = -1002347041324  # Channel to forward from

# Flood control parameters
MAX_RETRIES = 3
BASE_DELAY = 5  # Base seconds between user processing
JITTER = 2      # Maximum random jitter seconds

app = Client(
    "JoinAccepter",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def forward_channel_post(client, user):
    """Forward latest channel post to user with flood control"""
    try:
        # Get latest message from channel
        async for message in client.get_chat_history(CHANNEL_ID, limit=1):
            await client.forward_messages(
                chat_id=user.id,
                from_chat_id=CHANNEL_ID,
                message_ids=message.id
            )
            return True
    except Exception as e:
        logger.error(f"Forward error to {user.id}: {str(e)}")
        raise

@app.on_message(filters.command(["run", "approve"], [".", "/"]))
async def approve_members(client, message):
    """Handle join requests with enhanced flood control"""
    await message.delete()
    
    try:
        async for join_request in client.get_chat_join_requests(AUTH_GROUP):
            user = join_request.user
            logger.info(f"Processing user {user.id}")

            # Approve user with retry logic
            for attempt in range(MAX_RETRIES):
                try:
                    await client.approve_chat_join_request(AUTH_GROUP, user.id)
                    logger.info(f"Approved {user.id}")
                    break
                except FloodWait as e:
                    wait = e.value + attempt*2
                    logger.warning(f"Approval flood wait {wait}s")
                    await asyncio.sleep(wait)
                except Exception as e:
                    logger.error(f"Approval error: {str(e)}")
                    if attempt == MAX_RETRIES-1:
                        continue

            # Forward message with retry logic
            for attempt in range(MAX_RETRIES):
                try:
                    await forward_channel_post(client, user)
                    logger.info(f"Forwarded to {user.id}")
                    break
                except FloodWait as e:
                    wait = e.value + attempt*2
                    logger.warning(f"Forward flood wait {wait}s")
                    await asyncio.sleep(wait)
                except Exception as e:
                    logger.error(f"Forward error: {str(e)}")
                    if attempt == MAX_RETRIES-1:
                        continue

            # Randomized delay between users
            sleep_time = BASE_DELAY + random.uniform(0, JITTER)
            logger.info(f"Sleeping {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)

    except FloodWait as e:
        logger.warning(f"Main loop flood wait {e.value}s")
        await asyncio.sleep(e.value)
    except Exception as e:
        logger.error(f"Main loop error: {str(e)}")

app.run()
