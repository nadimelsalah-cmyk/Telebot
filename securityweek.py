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
from main import create_table, is_article_sent, mark_article_as_sent  # Import your database functions

# Telegram bot configuration
bot_token = '8041558734:AAGkbIaBHTzKLaQoDgtuiCInnwCX7y2wImo'  # Replace with your bot token
bot_chat_id = '-1002166281411'  # Replace with your chat ID
bot = telegram.Bot(token=bot_token)

async def send_message_to_telegram_channel(message):
    await bot.send_message(chat_id=bot_chat_id, text=message)

def scrape_latest_cybersecurity_news():
    # Set up the Chrome driver using WebDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://www.securityweek.com/"
    
    try:
        driver.get(url)
        
        # Wait until the first article under "Latest Cybersecurity News" is loaded
        wait = WebDriverWait(driver, 10)
        
        # Locate the first article link under the "Latest Cybersecurity News" section
        first_article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.zox-art-title a')))
        
        # Extract article details
        title = first_article_link.text
        link = first_article_link.get_attribute('href')
        
        # Click the article link to navigate to the full article page
        first_article_link.click()

        # Wait for the article page to load fully
        time.sleep(2)
        
        # Try to extract the date of the article from the page
        try:
            article_date = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'time'))).text
        except TimeoutException:
            article_date = "Date not available"
        
        # Return the formatted information
        return {
            "Title": title,
            "Link": link,
            "Date": article_date
        }

    except Exception as e:
        print(f"Error scraping the article: {e}")
        return None
    
    finally:
        driver.quit()  # Ensure the browser is closed

async def main():
    create_table()  # Create table in the database if it doesn't exist
    article_info = scrape_latest_cybersecurity_news()  # Scrape the article
    
    if article_info:
        message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: SecurityWeek"
        link = article_info['Link']
        
        if not is_article_sent(link):  # Check if the article has already been sent
            await send_message_to_telegram_channel(message)  # Send message to Telegram
            mark_article_as_sent(link)  # Mark the article as sent in the database
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
