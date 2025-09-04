import requests
from bs4 import BeautifulSoup
import asyncio
from main import DatabaseManager, TelegramBot  # Import your classes

db_manager = DatabaseManager()
telegram_bot = TelegramBot()

def scrape_latest_article():
    """Scrape the latest news article from BleepingComputer."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get("https://www.bleepingcomputer.com/", headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        tab = soup.find('div', id='nlatest')
        if tab:
            article_li = tab.find('li')
            if article_li:
                link_tag = article_li.find('a', href=True)
                title_tag = link_tag.find('p') if link_tag else None

                link = link_tag['href'] if link_tag else None
                title = title_tag.text.strip() if title_tag else "No Title"
                source = "bleepingcomputer.com"

                return title, link, source

        print("No article found.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

async def main():
    db_manager.create_table()

    article_info = scrape_latest_article()
    if article_info:
        title, link, source = article_info

        if not db_manager.is_article_sent(link):
            message = f"Title: {title}\nLink: {link}\nSource: {source}"
            await telegram_bot.send_message(message)
            db_manager.mark_article_as_sent(link)
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
