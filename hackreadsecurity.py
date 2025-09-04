import asyncio
from playwright.async_api import async_playwright
from main import DatabaseManager, TelegramBot

db_manager = DatabaseManager()
telegram_bot = TelegramBot()

async def scrape_latest_article():
    url = "https://hackread.com/category/security/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        article = await page.query_selector(".cs-entry__inner.cs-entry__content")
        if article:
            title_el = await article.query_selector("h2.cs-entry__title a")
            link_el = await article.query_selector("h2.cs-entry__title a")

            title = await title_el.inner_text() if title_el else "No Title"
            link = await link_el.get_attribute("href") if link_el else None
            source = "hackread.com"

            await browser.close()
            return title, link, source

        await browser.close()
        return None


async def main():
    article_info = await scrape_latest_article()
    if article_info:
        title, link, source = article_info
        if link and not db_manager.is_article_sent(link):
            message = f"📢 *New Article Found!*\n\n*Title:* {title}\n🔗 {link}\n📰 Source: {source}"
            await telegram_bot.send_message(message)
            db_manager.mark_article_as_sent(link)
        else:
            print("Article already sent or invalid link.")
    else:
        print("No new article found.")


if __name__ == "__main__":
    asyncio.run(main())
