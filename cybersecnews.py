import asyncio
from playwright.async_api import async_playwright
from main import DatabaseManager  # Use your existing DB manager

db_manager = DatabaseManager()


async def scrape_latest_article():
    """Scrape the latest article from CybersecurityNews."""
    url = "https://cybersecuritynews.com/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set headers to look like a real browser
        await page.goto(url, wait_until="domcontentloaded")

        # Select the first article (from your provided HTML)
        first_article = await page.query_selector("div.td_module_flex h3.entry-title a")

        if first_article:
            title = await first_article.inner_text()
            link = await first_article.get_attribute("href")

            source = "cybersecuritynews.com"

            await browser.close()
            return title, link, source

        await browser.close()
        return None


async def main():
    db_manager.create_table()

    article_info = await scrape_latest_article()
    if article_info:
        title, link, source = article_info

        if link and not db_manager.is_article_sent(link):
            message = f"Title: {title}\nLink: {link}\nSource: {source}"
            print("New article found:\n", message)
            db_manager.mark_article_as_sent(link)
        else:
            print("Article already sent or invalid link.")
    else:
        print("No new article found.")


if __name__ == "__main__":
    asyncio.run(main())
