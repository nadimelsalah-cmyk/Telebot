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

def scrape_first_article_details():
    # Set up the Chrome driver using WebDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://cybernews.com/"
    
    try:
        driver.get(url)
        
        # Wait for the page to load and for the first article to be clickable
        wait = WebDriverWait(driver, 10)
        
        # Wait for the first article's <h2> tag to be present
        first_article = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cells__item a.link.heading')))
        
        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView();", first_article)
        
        # Click the article
        first_article.click()

        # Wait for the new page to load fully
        time.sleep(2)  # Alternatively, you can use WebDriverWait to wait for specific elements

        # Extract the article title, date, and first paragraph (description)
        title = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1'))).text
        date = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
        article_link = driver.current_url

        # Return the scraped information
        return {
            "Title": title,
            "Date": date,
            "Link": article_link
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
    article_info = scrape_first_article_details()
    if article_info:
        message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: Cybernews"
        link = article_info['Link']
        
        if not is_article_sent(link):
            await send_message_to_telegram_channel(message)
            mark_article_as_sent(link)
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
