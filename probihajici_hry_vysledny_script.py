#funguje, rychlé
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time

# Your login details
login_url = 'https://cs.boardgamearena.com/account'  # URL of the login page
target_url = 'https://boardgamearena.com/playertables?player=93282695'  # URL of the target page after logging in
email = 'tvuj_email'
password = 'tve_heslo'

# Path to the WebDriver executable (ensure you have downloaded and installed the appropriate WebDriver for your browser)
driver_path = '/home/pavlina/Stažené/chromedriver-linux64/chromedriver-linux64/chromedriver'  # Replace with the actual path

# Initialize Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--window-size=1920x1080")  # Set the window size
chrome_options.add_argument("--headless")  # Run in headless mode

# Initialize the WebDriver service
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("Opening the login page...")
    driver.get(login_url)

    print("Entering login credentials...")
    email_field = driver.find_element(By.NAME, 'email')  # Adjust if necessary
    password_field = driver.find_element(By.NAME, 'password')  # Adjust if necessary

    email_field.send_keys(email)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    print("Waiting for the login process to complete...")
    try:
        WebDriverWait(driver, 20).until(EC.url_changes(login_url))
        print("Login successful.")
    except TimeoutException:
        print("Login process took too long. Exiting...")
        driver.quit()
        exit()

    print("Opening a new tab...")
    driver.execute_script("window.open('');")
    
    print("Switching to the new tab...")
    driver.switch_to.window(driver.window_handles[1])
    
    print("Navigating to the target page...")
    driver.get(target_url)

    print("Waiting for the target page to load...")
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        print("Target page loaded successfully.")
    except TimeoutException:
        print("Loading the target page took too long. Exiting...")
        driver.quit()
        exit()

    print("Handling cookie consent banner if present...")
    try:
        cookie_consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="dialog"] .cc-dismiss'))
        )
        cookie_consent_button.click()
        print("Cookie consent banner closed.")
    except (TimeoutException, NoSuchElementException):
        print("No cookie consent banner found or failed to close it.")
    
    # Wait for a specific key element
    print("Waiting for specific elements to ensure complete page load...")
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.specific-element-class')))  # Adjust the selector to fit your needs
        print("Specific elements loaded.")
    except TimeoutException:
        print("Specific elements did not load in time.")

    # Scroll in increments
    print("Scrolling through the page to trigger lazy loading...")
    scroll_pause_time = 1
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Save the source code of the target page
    page_source = driver.page_source
    with open("/home/pavlina/Dokumenty/IT/scraping_bga/240609_vsechny_hry/probihajici_hry/target_page_source.txt", "w", encoding='utf-8') as file:
        file.write(page_source)
    print("Source code saved successfully to target_page_source.txt")

finally:
    # Close the WebDriver
    driver.quit()
    print("WebDriver closed.")

###########################################################################################
from bs4 import BeautifulSoup
import pandas as pd
pd.set_option("display.max_colwidth",1000)

