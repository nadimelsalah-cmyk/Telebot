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

def scrape_security_boulevard_article():
    # Set up the Chrome driver using WebDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://securityboulevard.com/security-creators-network/"
    
    try:
        driver.get(url)
        
        # Wait for the first article under "Latest Posts" to load
        wait = WebDriverWait(driver, 15)
        
        # Locate the first article link and extract title and link
        first_article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pt-cv-title a.panel-title')))
        title = first_article_link.text.split("\n")[0]  # Extract only the title text
        link = first_article_link.get_attribute('href')

        # Extract the article's publication date
        article_date_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.entry-date time')))
        date = article_date_element.get_attribute('datetime')

        # Return the extracted information
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
    create_table()
    article_info = scrape_security_boulevard_article()
    if article_info:
        message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: Security Boulevard"
        link = article_info['Link']
        
        if not is_article_sent(link):
            await send_message_to_telegram_channel(message)
            mark_article_as_sent(link)
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
