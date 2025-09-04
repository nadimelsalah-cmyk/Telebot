# test.py
import asyncio
from cybernews import scrape_latest_article, send_message_to_telegram_channel
 
async def main():
    # Scrape the latest article
    latest_article_message = await scrape_latest_article()
    if latest_article_message:
        # Send the message to the Telegram channel
        await send_message_to_telegram_channel(latest_article_message)

if __name__ == "__main__":
    asyncio.run(main())