# Load the HTML content from the provided file
#with open('probihajici_zdroj.txt', 'r', encoding='utf-8') as file:
with open('/home/pavlina/Dokumenty/IT/scraping_bga/240609_vsechny_hry/probihajici_hry/target_page_source.txt', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Define the sections to look for
sections = ['section-play', 'section-arena', 'section-tournament']

# Dictionary to store game names, progression, and URLs for each section
games_info = {section: {'game_names': [], 'progression': [], 'urls': []} for section in sections}

# Extract game names, progression, and URLs for each section
for section in sections:
    section_div = soup.find('div', {'id': section})
    if section_div:
        game_elements = section_div.find_all('div', {'class': 'bga-table-list-item__game-name bga-link text-lg font-bold truncate svelte-1yag60g'})
        #game_elements = section_div.find_all('div', {'class': 'py-4 relative'})
        for game_element in game_elements:
            game_name = game_element.get_text(strip=True)
            
            # Find the progression percentage for the game
            progression_element = game_element.find_next('div', {'class': 'text-bga-gray-78 text-lg leading-none truncate'})
            if progression_element:
                progression_span = progression_element.find('span', {'class': 'font-bold'})
                progression = progression_span.get_text(strip=True) if progression_span else 'N/A'
            else:
                progression = 'N/A'
            
            # Find the URL for the game
            background_element = game_element.find_previous('div', {'class': 'bga-table-list-item__background z-0 svelte-1yag60g'})
            if background_element:
                url_element = background_element.find('a', {'class': 'absolute inset-0 block'})
                url = f"https:{url_element['href']}" if url_element else 'N/A'
            else:
                url = 'N/A'
            
            games_info[section]['game_names'].append(game_name)
            games_info[section]['progression'].append(progression)
            games_info[section]['urls'].append(url)

# Convert the dictionary to a DataFrame for display
games_df = pd.concat(
    {
        section: pd.DataFrame(data)
        for section, data in games_info.items()
    }, axis=1
)

# Separate the play and arena sections
games_df_play = games_df[[(      'section-play',  'game_names'), (      'section-play', 'progression'), (      'section-play',        'urls')]].dropna()
games_df_play.columns = ['game_names', 'progression', 'urls']
games_df_play['section'] = 'play'

games_df_arena = games_df[[(     'section-arena',  'game_names'), (     'section-arena', 'progression'), (     'section-arena',        'urls')]].dropna()
games_df_arena.columns = ['game_names', 'progression', 'urls']
games_df_arena['section'] = 'arena'

games_df_tournament = games_df[[(     'section-tournament',  'game_names'), (     'section-tournament', 'progression'), (     'section-tournament',        'urls')]].dropna()
games_df_tournament.columns = ['game_names', 'progression', 'urls']
games_df_tournament['section'] = 'tournament'

# Concatenate the DataFrames
games_df_combined = pd.concat([games_df_play, games_df_arena, games_df_tournament], ignore_index=True)

# Arrange the columns
games_df_combined = games_df_combined[['game_names', 'progression', 'urls', 'section']]

# Display the result
print(games_df_combined)
###################################################################################################
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import time
import os
import pandas as pd

# Your login details
login_url = 'https://cs.boardgamearena.com/account'  # URL of the login page
email = 'tvuj_email'
password = 'tve_heslo'

# Path to the WebDriver executable
driver_path = '/home/pavlina/Stažené/chromedriver-linux64/chromedriver-linux64/chromedriver'  # Replace with the actual path

# Initialize Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--window-size=1920x1080")  # Set the window size
chrome_options.add_argument("--headless")  # Run in headless mode

# Function to login
def login_to_site(driver):
    driver.get(login_url)
    email_field = driver.find_element(By.NAME, 'email')
    password_field = driver.find_element(By.NAME, 'password')
    email_field.send_keys(email)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    WebDriverWait(driver, 20).until(EC.url_changes(login_url))

# Function to handle URL loading with retries
def load_url_with_retries(driver, url, retries=3, timeout=30):
    for attempt in range(retries):
        try:
            driver.get(url)
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            return True
        except (TimeoutException, WebDriverException) as e:
            print(f"Attempt {attempt + 1} failed for URL {url}: {e}")
            time.sleep(5)  # Wait a bit before retrying
    return False

# Function to capture screenshot
def capture_screenshot(driver, filename):
    screenshot_path = os.path.join(os.getcwd(), filename)
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

# Initialize the WebDriver service
service = Service(executable_path=driver_path)

players_vse = []

try:
    # Initialize WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    login_to_site(driver)

    for i, url in enumerate(games_df_combined.urls):
        print(f"Opening a new tab for URL {i}...")
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])

        if i == 3:
            print(f"Handling problematic URL at index {i}: {url}")

        if load_url_with_retries(driver, url):
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract information
            players = []
            try:
                for tag in soup.find_all('a', href=True):
                    player_id = tag['href'].split('=')[-1]
                    player_name = tag.text
                    score_tag = soup.find('span', {'id': f'player_score_{player_id}'})
                    if score_tag:
                        player_score = score_tag.text
                        players.append(f"{player_name}: {player_score}")

                players_vse.append(players)
            except Exception as e:
                print(f"Error extracting information from URL {i}: {url} - {e}")
                players_vse.append("problém")
        else:
            print(f"Failed to load URL {i} after multiple attempts: {url}")
            capture_screenshot(driver, f"error_screenshot_{i}.png")
            players_vse.append("problém")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

finally:
    driver.quit()
    print("WebDriver closed.")

ddf = pd.DataFrame({"urls": games_df_combined.urls, "players": players_vse})
print(ddf)
#################################################################################
vysl = games_df_combined.merge(ddf, on = "urls", how = "left")
vysl.to_csv("/home/pavlina/Dokumenty/IT/scraping_bga/240609_vsechny_hry/probihajici_f.csv")
