import asyncio
from playwright.async_api import async_playwright
from main import DatabaseManager, TelegramBot  # Your existing classes

db_manager = DatabaseManager()
telegram_bot = TelegramBot()


async def scrape_latest_article():
    """Scrape the latest news article from Cybernews using Playwright."""
    url = "https://cybernews.com/news/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set legit headers
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36"
        })

        await page.goto(url)

        # Grab the first article title and link
        first_article = await page.query_selector("div.focus-articles__article a.focus-articles__link")

        if first_article:
            title = await first_article.get_attribute("aria-label")
            link = await first_article.get_attribute("href")

            # Normalize relative links
            if link and link.startswith("/"):
                link = f"https://cybernews.com{link}"

            source = "cybernews.com"
            await browser.close()
            return title, link, source

        await browser.close()
        return None


async def main():
    db_manager.create_table()

    article_info = await scrape_latest_article()
    if article_info:
        title, link, source = article_info

        # Temporary comment for testing
        # if link and not db_manager.is_article_sent(link):
        message = f"Title: {title}\nLink: {link}\nSource: {source}"
        print("Sending message:", message)
        # await telegram_bot.send_message(message)
        # db_manager.mark_article_as_sent(link)
        # else:
        #     print("Article already sent or invalid link.")
    else:
        print("No new article found.")


if __name__ == "__main__":
    asyncio.run(main())
