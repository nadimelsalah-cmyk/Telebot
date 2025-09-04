import time
import asyncio
import telegram
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from test import create_table, is_article_sent, mark_article_as_sent  # Import your database functions

# Telegram bot configuration
bot_token = '8041558734:AAGkbIaBHTzKLaQoDgtuiCInnwCX7y2wImo'  # Replace with your bot token
bot_chat_id = '-1002166281411'  # Replace with your chat ID
bot = telegram.Bot(token=bot_token)

async def send_message_to_telegram_channel(message):
    await bot.send_message(chat_id=bot_chat_id, text=message)

def scrape_first_article():
    # Set up the Chrome driver using WebDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://www.helpnetsecurity.com/"
    
    try:
        driver.get(url)
        
        # Wait until the first article in the "Cybersecurity news" section is loaded
        wait = WebDriverWait(driver, 10)
        
        # Get the first article's title and link
        first_article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.card-body a.d-block')))
        title = first_article_link.get_attribute('title')
        link = first_article_link.get_attribute('href')

        # Get the date of the first article
        article_date = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.card-body time')))
        date = article_date.text  # Get the visible date text
        
        # Return the formatted information
        return {
            "Title": title,
            "Link": link,
            "Date": date
        }

    except TimeoutException:
        print("Timeout waiting for page elements.")
        return None

    except Exception as e:
        print(f"Error scraping the article: {e}")
        return None
    
    finally:
        driver.quit()  # Ensure the browser is closed

async def main():
    create_table()  # Create table in the database if it doesn't exist
    article_info = scrape_first_article()  # Scrape the article
    
    if article_info:
        message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: HelpNetSecurity"
        link = article_info['Link']
        
        if not is_article_sent(link):  # Check if the article has already been sent
            await send_message_to_telegram_channel(message)  # Send message to Telegram
            mark_article_as_sent(link)  # Mark the article as sent in the database
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
