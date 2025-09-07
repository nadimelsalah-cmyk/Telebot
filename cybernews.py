import asyncio
from playwright.async_api import async_playwright
from main import DatabaseManager, TelegramBot  # Reuse your shared classes

db_manager = DatabaseManager()
telegram_bot = TelegramBot()


async def scrape_latest_article():
    """Scrape the latest news article from Hackread using Playwright."""
    url = "https://hackread.com/category/security/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # GitHub Actions safe
        page = await browser.new_page()
        await page.goto(url, timeout=60000)  # generous timeout

        # Grab the first article
        first_article = await page.query_selector("h2.cs-entry__title a")

        title, link, source = None, None, "hackread.com"

        if first_article:
            title = await first_article.inner_text()
            link = await first_article.get_attribute("href")

            # Normalize relative links
            if link and link.startswith("/"):
                link = f"https://hackread.com{link}"

        await browser.close()
        return (title, link, source) if title and link else None


async def main():
    db_manager.create_table()

    article_info = await scrape_latest_article()
    if not article_info:
        print("⚠️ No new article found.")
        return

    title, link, source = article_info

    if link and not db_manager.is_article_sent(link):
        message = f"Title: {title}\nLink: {link}\nSource: {source}"
        await telegram_bot.send_message(message)  # uses secrets inside TelegramBot
        db_manager.mark_article_as_sent(link)
        print("✅ Sent:", message)
    else:
        print("ℹ️ Article already sent or invalid link.")


if __name__ == "__main__":
    asyncio.run(main())
