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
bot_token = '8041558734:AAGkbIaBHTzKLaQoDgtuiCInnwCX7y2wImo' 
bot_chat_id = '-1002166281411' 
bot = telegram.Bot(token=bot_token)

async def send_message_to_telegram_channel(message):
    await bot.send_message(chat_id=bot_chat_id, text=message)

def scrape_latest_cybersecurity_news():
    # Set up the Chrome driver using WebDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://www.csoonline.com/"
    
    try:
        driver.get(url)
        
        # Wait until the first article under "Latest Cybersecurity News" is loaded
        wait = WebDriverWait(driver, 10)
        
        # Locate the first article link under the "Latest Cybersecurity News" section
        first_article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.latest-content__card-secondary a.card')))
        
        # Extract article details
        title = first_article_link.find_element(By.CSS_SELECTOR, 'h4.card__title').text
        link = first_article_link.get_attribute('href')
        
        # Extract the source and date
        source = first_article_link.find_element(By.CSS_SELECTOR, 'div.card__info span').text
        date = first_article_link.find_element(By.CSS_SELECTOR, 'div.card__info--light span').text
        # Return the formatted information
        return {
            "Title": title,
            "Link": link,
            "Source": source,
            "Date": date
        }

    except Exception as e:
        print(f"Error scraping the article: {e}")
        return None
    
    finally:
        driver.quit()  # Ensure the browser is closed

async def main():
    create_table() 
    article_info = scrape_latest_cybersecurity_news()  # Scrape the article
    
    if article_info:
        message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nSource: {article_info['Source']}\nDate: {article_info['Date']}"
        link = article_info['Link']
        
        if not is_article_sent(link):  # Check if the article has already been sent
            await send_message_to_telegram_channel(message)  # Send message to Telegram
            mark_article_as_sent(link)  # Mark the article as sent in the database
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
